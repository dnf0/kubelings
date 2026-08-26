from unittest.mock import MagicMock, patch

from kubelings.cluster import EPHEMERAL_NAMESPACE_PATTERN, ClusterDetector


def test_cluster_detector_safe_fallback_no_cluster():
    with patch(
        "kubernetes.config.list_kube_config_contexts",
        side_effect=Exception("No kubeconfig"),
    ):
        detector = ClusterDetector()
        status = detector.get_cluster_status()
        assert status["available"] is False
        assert status["context"] == "none"
        assert status["provider"] == "none"
        assert detector.is_cluster_available() is False
        assert detector.get_active_context() is None
        assert detector.last_error == "No kubeconfig"


def test_cluster_detector_local_provider():
    mock_contexts = ([{"name": "kind-kubelings-cluster"}], {"name": "kind-kubelings-cluster"})
    with patch("kubernetes.config.list_kube_config_contexts", return_value=mock_contexts):
        detector = ClusterDetector()
        status = detector.get_cluster_status()
        assert status["available"] is True
        assert status["context"] == "kind-kubelings-cluster"
        assert status["provider"] == "local"
        assert detector.is_cluster_available() is True
        assert detector.get_active_context() == "kind-kubelings-cluster"


def test_cluster_detector_minikube_and_k3d_providers():
    for ctx_name in ["minikube", "k3d-k8s-cluster", "docker-desktop", "orbstack"]:
        mock_contexts = ([{"name": ctx_name}], {"name": ctx_name})
        with patch("kubernetes.config.list_kube_config_contexts", return_value=mock_contexts):
            detector = ClusterDetector()
            status = detector.get_cluster_status()
            assert status["available"] is True
            assert status["provider"] == "local"


def test_cluster_detector_cloud_provider():
    mock_contexts = (
        [{"name": "gke_my-project_us-central1_prod"}],
        {"name": "gke_my-project_us-central1_prod"},
    )
    with patch("kubernetes.config.list_kube_config_contexts", return_value=mock_contexts):
        detector = ClusterDetector()
        status = detector.get_cluster_status()
        assert status["available"] is True
        assert status["context"] == "gke_my-project_us-central1_prod"
        assert status["provider"] == "cloud"


def test_cluster_detector_ephemeral_namespace_lifecycle():
    mock_contexts = ([{"name": "kind-test"}], {"name": "kind-test"})
    with (
        patch("kubernetes.config.list_kube_config_contexts", return_value=mock_contexts),
        patch("kubernetes.config.load_kube_config"),
        patch("kubernetes.client.CoreV1Api") as mock_core_api_class,
    ):
        mock_api_instance = MagicMock()
        mock_core_api_class.return_value = mock_api_instance

        detector = ClusterDetector()
        ns_name = detector.create_ephemeral_namespace(prefix="kubelings-test")
        assert ns_name is not None
        assert ns_name.startswith("kubelings-test-")
        assert ns_name in detector.created_namespaces
        assert mock_api_instance.create_namespace.called

        # Verify created namespace labels
        call_kwargs = mock_api_instance.create_namespace.call_args.kwargs
        assert "_request_timeout" in call_kwargs
        created_body = call_kwargs["body"]
        assert created_body.metadata.labels["kubelings.dev/ephemeral"] == "true"
        assert created_body.metadata.labels["app.kubernetes.io/managed-by"] == "kubelings"

        # Cleanup namespace
        cleanup_success = detector.cleanup_namespace(ns_name)
        assert cleanup_success is True
        assert mock_api_instance.delete_namespace.called
        assert mock_api_instance.delete_namespace.call_args.kwargs["name"] == ns_name
        assert ns_name not in detector.created_namespaces


def test_cluster_detector_custom_prefix_roundtrip():
    mock_contexts = ([{"name": "kind-test"}], {"name": "kind-test"})
    with (
        patch("kubernetes.config.list_kube_config_contexts", return_value=mock_contexts),
        patch("kubernetes.config.load_kube_config"),
        patch("kubernetes.client.CoreV1Api") as mock_core_api_class,
    ):
        mock_api_instance = MagicMock()
        mock_core_api_class.return_value = mock_api_instance

        detector = ClusterDetector()
        # Custom prefix without "kubelings-" prefix should be prefixed and DNS-1123 sanitized
        ns_name = detector.create_ephemeral_namespace(prefix="exercise-01")
        assert ns_name is not None
        assert ns_name.startswith("kubelings-exercise-01-")

        # Complex prefix with spaces/capitals/symbols
        ns_name_dirty = detector.create_ephemeral_namespace(prefix="My Test_NS!!")
        assert ns_name_dirty is not None
        assert ns_name_dirty.startswith("kubelings-my-test-ns-")

        # Prefix "kubelings" or "kubelings-" should not double-prefix
        ns_name_base = detector.create_ephemeral_namespace(prefix="kubelings")
        assert ns_name_base is not None
        assert ns_name_base.startswith("kubelings-test-")

        ns_name_dash = detector.create_ephemeral_namespace(prefix="kubelings-")
        assert ns_name_dash is not None
        assert ns_name_dash.startswith("kubelings-test-")

        ns_name_separators = detector.create_ephemeral_namespace(prefix="---")
        assert ns_name_separators is not None
        assert ns_name_separators.startswith("kubelings-test-")

        # prefix=None handling
        ns_name_none = detector.create_ephemeral_namespace(prefix=None)
        assert ns_name_none is not None
        assert ns_name_none.startswith("kubelings-test-")

        # Long prefix truncation (under 63 chars DNS-1123 max length)
        ns_name_long = detector.create_ephemeral_namespace(
            prefix="a-very-long-custom-exercise-prefix-that-exceeds-normal-length-limits-easily"
        )
        assert ns_name_long is not None
        assert len(ns_name_long) <= 63
        assert EPHEMERAL_NAMESPACE_PATTERN.fullmatch(ns_name_long)

        # All created namespaces should clean up properly
        for name in [
            ns_name,
            ns_name_dirty,
            ns_name_base,
            ns_name_dash,
            ns_name_separators,
            ns_name_none,
            ns_name_long,
        ]:
            assert detector.cleanup_namespace(name) is True


def test_cluster_detector_cleanup_untracked_namespace_label_check():
    mock_contexts = ([{"name": "kind-test"}], {"name": "kind-test"})
    with (
        patch("kubernetes.config.list_kube_config_contexts", return_value=mock_contexts),
        patch("kubernetes.config.load_kube_config"),
        patch("kubernetes.client.CoreV1Api") as mock_core_api_class,
    ):
        mock_api_instance = MagicMock()
        mock_core_api_class.return_value = mock_api_instance

        detector = ClusterDetector()

        # Target namespace with valid ephemeral label
        mock_valid_ns = MagicMock()
        mock_valid_ns.metadata.labels = {"kubelings.dev/ephemeral": "true"}
        mock_api_instance.read_namespace.return_value = mock_valid_ns

        assert detector.cleanup_namespace("kubelings-exercise-01-abcdef12") is True
        assert mock_api_instance.delete_namespace.called

        # Target namespace missing ephemeral label
        mock_invalid_ns = MagicMock()
        mock_invalid_ns.metadata.labels = {"app": "custom-prod"}
        mock_api_instance.read_namespace.return_value = mock_invalid_ns

        assert detector.cleanup_namespace("kubelings-prod-data-12345678") is False
        assert "missing 'kubelings.dev/ephemeral=true' label" in (detector.last_error or "")


def test_cluster_detector_cleanup_guard_against_non_ephemeral_namespaces():
    mock_contexts = ([{"name": "kind-test"}], {"name": "kind-test"})
    with (
        patch("kubernetes.config.list_kube_config_contexts", return_value=mock_contexts),
        patch("kubernetes.config.load_kube_config"),
        patch("kubernetes.client.CoreV1Api") as mock_core_api_class,
    ):
        mock_api_instance = MagicMock()
        mock_core_api_class.return_value = mock_api_instance

        detector = ClusterDetector()
        # Refuse to delete system or default namespaces
        assert detector.cleanup_namespace("default") is False
        assert "Refusing to delete" in (detector.last_error or "")
        assert detector.cleanup_namespace("kube-system") is False
        assert detector.cleanup_namespace("") is False
        assert detector.last_error == "Namespace name cannot be empty."
        assert detector.cleanup_namespace("kubelings-test-abc\n") is False
        assert not mock_api_instance.delete_namespace.called


def test_cluster_detector_ephemeral_namespace_failure_when_no_cluster():
    with patch("kubernetes.config.list_kube_config_contexts", side_effect=Exception("No cluster")):
        detector = ClusterDetector()
        ns_name = detector.create_ephemeral_namespace()
        assert ns_name is None
        assert detector.last_error == "No active Kubernetes cluster available."
        cleanup_success = detector.cleanup_namespace("kubelings-test-12345678")
        assert cleanup_success is False
        assert detector.last_error == "No active Kubernetes cluster available."


def test_cluster_detector_api_exception_handling_and_recovery():
    mock_contexts = ([{"name": "kind-test"}], {"name": "kind-test"})
    with (
        patch("kubernetes.config.list_kube_config_contexts", return_value=mock_contexts),
        patch("kubernetes.config.load_kube_config"),
        patch("kubernetes.client.CoreV1Api") as mock_core_api_class,
    ):
        mock_api_instance = MagicMock()
        mock_api_instance.create_namespace.side_effect = Exception("API Error")
        mock_api_instance.delete_namespace.side_effect = Exception("API Error")
        mock_core_api_class.return_value = mock_api_instance

        detector = ClusterDetector()
        ns_name = detector.create_ephemeral_namespace()
        assert ns_name is None
        assert detector.last_error == "API Error"
        assert detector.cleanup_namespace("kubelings-test-12345678") is False

        # Reset mock for successful operation and assert last_error is cleared
        mock_api_instance.create_namespace.side_effect = None
        mock_api_instance.delete_namespace.side_effect = None
        created = detector.create_ephemeral_namespace()
        assert created is not None
        assert detector.last_error is None


def test_cluster_detector_status_caching_and_refresh():
    mock_contexts_1 = ([{"name": "kind-first"}], {"name": "kind-first"})
    mock_contexts_2 = ([{"name": "kind-second"}], {"name": "kind-second"})

    with patch("kubernetes.config.list_kube_config_contexts", return_value=mock_contexts_1):
        detector = ClusterDetector()
        status1 = detector.get_cluster_status()
        assert status1["context"] == "kind-first"

    with patch("kubernetes.config.list_kube_config_contexts", return_value=mock_contexts_2):
        # Without refresh, should return cached status
        status_cached = detector.get_cluster_status()
        assert status_cached["context"] == "kind-first"

        # With refresh, should query again
        status_refreshed = detector.get_cluster_status(refresh=True)
        assert status_refreshed["context"] == "kind-second"

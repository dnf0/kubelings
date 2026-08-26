from unittest.mock import MagicMock, patch
from kubelings.cluster import ClusterDetector


def test_cluster_detector_safe_fallback_no_cluster():
    with patch("kubernetes.config.list_kube_config_contexts", side_effect=Exception("No kubeconfig")):
        detector = ClusterDetector()
        status = detector.get_cluster_status()
        assert status["available"] is False
        assert status["context"] == "none"
        assert status["provider"] == "none"
        assert detector.is_cluster_available() is False
        assert detector.get_active_context() is None


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
    with patch("kubernetes.config.list_kube_config_contexts", return_value=mock_contexts), \
         patch("kubernetes.config.load_kube_config"), \
         patch("kubernetes.client.CoreV1Api") as mock_core_api_class:
        
        mock_api_instance = MagicMock()
        mock_core_api_class.return_value = mock_api_instance

        detector = ClusterDetector()
        ns_name = detector.create_ephemeral_namespace(prefix="kubelings-test")
        assert ns_name is not None
        assert ns_name.startswith("kubelings-test-")
        assert mock_api_instance.create_namespace.called

        # Cleanup namespace
        cleanup_success = detector.cleanup_namespace(ns_name)
        assert cleanup_success is True
        assert mock_api_instance.delete_namespace.called


def test_cluster_detector_ephemeral_namespace_failure_when_no_cluster():
    with patch("kubernetes.config.list_kube_config_contexts", side_effect=Exception("No cluster")):
        detector = ClusterDetector()
        ns_name = detector.create_ephemeral_namespace()
        assert ns_name is None
        cleanup_success = detector.cleanup_namespace("any-namespace")
        assert cleanup_success is False


def test_cluster_detector_api_exception_handling():
    mock_contexts = ([{"name": "kind-test"}], {"name": "kind-test"})
    with patch("kubernetes.config.list_kube_config_contexts", return_value=mock_contexts), \
         patch("kubernetes.config.load_kube_config"), \
         patch("kubernetes.client.CoreV1Api") as mock_core_api_class:
        
        mock_api_instance = MagicMock()
        mock_api_instance.create_namespace.side_effect = Exception("API Error")
        mock_api_instance.delete_namespace.side_effect = Exception("API Error")
        mock_core_api_class.return_value = mock_api_instance

        detector = ClusterDetector()
        ns_name = detector.create_ephemeral_namespace()
        assert ns_name is None
        assert detector.cleanup_namespace("kubelings-test-123") is False


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

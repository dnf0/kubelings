from typing import Any, cast

import pytest
from kubernetes import client, config

from kubelings.cluster import ClusterDetector


def _has_live_cluster() -> bool:
    detector = ClusterDetector()
    return detector.is_cluster_available()


@pytest.mark.skipif(not _has_live_cluster(), reason="Requires an active Kubernetes cluster")
def test_live_cluster_ephemeral_lifecycle():
    detector = ClusterDetector()
    assert detector.is_cluster_available()

    status = detector.get_cluster_status()
    assert status["available"] is True
    assert status["context"] != "none"

    # Create ephemeral namespace
    ns = detector.create_ephemeral_namespace(prefix="ci-e2e-test")
    assert ns is not None
    assert ns.startswith("kubelings-ci-e2e-test-")
    assert ns in detector.created_namespaces

    # Verify namespace exists via client
    config.load_kube_config()
    v1 = client.CoreV1Api()
    ns_obj = cast(Any, v1.read_namespace(name=ns))
    assert ns_obj.metadata is not None
    assert ns_obj.metadata.name == ns
    assert ns_obj.metadata.labels.get("kubelings.dev/ephemeral") == "true"

    # Cleanup namespace
    cleaned = detector.cleanup_namespace(ns)
    assert cleaned is True
    assert ns not in detector.created_namespaces

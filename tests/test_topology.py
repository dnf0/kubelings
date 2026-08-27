"""Tests for Kubernetes Resource Topology Visualizer."""

from rich.tree import Tree
from kubelings.topology import build_resource_topology, render_topology_tree


def test_pod_service_topology():
    manifests = [
        {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {"name": "web-svc", "namespace": "default"},
            "spec": {
                "selector": {"app": "web"},
                "ports": [{"port": 80, "targetPort": 8080}],
            },
        },
        {
            "apiVersion": "v1",
            "kind": "Pod",
            "metadata": {"name": "web-pod-1", "namespace": "default", "labels": {"app": "web"}},
            "spec": {"containers": [{"name": "app", "image": "nginx:alpine"}]},
        },
    ]
    tree = build_resource_topology(manifests)
    assert isinstance(tree, Tree)
    assert "Topology" in str(tree.label)


def test_workload_storage_topology():
    manifests = [
        {
            "apiVersion": "apps/v1",
            "kind": "StatefulSet",
            "metadata": {"name": "db-cluster", "namespace": "production"},
            "spec": {
                "replicas": 3,
                "template": {
                    "spec": {
                        "containers": [{"name": "postgres", "image": "postgres:16"}],
                        "volumes": [
                            {
                                "name": "data",
                                "persistentVolumeClaim": {"claimName": "db-pvc"},
                            }
                        ],
                    }
                },
            },
        },
        {
            "apiVersion": "v1",
            "kind": "PersistentVolumeClaim",
            "metadata": {"name": "db-pvc", "namespace": "production"},
            "spec": {
                "accessModes": ["ReadWriteOnce"],
                "storageClassName": "fast-ssd",
                "resources": {"requests": {"storage": "50Gi"}},
            },
        },
    ]
    tree = build_resource_topology(manifests)
    assert isinstance(tree, Tree)


def test_network_policy_topology():
    manifests = [
        {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "NetworkPolicy",
            "metadata": {"name": "isolate-backend", "namespace": "default"},
            "spec": {
                "podSelector": {"matchLabels": {"role": "backend"}},
                "policyTypes": ["Ingress", "Egress"],
            },
        },
        {
            "apiVersion": "v1",
            "kind": "Pod",
            "metadata": {
                "name": "api-backend",
                "namespace": "default",
                "labels": {"role": "backend"},
            },
            "spec": {"containers": [{"name": "api", "image": "api:v1"}]},
        },
    ]
    tree = build_resource_topology(manifests)
    assert isinstance(tree, Tree)

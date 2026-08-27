"""
Solution: Hubble Observability & OpenTelemetry Tracing (mesh04)
"""

from typing import Any, Dict


def get_observable_pod_manifest() -> Dict[str, Any]:
    return {
        "apiVersion": "v1",
        "kind": "Pod",
        "metadata": {
            "name": "order-service",
            "annotations": {
                "sidecar.istio.io/inject": "false",
                "prometheus.io/scrape": "true",
                "prometheus.io/port": "9090",
                "telemetry.cilium.io/trace": "b3",
            },
        },
        "spec": {
            "containers": [
                {
                    "name": "order-api",
                    "image": "orders:v1.0",
                    "ports": [{"containerPort": 9090}],
                }
            ]
        },
    }


def verify() -> None:
    manifest = get_observable_pod_manifest()
    assert manifest, "Manifest cannot be empty"
    assert manifest.get("apiVersion") == "v1"
    assert manifest.get("kind") == "Pod"

    meta = manifest.get("metadata", {})
    assert meta.get("name") == "order-service"
    annotations = meta.get("annotations", {})
    assert annotations.get("prometheus.io/scrape") == "true"
    assert annotations.get("prometheus.io/port") == "9090"
    assert annotations.get("telemetry.cilium.io/trace") == "b3"

    spec = manifest.get("spec", {})
    containers = spec.get("containers", [])
    assert len(containers) == 1
    assert containers[0].get("ports", [{}])[0].get("containerPort") == 9090

    print("✓ Service Mesh Hubble & OpenTelemetry Observability validated successfully!")


if __name__ == "__main__":
    verify()

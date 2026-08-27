"""
Exercise: Hubble Observability & OpenTelemetry Tracing (mesh04)

Cilium Hubble provides deep network, service, and security visibility for Kubernetes.
Pod annotations allow Hubble and OpenTelemetry to collect distributed traces and metrics.

Task:
Complete `get_observable_pod_manifest()` returning a Pod manifest configured for mesh observability:
1. apiVersion: "v1"
2. kind: "Pod"
3. metadata:
   - name: "order-service"
   - annotations:
     - "sidecar.istio.io/inject": "false" # Using eBPF ambient mesh
     - "prometheus.io/scrape": "true"
     - "prometheus.io/port": "9090"
     - "telemetry.cilium.io/trace": "b3"
4. spec:
   - containers:
     - name: "order-api"
     - image: "orders:v1.0"
     - ports:
       - containerPort: 9090
"""

from typing import Any, Dict


def get_observable_pod_manifest() -> Dict[str, Any]:
    # TODO: Define and return the observable Pod manifest dictionary
    return {}


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

"""
Exercise: solutions/05_services_networking/net01.py
Topic: ClusterIP Services & Port Mapping

Reference Solution
"""

from typing import Any, Dict, Optional
import yaml
from kubelings.validator import validate_manifest

SERVICE_MANIFEST = """
apiVersion: v1
kind: Service
metadata:
  name: backend-service
spec:
  type: ClusterIP
  selector:
    app: backend
    tier: api
  ports:
  - name: http
    protocol: TCP
    port: 80
    targetPort: 8080
"""


def resolve_endpoint_target(
    service_manifest: Dict[str, Any], pod_manifest: Dict[str, Any]
) -> Optional[int]:
    """Check if a pod matches the service selector and return the targetPort."""
    selector = service_manifest.get("spec", {}).get("selector", {})
    if not selector:
        return None
    pod_labels = pod_manifest.get("metadata", {}).get("labels", {})
    for k, v in selector.items():
        if pod_labels.get(k) != v:
            return None
    ports = service_manifest.get("spec", {}).get("ports", [])
    if ports:
        return ports[0].get("targetPort", ports[0].get("port"))
    return None


def verify():
    manifest = yaml.safe_load(SERVICE_MANIFEST)
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(manifest, expected_kind="Service", expected_api_version="v1")

    assert manifest["metadata"]["name"] == "backend-service"
    assert manifest["spec"]["type"] == "ClusterIP"
    assert manifest["spec"]["selector"] == {"app": "backend", "tier": "api"}

    ports = manifest["spec"]["ports"]
    assert len(ports) == 1
    assert ports[0]["name"] == "http"
    assert ports[0]["protocol"] == "TCP"
    assert ports[0]["port"] == 80
    assert ports[0]["targetPort"] == 8080

    matching_pod = {
        "metadata": {
            "name": "backend-pod-1",
            "labels": {"app": "backend", "tier": "api", "version": "v1.2"},
        }
    }
    non_matching_pod = {
        "metadata": {"name": "frontend-pod-1", "labels": {"app": "frontend", "tier": "ui"}}
    }

    assert resolve_endpoint_target(manifest, matching_pod) == 8080
    assert resolve_endpoint_target(manifest, non_matching_pod) is None

    print("✓ net01 passed!")


if __name__ == "__main__":
    verify()

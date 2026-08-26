"""
Exercise: solutions/06_ingress_gateway/ingress01.py
Topic: Ingress Host & Path Routing

Reference Solution
"""

from typing import Any, Dict, Optional

import yaml

from kubelings.validator import validate_manifest

INGRESS_MANIFEST = """
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: api-gateway-ingress
spec:
  ingressClassName: nginx
  rules:
  - host: api.example.com
    http:
      paths:
      - path: /v1
        pathType: Prefix
        backend:
          service:
            name: api-v1-service
            port:
              number: 80
      - path: /v2
        pathType: Prefix
        backend:
          service:
            name: api-v2-service
            port:
              number: 80
  - host: admin.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: admin-portal-service
            port:
              number: 8080
"""


def route_ingress_request(ingress_manifest: Dict[str, Any], host: str, path: str) -> Optional[str]:
    """Find the destination backend service for a given incoming host and request path."""
    rules = ingress_manifest.get("spec", {}).get("rules", [])
    matching_services = []

    for r in rules:
        if r.get("host") == host:
            paths = r.get("http", {}).get("paths", [])
            for p in paths:
                prefix = p.get("path", "")
                if path.startswith(prefix):
                    matching_services.append(
                        (len(prefix), p.get("backend", {}).get("service", {}).get("name"))
                    )

    if not matching_services:
        return None

    # Pick the longest prefix match
    matching_services.sort(key=lambda x: x[0], reverse=True)
    return matching_services[0][1]


def verify():
    manifest = yaml.safe_load(INGRESS_MANIFEST)
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(
        manifest, expected_kind="Ingress", expected_api_version="networking.k8s.io/v1"
    )

    assert manifest["metadata"]["name"] == "api-gateway-ingress"
    assert manifest["spec"]["ingressClassName"] == "nginx"

    rules = manifest["spec"]["rules"]
    assert len(rules) == 2

    # Verify routing simulator
    assert route_ingress_request(manifest, "api.example.com", "/v1/users") == "api-v1-service"
    assert route_ingress_request(manifest, "api.example.com", "/v2/products") == "api-v2-service"
    assert (
        route_ingress_request(manifest, "admin.example.com", "/dashboard") == "admin-portal-service"
    )
    assert route_ingress_request(manifest, "unknown.example.com", "/") is None

    print("✓ ingress01 passed!")


if __name__ == "__main__":
    verify()

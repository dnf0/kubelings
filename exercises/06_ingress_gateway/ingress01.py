"""
Exercise: exercises/06_ingress_gateway/ingress01.py
Topic: Ingress Host & Path Routing

Context & Why:
While NodePort and LoadBalancer services operate primarily at Layer 4 (TCP/UDP transport layer),
`Ingress` objects manage Layer 7 application routing (HTTP and HTTPS). An Ingress Controller
(such as NGINX, Traefik, HAProxy, or AWS ALB Controller) inspects HTTP request headers, hostnames,
and URI paths to multiplex traffic from a single public entrypoint to dozens of internal microservices.
Specifying `ingressClassName: nginx` dictates which ingress controller implementation reconciles the rule.
Path matching types (`Prefix` vs `Exact`) define how URI paths are evaluated, allowing path-based
API versioning (`/v1` vs `/v2`) and multi-host virtual hosting (`api.example.com` vs `admin.example.com`).

Instructions:
Kubernetes Ingress manages external HTTP/HTTPS routing into internal Services.
Paths can be matched using `pathType: Prefix` or `pathType: Exact`.

1. Complete the Ingress manifest:
   - name: 'api-gateway-ingress'
   - ingressClassName: 'nginx'
   - rule 1 (host 'api.example.com'):
     - path '/v1' (Prefix) -> service 'api-v1-service', port number 80
     - path '/v2' (Prefix) -> service 'api-v2-service', port number 80
   - rule 2 (host 'admin.example.com'):
     - path '/' (Prefix) -> service 'admin-portal-service', port number 8080
2. Implement `route_ingress_request(ingress_manifest, host, path)`:
   - Evaluates host and path matches against rules, returning the matching backend service name.
   - Longest matching prefix wins when multiple paths match. Return None if no match.
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
  # TODO: Set ingressClassName to 'nginx'
  # WHY: IngressClass specifies which in-cluster controller (e.g. ingress-nginx) is responsible for provisioning the routing table.
  ingressClassName: ???
  rules:
  - host: api.example.com
    http:
      paths:
      - path: /v1
        # TODO: Set pathType to 'Prefix' and backend service to 'api-v1-service' on port 80
        # WHY: Prefix matching routes all subpaths starting with /v1 to the v1 backend service.
        pathType: ???
        backend:
          service:
            name: ???
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
            # TODO: Route host admin.example.com to 'admin-portal-service' on port 8080
            # WHY: Host-based routing separates traffic for administrative subdomains to internal management services.
            name: ???
            port:
              number: 0
"""


def route_ingress_request(ingress_manifest: Dict[str, Any], host: str, path: str) -> Optional[str]:
    """Find the destination backend service for a given incoming host and request path."""
    # TODO: Implement ingress path routing logic matching host and longest prefix path
    # WHY: Simulates the Layer 7 reverse proxy routing evaluation performed by ingress controllers like NGINX.
    return None


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

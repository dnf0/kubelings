"""
Exercise: exercises/06_ingress_gateway/ingress03.py
Topic: Ingress Annotations & Rewrites

Instructions:
Ingress controllers support custom behavior via annotations.
A common requirement is URI path rewriting (e.g., stripping the `/payments` prefix
before forwarding the request to the upstream microservice).

1. Configure the Ingress annotations:
   - `nginx.ingress.kubernetes.io/rewrite-target`: '/$2'
   - `nginx.ingress.kubernetes.io/ssl-redirect`: 'true'
   - `nginx.ingress.kubernetes.io/proxy-body-size`: '50m'
2. Complete rule in Ingress:
   - host: 'api.company.com'
   - path: '/payments(/|$)(.*)' with `pathType: ImplementationSpecific`
   - service: 'payments-service', port: 8080
3. Implement `apply_rewrite_rule(path_regex, rewrite_template, request_path)`:
   - Uses regex to rewrite matching request URIs.
   - Example: pattern `^/payments(/|$)(.*)` with rewrite `/$2` converts `/payments/v1/charge` to `/v1/charge`.
"""

# I AM NOT DONE

import re  # noqa: F401
from typing import Optional
import yaml
from kubelings.validator import validate_manifest

INGRESS_MANIFEST = """
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: rewrite-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: ???
    nginx.ingress.kubernetes.io/ssl-redirect: ???
    nginx.ingress.kubernetes.io/proxy-body-size: ???
spec:
  ingressClassName: nginx
  rules:
  - host: api.company.com
    http:
      paths:
      - path: ???
        pathType: ImplementationSpecific
        backend:
          service:
            name: payments-service
            port:
              number: 8080
"""


def apply_rewrite_rule(path_regex: str, rewrite_template: str, request_path: str) -> Optional[str]:
    """Simulate nginx rewrite-target behavior for a request path."""
    # TODO: Implement URL rewrite simulation
    return None


def verify():
    manifest = yaml.safe_load(INGRESS_MANIFEST)
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(manifest, expected_kind="Ingress", expected_api_version="networking.k8s.io/v1")

    ann = manifest["metadata"]["annotations"]
    assert ann.get("nginx.ingress.kubernetes.io/rewrite-target") == "/$2"
    assert ann.get("nginx.ingress.kubernetes.io/ssl-redirect") == "true"
    assert ann.get("nginx.ingress.kubernetes.io/proxy-body-size") == "50m"

    rule_path = manifest["spec"]["rules"][0]["http"]["paths"][0]
    assert rule_path["path"] == "/payments(/|$)(.*)"
    assert rule_path["pathType"] == "ImplementationSpecific"
    assert rule_path["backend"]["service"]["name"] == "payments-service"

    # Test rewrite simulator
    pattern = r"^/payments(/|$)(.*)"
    assert apply_rewrite_rule(pattern, r"/\2", "/payments/v1/charge") == "/v1/charge"
    assert apply_rewrite_rule(pattern, r"/\2", "/payments") == "/"
    assert apply_rewrite_rule(pattern, r"/\2", "/other/path") is None

    print("✓ ingress03 passed!")


if __name__ == "__main__":
    verify()

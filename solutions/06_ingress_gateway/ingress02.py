"""
Exercise: solutions/06_ingress_gateway/ingress02.py
Topic: Ingress TLS Termination

Reference Solution
"""

from typing import Any, Dict

import yaml

from kubelings.validator import validate_manifests

MANIFESTS = """
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: secure-ingress
spec:
  tls:
  - hosts:
    - secure.example.com
    - api.secure.example.com
    secretName: wildcard-tls-secret
  rules:
  - host: secure.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: secure-web-service
            port:
              number: 443
---
apiVersion: v1
kind: Secret
metadata:
  name: wildcard-tls-secret
type: kubernetes.io/tls
data:
  tls.crt: LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCg==
  tls.key: LS0tLS1CRUdJTiBQUklWQVRFIEtFWS0tLS0tCg==
"""


def verify_ingress_tls_coverage(ingress: Dict[str, Any], secret: Dict[str, Any]) -> bool:
    """Verify that all Ingress hosts are securely covered by the TLS configuration."""
    if secret.get("type") != "kubernetes.io/tls":
        return False

    secret_data = secret.get("data", {})
    if "tls.crt" not in secret_data or "tls.key" not in secret_data:
        return False

    tls_configs = ingress.get("spec", {}).get("tls", [])
    covered_hosts = set()
    secret_matched = False

    for item in tls_configs:
        if item.get("secretName") == secret.get("metadata", {}).get("name"):
            secret_matched = True
            for h in item.get("hosts", []):
                covered_hosts.add(h)

    if not secret_matched:
        return False

    rules = ingress.get("spec", {}).get("rules", [])
    for r in rules:
        host = r.get("host")
        if host and host not in covered_hosts:
            return False

    return True


def verify():
    manifests = list(yaml.safe_load_all(MANIFESTS))
    assert len(manifests) == 2, "Must define 2 manifests (Ingress and TLS Secret)"
    validate_manifests(manifests, expected_kinds=["Ingress", "Secret"])

    ing, sec = manifests[0], manifests[1]

    assert ing["metadata"]["name"] == "secure-ingress"
    tls_entry = ing["spec"]["tls"][0]
    assert "secure.example.com" in tls_entry["hosts"]
    assert "api.secure.example.com" in tls_entry["hosts"]
    assert tls_entry["secretName"] == "wildcard-tls-secret"

    assert sec["metadata"]["name"] == "wildcard-tls-secret"
    assert sec["type"] == "kubernetes.io/tls"
    assert "tls.crt" in sec["data"]
    assert "tls.key" in sec["data"]

    assert verify_ingress_tls_coverage(ing, sec) is True

    # Test uncovered host
    bad_ing = yaml.safe_load(yaml.dump(ing))
    bad_ing["spec"]["rules"].append(
        {
            "host": "unprotected.example.com",
            "http": {
                "paths": [
                    {
                        "path": "/",
                        "pathType": "Prefix",
                        "backend": {"service": {"name": "app", "port": {"number": 80}}},
                    }
                ]
            },
        }
    )
    assert verify_ingress_tls_coverage(bad_ing, sec) is False, (
        "Should fail when rule host not listed in tls.hosts"
    )

    print("✓ ingress02 passed!")


if __name__ == "__main__":
    verify()

"""
Exercise: exercises/06_ingress_gateway/ingress02.py
Topic: Ingress TLS Termination

Instructions:
To terminate TLS/HTTPS at the Ingress controller:
1. Define a Kubernetes Secret of type `kubernetes.io/tls` containing base64-encoded `tls.crt` and `tls.key`.
2. Reference the secret name in the Ingress manifest under `spec.tls`.

1. Complete the Ingress manifest:
   - name: 'secure-ingress'
   - spec.tls: hosts ['secure.example.com', 'api.secure.example.com'], secretName 'wildcard-tls-secret'
2. Complete the TLS Secret manifest:
   - name: 'wildcard-tls-secret'
   - type: 'kubernetes.io/tls'
   - data keys: 'tls.crt' and 'tls.key'
3. Implement `verify_ingress_tls_coverage(ingress, secret)`:
   - Verifies Secret type is 'kubernetes.io/tls' with valid keys.
   - Verifies all rule hosts in Ingress are listed in `spec.tls[].hosts` and secretName matches.
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
    - ???
    - ???
    secretName: ???
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
type: ???
data:
  tls.crt: LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCg==
  tls.key: LS0tLS1CRUdJTiBQUklWQVRFIEtFWS0tLS0tCg==
"""


def verify_ingress_tls_coverage(ingress: Dict[str, Any], secret: Dict[str, Any]) -> bool:
    """Verify that all Ingress hosts are securely covered by the TLS configuration."""
    # TODO: Implement TLS coverage validation
    return False


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

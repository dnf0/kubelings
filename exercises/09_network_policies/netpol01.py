"""
Exercise: exercises/09_network_policies/netpol01.py
Topic: Default Deny Network Policy

Instructions:
By default, Kubernetes pods accept network traffic from any source and can connect
to any destination. To establish a secure zero-trust networking baseline, a Default Deny
NetworkPolicy isolates all pods in a namespace, blocking all ingress and egress traffic
until explicit allow rules are defined.

1. Define a NetworkPolicy 'default-deny-all' in namespace 'production':
   - apiVersion: 'networking.k8s.io/v1'
   - kind: 'NetworkPolicy'
   - spec.podSelector: {} (selects all pods in the namespace)
   - spec.policyTypes: ['Ingress', 'Egress']
   - Do not specify any ingress or egress rules (empty/omitted).
"""

# I AM NOT DONE

import yaml

from kubelings.validator import validate_manifest

POLICY_MANIFEST = """
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: production
spec:
  podSelector: ???
  policyTypes:
  - ???
  - ???
"""


def verify():
    manifest = yaml.safe_load(POLICY_MANIFEST)
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(
        manifest, expected_kind="NetworkPolicy", expected_api_version="networking.k8s.io/v1"
    )

    assert manifest["metadata"]["name"] == "default-deny-all"
    assert manifest["metadata"]["namespace"] == "production"

    spec = manifest.get("spec", {})
    assert spec.get("podSelector") == {}, (
        "podSelector must be an empty dict {} to match all pods in namespace"
    )
    assert set(spec.get("policyTypes", [])) == {"Ingress", "Egress"}, (
        "policyTypes must include both 'Ingress' and 'Egress'"
    )
    assert "ingress" not in spec or len(spec.get("ingress", [])) == 0, (
        "Default deny must not define allow ingress rules"
    )
    assert "egress" not in spec or len(spec.get("egress", [])) == 0, (
        "Default deny must not define allow egress rules"
    )

    print("✓ netpol01 passed!")


if __name__ == "__main__":
    verify()

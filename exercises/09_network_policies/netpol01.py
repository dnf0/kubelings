"""
Exercise: exercises/09_network_policies/netpol01.py
Topic: Default Deny Network Policy

Context & Why:
Kubernetes implements a flat, open network model by default: any pod in any namespace can
communicate with any other pod without restriction. To establish a defense-in-depth Zero Trust
architecture, production clusters implement a "Default Deny" posture. A NetworkPolicy with an
empty `podSelector: {}` targets all pods in the namespace, and declaring `policyTypes: [Ingress, Egress]`
without specifying allow rules immediately blocks all non-whitelisted inbound and outbound traffic.
This forces development teams to explicitly document and declare legitimate microservice traffic paths.

Instructions:
1. Define a NetworkPolicy 'default-deny-all' in namespace 'production':
   - apiVersion: 'networking.k8s.io/v1'
   - kind: 'NetworkPolicy'
   - spec.podSelector: {} (selects all pods in the namespace)
   - spec.policyTypes: ['Ingress', 'Egress']
   - Do not specify any ingress or egress rules (empty/omitted).
"""

import yaml

from kubelings.validator import validate_manifest

POLICY_MANIFEST = """
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: production
spec:
  # TODO: Select all pods in the namespace using an empty mapping ({}).
  # WHY: An empty podSelector matches 100% of the pods in the target namespace.
  podSelector: ???
  # TODO: Declare both 'Ingress' and 'Egress' policy types.
  # WHY: Instructs the CNI network plugin to enforce filtering in both directions, defaulting to drop unless allowed.
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

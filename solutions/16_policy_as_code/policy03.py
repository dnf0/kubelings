"""
Chapter 16: Policy as Code with Kyverno & Gatekeeper
Exercise 16.3: Kyverno Generate Policy for Default Deny NetworkPolicy (Solution)
"""

from typing import Any, Dict

import yaml


def get_kyverno_generate_manifest() -> Dict[str, Any]:
    manifest_yaml = """
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: generate-default-deny
spec:
  rules:
  - name: generate-deny-all
    match:
      any:
      - resources:
          kinds:
          - Namespace
    generate:
      apiVersion: networking.k8s.io/v1
      kind: NetworkPolicy
      name: default-deny-all
      namespace: "{{request.object.metadata.name}}"
      synchronize: true
      data:
        spec:
          podSelector: {}
          policyTypes:
          - Ingress
          - Egress
"""
    return yaml.safe_load(manifest_yaml)


if __name__ == "__main__":
    policy = get_kyverno_generate_manifest()
    assert policy.get("kind") == "ClusterPolicy"
    rules = policy.get("spec", {}).get("rules", [])
    assert len(rules) == 1
    gen = rules[0].get("generate", {})
    assert gen.get("kind") == "NetworkPolicy"
    assert gen.get("synchronize") is True
    print("✓ Kyverno generate policy validation passed!")

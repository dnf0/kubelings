# I AM NOT DONE
"""
Chapter 16: Policy as Code with Kyverno & Gatekeeper
Exercise 16.2: Kyverno Mutating Policy for Security Context Defaults

Fix the Kyverno Mutating Policy manifest to automatically inject
securityContext.runAsNonRoot: true into any Pod that omits it.
"""

from typing import Any, Dict
import yaml


def get_kyverno_mutation_manifest() -> Dict[str, Any]:
    manifest_yaml = """
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: mutate-pod-security
spec:
  rules:
  - name: inject-run-as-non-root
    match:
      any:
      - resources:
          kinds:
          - Pod
    mutate:
      patchStrategicMerge:
        spec:
          +(securityContext):
            runAsNonRoot: true
"""
    # Fix the return dictionary
    return {}


if __name__ == "__main__":
    policy = get_kyverno_mutation_manifest()
    assert policy.get("kind") == "ClusterPolicy"
    rules = policy.get("spec", {}).get("rules", [])
    assert len(rules) == 1
    mutate = rules[0].get("mutate", {})
    assert "patchStrategicMerge" in mutate
    print("✓ Kyverno mutation policy validation passed!")

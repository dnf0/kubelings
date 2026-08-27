# I AM NOT DONE
"""
Chapter 16: Policy as Code with Kyverno & Gatekeeper
Exercise 16.1: Kyverno ClusterPolicy for Required Labels

Fix the Kyverno ClusterPolicy manifest to enforce that all Pods
in the cluster have the 'app.kubernetes.io/name' and 'team' labels.
"""

from typing import Any, Dict

import yaml


def get_kyverno_policy_manifest() -> Dict[str, Any]:
    manifest_yaml = """
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: require-labels
spec:
  validationFailureAction: Enforce
  background: true
  rules:
  - name: check-team-and-app-labels
    match:
      any:
      - resources:
          kinds:
          - Pod
    validate:
      message: "Label 'app.kubernetes.io/name' and 'team' are required."
      pattern:
        metadata:
          labels:
            app.kubernetes.io/name: "?*"
            team: "?*"
"""
    # Fix the return dictionary
    return {}


if __name__ == "__main__":
    policy = get_kyverno_policy_manifest()
    assert policy.get("kind") == "ClusterPolicy"
    assert policy.get("apiVersion") == "kyverno.io/v1"
    rules = policy.get("spec", {}).get("rules", [])
    assert len(rules) == 1
    assert "app.kubernetes.io/name" in rules[0]["validate"]["pattern"]["metadata"]["labels"]
    print("✓ Kyverno policy validation passed!")

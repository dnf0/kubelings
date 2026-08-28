"""
Chapter 16: Policy as Code with Kyverno & Gatekeeper
Exercise 16.1: Kyverno ClusterPolicy for Required Labels

Context & Why:
In enterprise Kubernetes clusters, consistent resource labeling is essential for cost
allocation, telemetry aggregation, security audit trails, and automated routing. Relying
on manual code reviews or developer discipline inevitably leads to missing metadata and
orphaned workloads.

Kyverno provides a Kubernetes-native Policy-as-Code engine that validates resources
using standard YAML patterns rather than proprietary programming languages. Setting
`validationFailureAction: Enforce` instructs the dynamic admission webhook to synchronously
block non-compliant Pod creation requests at the API boundary, returning a descriptive
error message to the user.

Task:
Fix the Kyverno ClusterPolicy manifest function to return the parsed manifest dictionary
enforcing that all Pods in the cluster have 'app.kubernetes.io/name' and 'team' labels.
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
    # TODO: Parse and return the Kyverno ClusterPolicy manifest dictionary (e.g., using yaml.safe_load).
    # WHY: Declarative validation policies enforce organizational compliance and metadata standards
    #      at admission time before non-compliant resources enter cluster state.
    return {}


if __name__ == "__main__":
    policy = get_kyverno_policy_manifest()
    assert policy.get("kind") == "ClusterPolicy"
    assert policy.get("apiVersion") == "kyverno.io/v1"
    rules = policy.get("spec", {}).get("rules", [])
    assert len(rules) == 1
    assert "app.kubernetes.io/name" in rules[0]["validate"]["pattern"]["metadata"]["labels"]
    print("✓ Kyverno policy validation passed!")

"""
Chapter 16: Policy as Code with Kyverno & Gatekeeper
Exercise 16.3: Kyverno Generate Policy for Default Deny NetworkPolicy

Context & Why:
In Kubernetes multi-tenancy, newly created namespaces have no network isolation by default.
Pods in a newly created namespace can communicate with any pod in the cluster, and receive
traffic from anywhere. Relying on manual provisioning of security baselines creates a dangerous
window of exposure before security manifests are applied.

Kyverno `generate` rules enable automatic resource provisioning in response to cluster lifecycle
events. When a new `Namespace` is created, Kyverno dynamically generates a baseline `NetworkPolicy`
with `podSelector: {}` and `policyTypes: [Ingress, Egress]` inside that namespace. The `synchronize: true`
directive guarantees ongoing reconciliation: if a tenant user accidentally deletes or tampers with the
generated NetworkPolicy, Kyverno immediately recreates or restores it, ensuring continuous zero-trust
network posture.

Task:
Fix the Kyverno Generate Policy manifest function to return the parsed manifest dictionary
that provisions a synchronized default-deny NetworkPolicy upon Namespace creation.
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
    # TODO: Parse and return the Kyverno Generate ClusterPolicy manifest dictionary (e.g., using yaml.safe_load).
    # WHY: Generate rules automate Day-2 multi-tenancy by stamping out critical baseline resources (such as
    #      zero-trust default-deny NetworkPolicies) instantly and continuously synchronizing their state.
    return {}


if __name__ == "__main__":
    policy = get_kyverno_generate_manifest()
    assert policy.get("kind") == "ClusterPolicy"
    rules = policy.get("spec", {}).get("rules", [])
    assert len(rules) == 1
    gen = rules[0].get("generate", {})
    assert gen.get("kind") == "NetworkPolicy"
    assert gen.get("synchronize") is True
    print("✓ Kyverno generate policy validation passed!")

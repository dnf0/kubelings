"""
Chapter 16: Policy as Code with Kyverno & Gatekeeper
Exercise 16.2: Kyverno Mutating Policy for Security Context Defaults

Context & Why:
Container security baselines (such as CIS Kubernetes Benchmark and Pod Security Standards)
mandate that containers should run as non-root users (`securityContext.runAsNonRoot: true`)
to minimize the blast radius of container escapes. However, expecting developers to manually
declare security contexts on every workload creates friction and frequent validation rejections.

Kyverno mutating policies solve this friction by mutating incoming requests before they are
persisted to etcd. Using `patchStrategicMerge` with conditional syntax (`+(securityContext): ...`),
Kyverno automatically injects safe default security settings only when the workload author has
omitted them. This delivers a "secure by default" platform experience without blocking developer
deployments.

Task:
Fix the Kyverno Mutating Policy manifest function to return the parsed manifest dictionary
that automatically injects `securityContext.runAsNonRoot: true` into Pods that omit it.
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
    # TODO: Parse and return the Kyverno Mutating ClusterPolicy manifest dictionary (e.g., using yaml.safe_load).
    # WHY: Mutating admission policies enforce secure-by-default standards by automatically injecting mandatory
    #      security configurations into workload specs without developer friction.
    return {}


if __name__ == "__main__":
    policy = get_kyverno_mutation_manifest()
    assert policy.get("kind") == "ClusterPolicy"
    rules = policy.get("spec", {}).get("rules", [])
    assert len(rules) == 1
    mutate = rules[0].get("mutate", {})
    assert "patchStrategicMerge" in mutate
    print("✓ Kyverno mutation policy validation passed!")

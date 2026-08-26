"""
Exercise: exercises/13_troubleshooting/troubleshoot04.py
Topic: ResourceQuotas & LimitRanges

Instructions:
Kubernetes multi-tenancy relies on two complementary resource governance primitives:
1. `ResourceQuota`: Sets aggregate resource limits (CPU, Memory, Pod count) across
   an entire namespace. Exceeding quotas causes the API server to reject creations (403).
2. `LimitRange`: Enforces minimum/maximum constraints and injects default requests
   and limits for containers created in the namespace without explicit definitions.

Define a ResourceQuota and LimitRange for namespace 'team-billing':
1. ResourceQuota 'compute-quota':
   - requests.cpu: "4"
   - requests.memory: "8Gi"
   - limits.cpu: "8"
   - limits.memory: "16Gi"
   - pods: "10"
2. LimitRange 'container-limits':
   - type: Container
   - default: cpu "500m", memory "512Mi"
   - defaultRequest: cpu "200m", memory "256Mi"
   - max: cpu "2", memory "2Gi"
   - min: cpu "100m", memory "128Mi"
"""

# I AM NOT DONE

import yaml

from kubelings.validator import validate_manifests

MANIFESTS = """
apiVersion: v1
kind: ResourceQuota
metadata:
  name: compute-quota
  namespace: team-billing
spec:
  hard:
    requests.cpu: ???
    requests.memory: "8Gi"
    limits.cpu: "8"
    limits.memory: ???
    pods: "10"
---
apiVersion: v1
kind: LimitRange
metadata:
  name: container-limits
  namespace: team-billing
spec:
  limits:
  - type: Container
    default:
      cpu: ???
      memory: "512Mi"
    defaultRequest:
      cpu: "200m"
      memory: ???
    max:
      cpu: "2"
      memory: "2Gi"
    min:
      cpu: "100m"
      memory: "128Mi"
"""


def verify():
    manifests = list(yaml.safe_load_all(MANIFESTS))
    assert len(manifests) == 2, "Must contain exactly 2 manifests (ResourceQuota and LimitRange)"
    validate_manifests(manifests, expected_kinds=["ResourceQuota", "LimitRange"])

    quota, limit_range = manifests[0], manifests[1]

    # Verify ResourceQuota
    assert quota["metadata"]["name"] == "compute-quota"
    assert quota["metadata"]["namespace"] == "team-billing"
    hard = quota.get("spec", {}).get("hard", {})
    assert hard.get("requests.cpu") == "4"
    assert hard.get("requests.memory") == "8Gi"
    assert hard.get("limits.cpu") == "8"
    assert hard.get("limits.memory") == "16Gi"
    assert hard.get("pods") == "10"

    # Verify LimitRange
    assert limit_range["metadata"]["name"] == "container-limits"
    assert limit_range["metadata"]["namespace"] == "team-billing"
    limits = limit_range.get("spec", {}).get("limits", [])
    assert len(limits) == 1
    c_limit = limits[0]
    assert c_limit.get("type") == "Container"
    assert c_limit.get("default") == {"cpu": "500m", "memory": "512Mi"}
    assert c_limit.get("defaultRequest") == {"cpu": "200m", "memory": "256Mi"}
    assert c_limit.get("max") == {"cpu": "2", "memory": "2Gi"}
    assert c_limit.get("min") == {"cpu": "100m", "memory": "128Mi"}

    print("✓ troubleshoot04 passed!")


if __name__ == "__main__":
    verify()

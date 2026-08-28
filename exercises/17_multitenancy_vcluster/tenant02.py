"""
Chapter 17: Multi-Tenancy, Virtual Clusters & HNC
Exercise 17.2: Tenant ResourceQuota and LimitRange Multi-Document Manifest

Context & Why:
In shared multi-tenant clusters, an unconstrained workload can cause "noisy neighbor"
problems by consuming all available node memory, leading to out-of-memory (OOM) kills of
neighboring tenant pods. Kubernetes provides two complementary primitives to guarantee fair
resource sharing and cluster stability: `ResourceQuota` and `LimitRange`.

A `ResourceQuota` sets aggregate ceilings on the total CPU, memory, and Pod count that a tenant
namespace can consume across all its workloads. A `LimitRange` complements this by enforcing
per-container constraints—specifically injecting default requests/limits for containers that
omit them. Without a LimitRange injecting default requests, a ResourceQuota that tracks requests
would reject any pod manifest lacking explicit resource declarations.

Task:
Fix the function `get_tenant_isolation_manifests()` to parse and return the multi-document YAML
manifest containing both the ResourceQuota and LimitRange dictionaries for namespace 'tenant-b'.
"""

from typing import Any, Dict, List

import yaml


def get_tenant_isolation_manifests() -> List[Dict[str, Any]]:
    manifest_yaml = """
apiVersion: v1
kind: ResourceQuota
metadata:
  name: tenant-b-quota
  namespace: tenant-b
spec:
  hard:
    requests.cpu: "4"
    requests.memory: 8Gi
    limits.cpu: "8"
    limits.memory: 16Gi
    pods: "10"
---
apiVersion: v1
kind: LimitRange
metadata:
  name: tenant-b-limits
  namespace: tenant-b
spec:
  limits:
  - default:
      cpu: 500m
      memory: 512Mi
    defaultRequest:
      cpu: 100m
      memory: 128Mi
    type: Container
"""
    # TODO: Parse and return the list of manifest dictionaries containing both ResourceQuota and LimitRange
    #       (e.g., using list(yaml.safe_load_all(manifest_yaml))).
    # WHY: ResourceQuotas and LimitRanges work in tandem to establish namespace-wide resource budgets and
    #      container-level defaults, preventing noisy neighbors from starving shared node capacity.
    return []


if __name__ == "__main__":
    docs = get_tenant_isolation_manifests()
    assert len(docs) == 2
    kinds = {d.get("kind") for d in docs}
    assert kinds == {"ResourceQuota", "LimitRange"}
    quota = next(d for d in docs if d.get("kind") == "ResourceQuota")
    assert quota["spec"]["hard"]["pods"] == "10"
    print("✓ Tenant quota and limit range validation passed!")

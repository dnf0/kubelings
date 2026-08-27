# I AM NOT DONE
"""
Chapter 17: Multi-Tenancy, Virtual Clusters & HNC
Exercise 17.2: Tenant ResourceQuota and LimitRange Multi-Document Manifest

Fix the multi-document manifest containing both a ResourceQuota and
a LimitRange to enforce strict CPU, memory, and pod count ceilings for tenant-b.
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
    # Fix the return list of documents
    return []


if __name__ == "__main__":
    docs = get_tenant_isolation_manifests()
    assert len(docs) == 2
    kinds = {d.get("kind") for d in docs}
    assert kinds == {"ResourceQuota", "LimitRange"}
    quota = next(d for d in docs if d.get("kind") == "ResourceQuota")
    assert quota["spec"]["hard"]["pods"] == "10"
    print("✓ Tenant quota and limit range validation passed!")

"""
Chapter 17: Multi-Tenancy, Virtual Clusters & HNC
Exercise 17.4: Multi-Tenant Network Isolation Policy (Solution)
"""

from typing import Any, Dict

import yaml


def get_tenant_network_isolation_policy() -> Dict[str, Any]:
    manifest_yaml = """
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: tenant-isolation
  namespace: tenant-secure
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector: {}
  egress:
  - to:
    - podSelector: {}
  - to:
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: kube-system
    ports:
    - protocol: UDP
      port: 53
"""
    return yaml.safe_load(manifest_yaml)


if __name__ == "__main__":
    policy = get_tenant_network_isolation_policy()
    assert policy.get("kind") == "NetworkPolicy"
    assert policy.get("metadata", {}).get("namespace") == "tenant-secure"
    egress = policy.get("spec", {}).get("egress", [])
    assert len(egress) == 2
    print("✓ Tenant network isolation policy validation passed!")

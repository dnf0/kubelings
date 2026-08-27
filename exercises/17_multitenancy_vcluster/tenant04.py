# I AM NOT DONE
"""
Chapter 17: Multi-Tenancy, Virtual Clusters & HNC
Exercise 17.4: Multi-Tenant Network Isolation Policy

Fix the NetworkPolicy that restricts all pods in namespace 'tenant-secure'
to only communicate with other pods inside 'tenant-secure' and DNS on port 53.
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
    # Fix the return dictionary
    return {}


if __name__ == "__main__":
    policy = get_tenant_network_isolation_policy()
    assert policy.get("kind") == "NetworkPolicy"
    assert policy.get("metadata", {}).get("namespace") == "tenant-secure"
    egress = policy.get("spec", {}).get("egress", [])
    assert len(egress) == 2
    print("✓ Tenant network isolation policy validation passed!")

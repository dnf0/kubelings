"""
Chapter 17: Multi-Tenancy, Virtual Clusters & HNC
Exercise 17.4: Multi-Tenant Network Isolation Policy

Context & Why:
In a multi-tenant Kubernetes cluster, default networking behavior allows unrestricted
cross-namespace communication (the "flat network" model). A compromised pod in one tenant
namespace can scan and attack services hosted in neighboring tenant namespaces unless
strict network segmentation is explicitly configured.

Kubernetes `NetworkPolicy` allows platform operators to enforce tenant micro-segmentation.
A zero-trust multi-tenant isolation policy defines `policyTypes: [Ingress, Egress]`,
allowing ingress and egress exclusively to pods within the same namespace (`podSelector: {}`),
while selectively allowing egress to the cluster DNS service (`kube-system` namespace on UDP port 53).
All other external and cross-tenant network paths are blocked by default.

Task:
Fix the function `get_tenant_network_isolation_policy()` to parse and return the NetworkPolicy
dictionary that enforces intra-namespace traffic boundaries and cluster DNS access for 'tenant-secure'.
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
    # TODO: Parse and return the tenant NetworkPolicy manifest dictionary (e.g., using yaml.safe_load).
    # WHY: Multi-tenant network policies block lateral movement and cross-tenant traffic leaks while ensuring
    #      internal intra-namespace communication and cluster CoreDNS resolution remain functional.
    return {}


if __name__ == "__main__":
    policy = get_tenant_network_isolation_policy()
    assert policy.get("kind") == "NetworkPolicy"
    assert policy.get("metadata", {}).get("namespace") == "tenant-secure"
    egress = policy.get("spec", {}).get("egress", [])
    assert len(egress) == 2
    print("✓ Tenant network isolation policy validation passed!")

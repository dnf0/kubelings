"""
Chapter 17: Multi-Tenancy, Virtual Clusters & HNC
Exercise 17.3: Virtual Cluster (vcluster) Control Plane Manifest

Context & Why:
Traditional namespace-based multi-tenancy provides "soft" isolation. All tenants share the
same Kubernetes API server, CRD registry, RBAC cluster roles, and admission webhooks. A tenant
cannot install their own operators, test different Kubernetes API versions, or have `cluster-admin`
privileges inside their sandbox without risking cluster-wide compromise.

Virtual clusters (`vcluster`) deliver "hard" control-plane multi-tenancy. A `VirtualCluster`
manifest provisions a dedicated, lightweight control plane (e.g. k3s or vanilla k8s) running inside
a host namespace. The vcluster syncer controller synchronizes low-level execution primitives
(Pods, Services, Ingresses) to the underlying host cluster while keeping CRDs, namespaces, and
RBAC completely isolated within the tenant's private virtual control plane.

Task:
Fix the vcluster virtual cluster specification function to return the parsed manifest dictionary
provisioning an isolated virtual control plane with resource syncing in namespace 'team-c'.
"""

from typing import Any, Dict

import yaml


def get_vcluster_manifest() -> Dict[str, Any]:
    manifest_yaml = """
apiVersion: vcluster.loft.sh/v1alpha1
kind: VirtualCluster
metadata:
  name: dev-vcluster
  namespace: team-c
spec:
  distro:
    k3s:
      enabled: true
  sync:
    toHost:
      ingresses:
        enabled: true
      services:
        enabled: true
    fromHost:
      nodes:
        enabled: true
"""
    # TODO: Parse and return the vcluster VirtualCluster manifest dictionary (e.g., using yaml.safe_load).
    # WHY: Virtual clusters decouple tenant control planes from host infrastructure, enabling safe multi-tenancy
    #      with isolated CRD registration, separate API versions, and granular syncer mappings.
    return {}


if __name__ == "__main__":
    vcluster = get_vcluster_manifest()
    assert vcluster.get("kind") == "VirtualCluster"
    assert vcluster.get("apiVersion") == "vcluster.loft.sh/v1alpha1"
    sync = vcluster.get("spec", {}).get("sync", {})
    assert sync.get("toHost", {}).get("services", {}).get("enabled") is True
    print("✓ Virtual cluster validation passed!")

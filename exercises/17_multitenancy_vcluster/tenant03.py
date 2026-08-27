# I AM NOT DONE
"""
Chapter 17: Multi-Tenancy, Virtual Clusters & HNC
Exercise 17.3: Virtual Cluster (vcluster) Control Plane Manifest

Fix the vcluster virtual cluster specification to provision an isolated
virtual control plane running k3s with isolated persistent storage in namespace 'team-c'.
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
    # Fix the return dictionary
    return {}


if __name__ == "__main__":
    vcluster = get_vcluster_manifest()
    assert vcluster.get("kind") == "VirtualCluster"
    assert vcluster.get("apiVersion") == "vcluster.loft.sh/v1alpha1"
    sync = vcluster.get("spec", {}).get("sync", {})
    assert sync.get("toHost", {}).get("services", {}).get("enabled") is True
    print("✓ Virtual cluster validation passed!")

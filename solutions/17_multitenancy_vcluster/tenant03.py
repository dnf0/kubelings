"""
Chapter 17: Multi-Tenancy, Virtual Clusters & HNC
Exercise 17.3: Virtual Cluster (vcluster) Control Plane Manifest (Solution)
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
    return yaml.safe_load(manifest_yaml)


if __name__ == "__main__":
    vcluster = get_vcluster_manifest()
    assert vcluster.get("kind") == "VirtualCluster"
    assert vcluster.get("apiVersion") == "vcluster.loft.sh/v1alpha1"
    sync = vcluster.get("spec", {}).get("sync", {})
    assert sync.get("toHost", {}).get("services", {}).get("enabled") is True
    print("✓ Virtual cluster validation passed!")

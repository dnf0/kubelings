# I AM NOT DONE
"""
Chapter 17: Multi-Tenancy, Virtual Clusters & HNC
Exercise 17.1: Hierarchical Namespace Controller (HNC) Subnamespace Anchor

Fix the HNC SubnamespaceAnchor manifest that declares a child namespace
'team-a-dev' under the parent namespace 'team-a'.
"""

from typing import Any, Dict
import yaml


def get_subnamespace_anchor_manifest() -> Dict[str, Any]:
    manifest_yaml = """
apiVersion: hnc.x-k8s.io/v1alpha2
kind: SubnamespaceAnchor
metadata:
  name: team-a-dev
  namespace: team-a
spec: {}
"""
    # Fix the return dictionary
    return {}


if __name__ == "__main__":
    anchor = get_subnamespace_anchor_manifest()
    assert anchor.get("kind") == "SubnamespaceAnchor"
    assert anchor.get("apiVersion") == "hnc.x-k8s.io/v1alpha2"
    assert anchor.get("metadata", {}).get("name") == "team-a-dev"
    assert anchor.get("metadata", {}).get("namespace") == "team-a"
    print("✓ HNC subnamespace anchor validation passed!")

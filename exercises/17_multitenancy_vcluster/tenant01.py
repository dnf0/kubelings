"""
Chapter 17: Multi-Tenancy, Virtual Clusters & HNC
Exercise 17.1: Hierarchical Namespace Controller (HNC) Subnamespace Anchor

Context & Why:
Standard Kubernetes namespaces are completely flat, lacking organizational structure
(e.g., departments, teams, and sub-environments). Managing RBAC roles, resource quotas,
and network policies across dozens of distinct, flat namespaces forces platform teams to
manually duplicate configurations or build complex synchronization scripts.

The Hierarchical Namespace Controller (HNC) solves this by introducing hierarchical
relationships between namespaces. A `SubnamespaceAnchor` CR allows tenant owners to self-service
child subnamespaces (e.g., `team-a-dev` under parent `team-a`). HNC automatically provisions
the subnamespace and cascades parent policies, RoleBindings, and Secrets down the hierarchy,
enabling scalable soft multi-tenancy with delegated administration.

Task:
Fix the HNC SubnamespaceAnchor manifest function to return the parsed manifest dictionary
declaring a child namespace 'team-a-dev' under parent namespace 'team-a'.
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
    # TODO: Parse and return the HNC SubnamespaceAnchor manifest dictionary (e.g., using yaml.safe_load).
    # WHY: Subnamespace anchors empower tenant teams to self-provision child namespaces while automatically
    #      inheriting compliance, RBAC, and policy guardrails from parent namespaces.
    return {}


if __name__ == "__main__":
    anchor = get_subnamespace_anchor_manifest()
    assert anchor.get("kind") == "SubnamespaceAnchor"
    assert anchor.get("apiVersion") == "hnc.x-k8s.io/v1alpha2"
    assert anchor.get("metadata", {}).get("name") == "team-a-dev"
    assert anchor.get("metadata", {}).get("namespace") == "team-a"
    print("✓ HNC subnamespace anchor validation passed!")

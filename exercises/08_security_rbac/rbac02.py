"""
Exercise: exercises/08_security_rbac/rbac02.py
Topic: Roles & RoleBindings

Context & Why:
Kubernetes Role-Based Access Control (RBAC) enforces namespace-scoped authorization for users,
groups, and ServiceAccounts. A `Role` defines granular access policies through API groups,
resource types, and authorized HTTP verbs (`get`, `list`, `watch`, `create`, `delete`, etc.).
A `RoleBinding` binds those declared permissions to specific subjects within the same namespace.
In multi-tenant clusters, crafting precise, minimal Roles prevents lateral movement and privilege
escalation, ensuring deployer automation and microservice agents only manipulate their designated
workload resources.

Instructions:
1. Define a Role 'pod-manager-role' in namespace 'staging':
   - apiVersion: 'rbac.authorization.k8s.io/v1'
   - rule 1: apiGroups [""], resources ["pods", "pods/log"], verbs ["get", "list", "watch", "create", "delete"]
   - rule 2: apiGroups ["apps"], resources ["deployments"], verbs ["get", "list", "watch"]
2. Define a RoleBinding 'bind-pod-manager' in namespace 'staging':
   - subjects: ServiceAccount 'staging-deployer' in namespace 'staging'
   - roleRef: Role 'pod-manager-role' (apiGroup: 'rbac.authorization.k8s.io')
3. Implement `can_perform_action(rules, api_group, resource, verb)`:
   - Returns True if any rule grants the requested verb on the resource in the given apiGroup (handling '*' wildcards).
"""

from typing import Any, Dict, List

import yaml

from kubelings.validator import validate_manifests

MANIFESTS = """
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: pod-manager-role
  namespace: staging
rules:
- apiGroups: [""]
  resources: ["pods", "pods/log"]
  verbs: ["get", "list", "watch", "create", "delete"]
- apiGroups: ["apps"]
  resources: ["deployments"]
  verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: bind-pod-manager
  namespace: staging
subjects:
- kind: ServiceAccount
  # TODO: Specify the subject ServiceAccount name 'staging-deployer'.
  # WHY: Identifies the workload identity that is granted the role's permissions.
  name: ???
  namespace: staging
roleRef:
  kind: Role
  # TODO: Reference the target Role name 'pod-manager-role'.
  # WHY: Binds the declared rules in pod-manager-role to the staging-deployer subject.
  name: ???
  apiGroup: rbac.authorization.k8s.io
"""


def can_perform_action(
    rules: List[Dict[str, Any]],
    api_group: str,
    resource: str,
    verb: str,
) -> bool:
    """Determine whether the RBAC rules permit the specified action."""
    # TODO: Implement RBAC permission evaluation supporting wildcard ('*') matching for apiGroups, resources, and verbs.
    # WHY: The Kubernetes API server authorization engine evaluates incoming requests by matching against rule list patterns where '*' grants universal access across that dimension.
    return False


def verify():
    manifests = list(yaml.safe_load_all(MANIFESTS))
    assert len(manifests) == 2, "Must contain exactly 2 manifests (Role and RoleBinding)"
    validate_manifests(manifests, expected_kinds=["Role", "RoleBinding"])

    role, binding = manifests[0], manifests[1]

    # Verify Role
    assert role["metadata"]["name"] == "pod-manager-role"
    assert role["metadata"]["namespace"] == "staging"
    assert len(role["rules"]) == 2
    r1, r2 = role["rules"][0], role["rules"][1]
    assert r1["apiGroups"] == [""]
    assert set(r1["resources"]) == {"pods", "pods/log"}
    assert set(r1["verbs"]) == {"get", "list", "watch", "create", "delete"}
    assert r2["apiGroups"] == ["apps"]
    assert r2["resources"] == ["deployments"]
    assert set(r2["verbs"]) == {"get", "list", "watch"}

    # Verify RoleBinding
    assert binding["metadata"]["name"] == "bind-pod-manager"
    assert binding["metadata"]["namespace"] == "staging"
    assert binding["roleRef"]["kind"] == "Role"
    assert binding["roleRef"]["name"] == "pod-manager-role"
    assert binding["roleRef"]["apiGroup"] == "rbac.authorization.k8s.io"

    sub = binding["subjects"][0]
    assert sub["kind"] == "ServiceAccount"
    assert sub["name"] == "staging-deployer"
    assert sub["namespace"] == "staging"

    # Verify rule evaluator logic
    rules = role["rules"]
    assert can_perform_action(rules, "", "pods", "get") is True
    assert can_perform_action(rules, "", "pods", "create") is True
    assert can_perform_action(rules, "", "pods/log", "get") is True
    assert can_perform_action(rules, "apps", "deployments", "list") is True
    assert can_perform_action(rules, "apps", "deployments", "delete") is False, (
        "delete deployments not granted"
    )
    assert can_perform_action(rules, "", "secrets", "get") is False, "secrets not granted"

    # Wildcard test
    wildcard_rules = [{"apiGroups": ["*"], "resources": ["*"], "verbs": ["*"]}]
    assert can_perform_action(wildcard_rules, "custom.io", "widgets", "delete") is True

    print("✓ rbac02 passed!")


if __name__ == "__main__":
    verify()

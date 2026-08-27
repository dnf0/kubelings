"""
Exercise: exercises/08_security_rbac/rbac03.py
Topic: ClusterRoles & ClusterRoleBindings

Instructions:
ClusterRoles define permissions across the entire cluster, covering cluster-scoped
resources (such as nodes and namespaces), resources across all namespaces, or
non-resource URL endpoints (such as /healthz and /metrics).

1. Define a ClusterRole 'cluster-node-viewer':
   - apiVersion: 'rbac.authorization.k8s.io/v1'
   - rule 1: apiGroups [""], resources ["nodes", "nodes/status", "namespaces"], verbs ["get", "list", "watch"]
   - rule 2: nonResourceURLs ["/healthz", "/metrics"], verbs ["get"]
2. Define a ClusterRoleBinding 'bind-node-viewer':
   - subjects: Group 'sre-monitoring-team' (apiGroup: 'rbac.authorization.k8s.io')
   - roleRef: ClusterRole 'cluster-node-viewer' (apiGroup: 'rbac.authorization.k8s.io')
"""

import yaml

from kubelings.validator import validate_manifests

MANIFESTS = """
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: cluster-node-viewer
rules:
- apiGroups: [""]
  resources: ["nodes", "nodes/status", "namespaces"]
  verbs: ["get", "list", "watch"]
- nonResourceURLs: ["/healthz", "/metrics"]
  verbs: ["get"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: bind-node-viewer
subjects:
- kind: Group
  name: ???
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole
  name: ???
  apiGroup: rbac.authorization.k8s.io
"""


def verify():
    manifests = list(yaml.safe_load_all(MANIFESTS))
    assert len(manifests) == 2, (
        "Must contain exactly 2 manifests (ClusterRole and ClusterRoleBinding)"
    )
    validate_manifests(manifests, expected_kinds=["ClusterRole", "ClusterRoleBinding"])

    cr, crb = manifests[0], manifests[1]

    # ClusterRole checks
    assert cr["metadata"]["name"] == "cluster-node-viewer"
    assert "namespace" not in cr["metadata"], "ClusterRole must not define a namespace"
    assert len(cr["rules"]) == 2

    r1, r2 = cr["rules"][0], cr["rules"][1]
    assert r1["apiGroups"] == [""]
    assert set(r1["resources"]) == {"nodes", "nodes/status", "namespaces"}
    assert set(r1["verbs"]) == {"get", "list", "watch"}

    assert set(r2["nonResourceURLs"]) == {"/healthz", "/metrics"}
    assert r2["verbs"] == ["get"]

    # ClusterRoleBinding checks
    assert crb["metadata"]["name"] == "bind-node-viewer"
    assert "namespace" not in crb["metadata"], "ClusterRoleBinding must not define a namespace"
    assert crb["roleRef"]["kind"] == "ClusterRole"
    assert crb["roleRef"]["name"] == "cluster-node-viewer"
    assert crb["roleRef"]["apiGroup"] == "rbac.authorization.k8s.io"

    sub = crb["subjects"][0]
    assert sub["kind"] == "Group"
    assert sub["name"] == "sre-monitoring-team"
    assert sub["apiGroup"] == "rbac.authorization.k8s.io"

    print("✓ rbac03 passed!")


if __name__ == "__main__":
    verify()

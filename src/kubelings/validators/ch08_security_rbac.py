"""
Validators for Chapter 08: Security, RBAC & Service Accounts
"""

from typing import Any, Dict, List

from kubelings.validator import validate_manifest, validate_manifests
from kubelings.validators import register_validator

MANIFESTS = '\napiVersion: v1\nkind: ServiceAccount\nmetadata:\n  name: build-robot-sa\n  namespace: ci-runners\nautomountServiceAccountToken: false\n---\napiVersion: v1\nkind: Pod\nmetadata:\n  name: build-worker-pod\n  namespace: ci-runners\nspec:\n  serviceAccountName: build-robot-sa\n  automountServiceAccountToken: false\n  containers:\n  - name: runner\n    image: alpine:3.19\n    command: ["sh", "-c", "echo Ready && sleep 3600"]\n'


@register_validator("rbac01")
def validate_rbac01(manifest: Any, raw_yaml: str = "") -> None:
    manifests = manifest if isinstance(manifest, list) else [manifest]
    assert len(manifests) == 2, "Must contain exactly 2 manifests (ServiceAccount and Pod)"
    validate_manifests(manifests, expected_kinds=["ServiceAccount", "Pod"])
    sa, pod = (manifests[0], manifests[1])
    assert sa["metadata"]["name"] == "build-robot-sa", (
        "ServiceAccount name must be 'build-robot-sa'"
    )
    assert sa["metadata"]["namespace"] == "ci-runners", (
        "ServiceAccount namespace must be 'ci-runners'"
    )
    assert sa.get("automountServiceAccountToken") is False, (
        "ServiceAccount automountServiceAccountToken must be False"
    )
    assert pod["metadata"]["name"] == "build-worker-pod", "Pod name must be 'build-worker-pod'"
    assert pod["metadata"]["namespace"] == "ci-runners", "Pod namespace must be 'ci-runners'"
    assert pod["spec"].get("serviceAccountName") == "build-robot-sa", (
        "Pod serviceAccountName must be 'build-robot-sa'"
    )
    assert pod["spec"].get("automountServiceAccountToken") is False, (
        "Pod automountServiceAccountToken must be False"
    )
    assert pod["spec"]["containers"][0]["name"] == "runner"
    assert pod["spec"]["containers"][0]["image"] == "alpine:3.19"


def can_perform_action(
    rules: List[Dict[str, Any]], api_group: str, resource: str, verb: str
) -> bool:
    """Determine whether the RBAC rules permit the specified action."""
    for rule in rules:
        groups = rule.get("apiGroups", [])
        resources = rule.get("resources", [])
        verbs = rule.get("verbs", [])
        group_match = "*" in groups or api_group in groups
        resource_match = "*" in resources or resource in resources
        verb_match = "*" in verbs or verb in verbs
        if group_match and resource_match and verb_match:
            return True
    return False


@register_validator("rbac02")
def validate_rbac02(manifest: Any, raw_yaml: str = "") -> None:
    manifests = manifest if isinstance(manifest, list) else [manifest]
    assert len(manifests) == 2, "Must contain exactly 2 manifests (Role and RoleBinding)"
    validate_manifests(manifests, expected_kinds=["Role", "RoleBinding"])
    role, binding = (manifests[0], manifests[1])
    assert role["metadata"]["name"] == "pod-manager-role"
    assert role["metadata"]["namespace"] == "staging"
    assert len(role["rules"]) == 2
    r1, r2 = (role["rules"][0], role["rules"][1])
    assert r1["apiGroups"] == [""]
    assert set(r1["resources"]) == {"pods", "pods/log"}
    assert set(r1["verbs"]) == {"get", "list", "watch", "create", "delete"}
    assert r2["apiGroups"] == ["apps"]
    assert r2["resources"] == ["deployments"]
    assert set(r2["verbs"]) == {"get", "list", "watch"}
    assert binding["metadata"]["name"] == "bind-pod-manager"
    assert binding["metadata"]["namespace"] == "staging"
    assert binding["roleRef"]["kind"] == "Role"
    assert binding["roleRef"]["name"] == "pod-manager-role"
    assert binding["roleRef"]["apiGroup"] == "rbac.authorization.k8s.io"
    sub = binding["subjects"][0]
    assert sub["kind"] == "ServiceAccount"
    assert sub["name"] == "staging-deployer"
    assert sub["namespace"] == "staging"
    rules = role["rules"]
    assert can_perform_action(rules, "", "pods", "get") is True
    assert can_perform_action(rules, "", "pods", "create") is True
    assert can_perform_action(rules, "", "pods/log", "get") is True
    assert can_perform_action(rules, "apps", "deployments", "list") is True
    assert can_perform_action(rules, "apps", "deployments", "delete") is False, (
        "delete deployments not granted"
    )
    assert can_perform_action(rules, "", "secrets", "get") is False, "secrets not granted"
    wildcard_rules = [{"apiGroups": ["*"], "resources": ["*"], "verbs": ["*"]}]
    assert can_perform_action(wildcard_rules, "custom.io", "widgets", "delete") is True


@register_validator("rbac03")
def validate_rbac03(manifest: Any, raw_yaml: str = "") -> None:
    manifests = manifest if isinstance(manifest, list) else [manifest]
    assert len(manifests) == 2, (
        "Must contain exactly 2 manifests (ClusterRole and ClusterRoleBinding)"
    )
    validate_manifests(manifests, expected_kinds=["ClusterRole", "ClusterRoleBinding"])
    cr, crb = (manifests[0], manifests[1])
    assert cr["metadata"]["name"] == "cluster-node-viewer"
    assert "namespace" not in cr["metadata"], "ClusterRole must not define a namespace"
    assert len(cr["rules"]) == 2
    r1, r2 = (cr["rules"][0], cr["rules"][1])
    assert r1["apiGroups"] == [""]
    assert set(r1["resources"]) == {"nodes", "nodes/status", "namespaces"}
    assert set(r1["verbs"]) == {"get", "list", "watch"}
    assert set(r2["nonResourceURLs"]) == {"/healthz", "/metrics"}
    assert r2["verbs"] == ["get"]
    assert crb["metadata"]["name"] == "bind-node-viewer"
    assert "namespace" not in crb["metadata"], "ClusterRoleBinding must not define a namespace"
    assert crb["roleRef"]["kind"] == "ClusterRole"
    assert crb["roleRef"]["name"] == "cluster-node-viewer"
    assert crb["roleRef"]["apiGroup"] == "rbac.authorization.k8s.io"
    sub = crb["subjects"][0]
    assert sub["kind"] == "Group"
    assert sub["name"] == "sre-monitoring-team"
    assert sub["apiGroup"] == "rbac.authorization.k8s.io"


@register_validator("rbac04")
def validate_rbac04(manifest: Any, raw_yaml: str = "") -> None:
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(manifest, expected_kind="Pod", expected_api_version="v1")
    assert manifest["metadata"]["name"] == "secure-app-pod"
    pod_sc = manifest["spec"].get("securityContext", {})
    assert pod_sc.get("runAsNonRoot") is True, "Pod runAsNonRoot must be True"
    assert pod_sc.get("runAsUser") == 10001, "Pod runAsUser must be 10001"
    assert pod_sc.get("runAsGroup") == 10001, "Pod runAsGroup must be 10001"
    assert pod_sc.get("fsGroup") == 20001, "Pod fsGroup must be 20001"
    assert pod_sc.get("seccompProfile", {}).get("type") == "RuntimeDefault", (
        "seccompProfile must be RuntimeDefault"
    )
    container = manifest["spec"]["containers"][0]
    c_sc = container.get("securityContext", {})
    assert c_sc.get("allowPrivilegeEscalation") is False, "allowPrivilegeEscalation must be False"
    assert c_sc.get("readOnlyRootFilesystem") is True, "readOnlyRootFilesystem must be True"
    caps = c_sc.get("capabilities", {})
    assert caps.get("drop") == ["ALL"], "capabilities.drop must contain 'ALL'"
    assert caps.get("add") == ["NET_BIND_SERVICE"], (
        "capabilities.add must contain 'NET_BIND_SERVICE'"
    )


def evaluate_pss_compliance(pod_manifest: Dict[str, Any], level: str) -> bool:
    """Evaluate whether a Pod manifest satisfies the given Pod Security Standard level."""
    if level == "privileged":
        return True
    spec = pod_manifest.get("spec", {})
    if spec.get("hostNetwork") or spec.get("hostPID") or spec.get("hostIPC"):
        return False
    containers = spec.get("containers", [])
    for c in containers:
        c_sc = c.get("securityContext", {})
        if c_sc.get("privileged") is True:
            return False
    if level == "baseline":
        return True
    if level == "restricted":
        pod_sc = spec.get("securityContext", {})
        pod_run_as_non_root = pod_sc.get("runAsNonRoot") is True
        for c in containers:
            c_sc = c.get("securityContext", {})
            if c_sc.get("allowPrivilegeEscalation") is not False:
                return False
            c_run_as_non_root = c_sc.get("runAsNonRoot") is True
            if not (pod_run_as_non_root or c_run_as_non_root):
                return False
            caps = c_sc.get("capabilities", {})
            dropped = caps.get("drop", [])
            if "ALL" not in dropped:
                return False
        return True
    return False


@register_validator("rbac05")
def validate_rbac05(manifest: Any, raw_yaml: str = "") -> None:
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(manifest, expected_kind="Namespace", expected_api_version="v1")
    assert manifest["metadata"]["name"] == "secure-production"
    labels = manifest["metadata"].get("labels", {})
    assert labels.get("pod-security.kubernetes.io/enforce") == "restricted"
    assert labels.get("pod-security.kubernetes.io/enforce-version") == "latest"
    assert labels.get("pod-security.kubernetes.io/audit") == "restricted"
    assert labels.get("pod-security.kubernetes.io/audit-version") == "latest"
    assert labels.get("pod-security.kubernetes.io/warn") == "restricted"
    assert labels.get("pod-security.kubernetes.io/warn-version") == "latest"
    privileged_pod = {
        "apiVersion": "v1",
        "kind": "Pod",
        "metadata": {"name": "priv-pod"},
        "spec": {
            "hostNetwork": True,
            "containers": [
                {"name": "app", "image": "busybox", "securityContext": {"privileged": True}}
            ],
        },
    }
    baseline_pod = {
        "apiVersion": "v1",
        "kind": "Pod",
        "metadata": {"name": "base-pod"},
        "spec": {"containers": [{"name": "app", "image": "busybox"}]},
    }
    restricted_pod = {
        "apiVersion": "v1",
        "kind": "Pod",
        "metadata": {"name": "rest-pod"},
        "spec": {
            "securityContext": {"runAsNonRoot": True},
            "containers": [
                {
                    "name": "app",
                    "image": "busybox",
                    "securityContext": {
                        "allowPrivilegeEscalation": False,
                        "capabilities": {"drop": ["ALL"]},
                    },
                }
            ],
        },
    }
    assert evaluate_pss_compliance(privileged_pod, "privileged") is True
    assert evaluate_pss_compliance(baseline_pod, "privileged") is True
    assert evaluate_pss_compliance(restricted_pod, "privileged") is True
    assert evaluate_pss_compliance(privileged_pod, "baseline") is False
    assert evaluate_pss_compliance(baseline_pod, "baseline") is True
    assert evaluate_pss_compliance(restricted_pod, "baseline") is True
    assert evaluate_pss_compliance(privileged_pod, "restricted") is False
    assert evaluate_pss_compliance(baseline_pod, "restricted") is False
    assert evaluate_pss_compliance(restricted_pod, "restricted") is True

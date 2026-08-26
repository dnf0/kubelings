"""
Exercise: solutions/08_security_rbac/rbac05.py
Topic: Pod Security Standards (PSS/PSA)

Reference Solution
"""

from typing import Any, Dict
import yaml
from kubelings.validator import validate_manifest

NAMESPACE_MANIFEST = """
apiVersion: v1
kind: Namespace
metadata:
  name: secure-production
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/enforce-version: latest
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/audit-version: latest
    pod-security.kubernetes.io/warn: restricted
    pod-security.kubernetes.io/warn-version: latest
"""


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


def verify():
    manifest = yaml.safe_load(NAMESPACE_MANIFEST)
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

    # Test PSS evaluation logic
    privileged_pod = {
        "apiVersion": "v1",
        "kind": "Pod",
        "metadata": {"name": "priv-pod"},
        "spec": {
            "hostNetwork": True,
            "containers": [{"name": "app", "image": "busybox", "securityContext": {"privileged": True}}],
        },
    }

    baseline_pod = {
        "apiVersion": "v1",
        "kind": "Pod",
        "metadata": {"name": "base-pod"},
        "spec": {
            "containers": [{"name": "app", "image": "busybox"}],
        },
    }

    restricted_pod = {
        "apiVersion": "v1",
        "kind": "Pod",
        "metadata": {"name": "rest-pod"},
        "spec": {
            "securityContext": {"runAsNonRoot": True},
            "containers": [{
                "name": "app",
                "image": "busybox",
                "securityContext": {
                    "allowPrivilegeEscalation": False,
                    "capabilities": {"drop": ["ALL"]},
                },
            }],
        },
    }

    # Privileged level allows everything
    assert evaluate_pss_compliance(privileged_pod, "privileged") is True
    assert evaluate_pss_compliance(baseline_pod, "privileged") is True
    assert evaluate_pss_compliance(restricted_pod, "privileged") is True

    # Baseline rejects hostNetwork and privileged containers
    assert evaluate_pss_compliance(privileged_pod, "baseline") is False
    assert evaluate_pss_compliance(baseline_pod, "baseline") is True
    assert evaluate_pss_compliance(restricted_pod, "baseline") is True

    # Restricted requires non-root, no privilege escalation, and dropping ALL capabilities
    assert evaluate_pss_compliance(privileged_pod, "restricted") is False
    assert evaluate_pss_compliance(baseline_pod, "restricted") is False
    assert evaluate_pss_compliance(restricted_pod, "restricted") is True

    print("✓ rbac05 passed!")


if __name__ == "__main__":
    verify()

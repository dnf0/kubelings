"""
Exercise: exercises/08_security_rbac/rbac05.py
Topic: Pod Security Standards (PSS/PSA)

Instructions:
Kubernetes Pod Security Admission (PSA) enforces Pod Security Standards (Privileged, Baseline,
Restricted) through namespace labels across three modes: `enforce`, `audit`, and `warn`.

1. Define a Namespace manifest for 'secure-production':
   - enforce: 'restricted' (version: 'latest')
   - audit: 'restricted' (version: 'latest')
   - warn: 'restricted' (version: 'latest')
2. Implement `evaluate_pss_compliance(pod_manifest, level)`:
   - For level == 'privileged': returns True for any valid pod.
   - For level == 'baseline': returns False if any container has `privileged: true`, or if
     pod uses `hostNetwork: true`, `hostPID: true`, or `hostIPC: true`. Otherwise True.
   - For level == 'restricted': returns True only if baseline passes AND container has
     `allowPrivilegeEscalation: false`, `runAsNonRoot: true` (at pod or container level),
     and container `capabilities.drop` includes 'ALL'.
"""

# I AM NOT DONE

from typing import Any, Dict
import yaml
from kubelings.validator import validate_manifest

NAMESPACE_MANIFEST = """
apiVersion: v1
kind: Namespace
metadata:
  name: secure-production
  labels:
    pod-security.kubernetes.io/enforce: ???
    pod-security.kubernetes.io/enforce-version: latest
    pod-security.kubernetes.io/audit: ???
    pod-security.kubernetes.io/audit-version: latest
    pod-security.kubernetes.io/warn: ???
    pod-security.kubernetes.io/warn-version: latest
"""


def evaluate_pss_compliance(pod_manifest: Dict[str, Any], level: str) -> bool:
    """Evaluate whether a Pod manifest satisfies the given Pod Security Standard level."""
    # TODO: Implement PSS compliance checks for privileged, baseline, and restricted
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

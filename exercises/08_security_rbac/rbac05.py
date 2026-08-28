"""
Exercise: exercises/08_security_rbac/rbac05.py
Topic: Pod Security Standards (PSS/PSA)

Context & Why:
Kubernetes Pod Security Admission (PSA) replaces deprecated PodSecurityPolicies (PSP) with built-in,
declarative namespace policy enforcement based on three Pod Security Standards: `Privileged` (unrestricted),
`Baseline` (prevents known privilege escalations), and `Restricted` (heavily hardened). Namespaces configure
PSA across three operational modes via labels: `enforce` (rejects non-compliant pods), `audit` (records
audit log annotations without blocking), and `warn` (returns user-facing CLI warnings). This tripartite model
allows platform teams to safely test and audit workload compliance before switching to strict enforcement.

Instructions:
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

from typing import Any, Dict

import yaml

from kubelings.validator import validate_manifest

NAMESPACE_MANIFEST = """
apiVersion: v1
kind: Namespace
metadata:
  name: secure-production
  labels:
    # TODO: Set the Pod Security Admission enforcement level to 'restricted'.
    # WHY: Causes the API server admission plugin to strictly reject any pod that fails restricted PSS checks.
    pod-security.kubernetes.io/enforce: ???
    pod-security.kubernetes.io/enforce-version: latest
    # TODO: Set the Pod Security Admission audit level to 'restricted'.
    # WHY: Adds audit log annotations for any non-compliant pods admitted under exemption or grandfathered in.
    pod-security.kubernetes.io/audit: ???
    pod-security.kubernetes.io/audit-version: latest
    # TODO: Set the Pod Security Admission warning level to 'restricted'.
    # WHY: Emits helpful warning messages back to kubectl clients when applying non-compliant resources.
    pod-security.kubernetes.io/warn: ???
    pod-security.kubernetes.io/warn-version: latest
"""


def evaluate_pss_compliance(pod_manifest: Dict[str, Any], level: str) -> bool:
    """Evaluate whether a Pod manifest satisfies the given Pod Security Standard level."""
    # TODO: Implement PSS compliance checks for privileged (allow all), baseline (no host namespaces or privileged containers), and restricted (baseline + non-root + no privilege escalation + drop ALL capabilities).
    # WHY: Programmatic admission controllers evaluate pod specs against standard compliance criteria to enforce workload isolation.
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
            "containers": [
                {"name": "app", "image": "busybox", "securityContext": {"privileged": True}}
            ],
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

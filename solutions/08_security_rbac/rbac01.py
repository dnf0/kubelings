"""
Exercise: solutions/08_security_rbac/rbac01.py
Topic: ServiceAccounts & Token Management

Reference Solution
"""

import yaml
from kubelings.validator import validate_manifests

MANIFESTS = """
apiVersion: v1
kind: ServiceAccount
metadata:
  name: build-robot-sa
  namespace: ci-runners
automountServiceAccountToken: false
---
apiVersion: v1
kind: Pod
metadata:
  name: build-worker-pod
  namespace: ci-runners
spec:
  serviceAccountName: build-robot-sa
  automountServiceAccountToken: false
  containers:
  - name: runner
    image: alpine:3.19
    command: ["sh", "-c", "echo Ready && sleep 3600"]
"""


def verify():
    manifests = list(yaml.safe_load_all(MANIFESTS))
    assert len(manifests) == 2, "Must contain exactly 2 manifests (ServiceAccount and Pod)"
    validate_manifests(manifests, expected_kinds=["ServiceAccount", "Pod"])

    sa, pod = manifests[0], manifests[1]

    # Check ServiceAccount
    assert sa["metadata"]["name"] == "build-robot-sa", (
        "ServiceAccount name must be 'build-robot-sa'"
    )
    assert sa["metadata"]["namespace"] == "ci-runners", (
        "ServiceAccount namespace must be 'ci-runners'"
    )
    assert sa.get("automountServiceAccountToken") is False, (
        "ServiceAccount automountServiceAccountToken must be False"
    )

    # Check Pod
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

    print("✓ rbac01 passed!")


if __name__ == "__main__":
    verify()

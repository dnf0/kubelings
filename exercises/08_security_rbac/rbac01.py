"""
Exercise: exercises/08_security_rbac/rbac01.py
Topic: ServiceAccounts & Token Management

Context & Why:
In production Kubernetes clusters, workload identity is established via ServiceAccounts.
By default, every pod without an explicit service account inherits the namespace's 'default'
ServiceAccount and automatically mounts a projected API token credential at
`/var/run/secrets/kubernetes.io/serviceaccount/token`. If a workload is compromised (e.g. via RCE),
an attacker can leverage this mounted token to query or manipulate cluster resources. Following
the principle of least privilege, disabling `automountServiceAccountToken: false` at both the
ServiceAccount and Pod levels guarantees that non-control-plane workloads (such as CI runners,
batch jobs, and frontend services) do not needlessly expose API access tokens to container runtimes.

Instructions:
1. Define a ServiceAccount 'build-robot-sa' in namespace 'ci-runners':
   - automountServiceAccountToken: false
2. Define a Pod 'build-worker-pod' in namespace 'ci-runners':
   - serviceAccountName: 'build-robot-sa'
   - automountServiceAccountToken: false
   - container 'runner': image 'alpine:3.19', command ["sh", "-c", "echo Ready && sleep 3600"]
"""

import yaml

from kubelings.validator import validate_manifests

MANIFESTS = """
apiVersion: v1
kind: ServiceAccount
metadata:
  name: build-robot-sa
  namespace: ci-runners
# TODO: Disable automatic token mounting for this ServiceAccount (boolean false).
# WHY: Prevents pods using this ServiceAccount from automatically mounting API credentials.
automountServiceAccountToken: ???
---
apiVersion: v1
kind: Pod
metadata:
  name: build-worker-pod
  namespace: ci-runners
spec:
  # TODO: Assign the custom ServiceAccount name 'build-robot-sa'.
  # WHY: Decouples the workload from the default namespace ServiceAccount identity.
  serviceAccountName: ???
  # TODO: Disable token mounting at the Pod spec level (boolean false).
  # WHY: Provides defense-in-depth even if the underlying ServiceAccount configuration changes.
  automountServiceAccountToken: ???
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

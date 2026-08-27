"""
Exercise: exercises/08_security_rbac/rbac04.py
Topic: Pod & Container SecurityContext

Instructions:
Security contexts define privilege and access control settings for Pods and Containers.
Best practices include running as non-root, preventing privilege escalation, enforcing
a read-only root filesystem, applying a RuntimeDefault seccomp profile, and dropping
unnecessary Linux capabilities.

1. Configure Pod 'secure-app-pod' with Pod-level `spec.securityContext`:
   - runAsNonRoot: true
   - runAsUser: 10001
   - runAsGroup: 10001
   - fsGroup: 20001
   - seccompProfile: {type: 'RuntimeDefault'}
2. Configure Container 'secure-app' with container-level `securityContext`:
   - allowPrivilegeEscalation: false
   - readOnlyRootFilesystem: true
   - capabilities: drop ['ALL'], add ['NET_BIND_SERVICE']
"""

import yaml

from kubelings.validator import validate_manifest

POD_MANIFEST = """
apiVersion: v1
kind: Pod
metadata:
  name: secure-app-pod
spec:
  securityContext:
    runAsNonRoot: ???
    runAsUser: 10001
    runAsGroup: 10001
    fsGroup: 20001
    seccompProfile:
      type: ???
  containers:
  - name: secure-app
    image: alpine:3.19
    command: ["sh", "-c", "echo Security context applied && sleep 3600"]
    securityContext:
      allowPrivilegeEscalation: ???
      readOnlyRootFilesystem: ???
      capabilities:
        drop:
        - ???
        add:
        - ???
"""


def verify():
    manifest = yaml.safe_load(POD_MANIFEST)
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(manifest, expected_kind="Pod", expected_api_version="v1")

    assert manifest["metadata"]["name"] == "secure-app-pod"

    # Verify Pod-level security context
    pod_sc = manifest["spec"].get("securityContext", {})
    assert pod_sc.get("runAsNonRoot") is True, "Pod runAsNonRoot must be True"
    assert pod_sc.get("runAsUser") == 10001, "Pod runAsUser must be 10001"
    assert pod_sc.get("runAsGroup") == 10001, "Pod runAsGroup must be 10001"
    assert pod_sc.get("fsGroup") == 20001, "Pod fsGroup must be 20001"
    assert pod_sc.get("seccompProfile", {}).get("type") == "RuntimeDefault", (
        "seccompProfile must be RuntimeDefault"
    )

    # Verify Container-level security context
    container = manifest["spec"]["containers"][0]
    c_sc = container.get("securityContext", {})
    assert c_sc.get("allowPrivilegeEscalation") is False, "allowPrivilegeEscalation must be False"
    assert c_sc.get("readOnlyRootFilesystem") is True, "readOnlyRootFilesystem must be True"

    caps = c_sc.get("capabilities", {})
    assert caps.get("drop") == ["ALL"], "capabilities.drop must contain 'ALL'"
    assert caps.get("add") == ["NET_BIND_SERVICE"], (
        "capabilities.add must contain 'NET_BIND_SERVICE'"
    )

    print("✓ rbac04 passed!")


if __name__ == "__main__":
    verify()

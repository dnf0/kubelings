"""
Exercise: exercises/08_security_rbac/rbac04.py
Topic: Pod & Container SecurityContext

Context & Why:
SecurityContext settings configure Linux kernel security primitives (UID/GID namespaces,
Linux capabilities, seccomp filters, and volume ownership permissions) at both the Pod and
Container levels. Running containers as root (`UID 0`) or permitting privilege escalation
dramatically increases the blast radius of container breakouts. Hardening workloads according
to production security baselines requires enforcing non-root execution (`runAsNonRoot: true`),
disallowing privilege escalation (`allowPrivilegeEscalation: false`), enforcing an immutable
root filesystem (`readOnlyRootFilesystem: true`), dropping all default Linux capabilities
(`drop: ["ALL"]`), and applying the restrictive `RuntimeDefault` seccomp profile.

Instructions:
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
    # TODO: Require containers in this pod to run as non-root (boolean true).
    # WHY: Kubelet will validate at container start that the entrypoint UID is not 0 (root).
    runAsNonRoot: ???
    runAsUser: 10001
    runAsGroup: 10001
    fsGroup: 20001
    seccompProfile:
      # TODO: Set seccomp profile type to 'RuntimeDefault'.
      # WHY: Restricts unneeded Linux system calls using the container runtime's hardened default filter.
      type: ???
  containers:
  - name: secure-app
    image: alpine:3.19
    command: ["sh", "-c", "echo Security context applied && sleep 3600"]
    securityContext:
      # TODO: Disallow privilege escalation (boolean false).
      # WHY: Prevents setuid/setgid binaries or child processes from gaining more privileges than their parent.
      allowPrivilegeEscalation: ???
      # TODO: Mount the container root filesystem as read-only (boolean true).
      # WHY: Prevents malicious payloads or compromised processes from writing to root binary directories.
      readOnlyRootFilesystem: ???
      capabilities:
        drop:
        # TODO: Drop all default Linux kernel capabilities ('ALL').
        # WHY: Removes dangerous kernel privileges (e.g. CAP_SYS_ADMIN, CAP_NET_RAW) not needed by the app.
        - ???
        add:
        # TODO: Explicitly add only 'NET_BIND_SERVICE'.
        # WHY: Allows binding to privileged low-numbered network ports (<1024) without requiring root UID.
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

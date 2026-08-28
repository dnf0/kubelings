"""
Exercise: exercises/03_config_secrets/config04.py
Topic: Secret Volume Mounts & Permissions (defaultMode)

Context & Why:
When a Secret is mounted into a Pod as a volume, Kubernetes mounts it using an in-memory
`tmpfs` filesystem on the host node, guaranteeing that sensitive material is never written
to physical disk. To implement defense-in-depth, permissions on the mounted secret files must
be strictly restricted. The `defaultMode` setting specifies POSIX file permissions: setting
`defaultMode: 256` (octal `0400`) ensures files are readable only by the process owner,
preventing other non-root container users from inspecting secrets. Additionally, setting
`readOnly: true` in the container `volumeMounts` enforces immutability at the Linux mount layer.

Instructions:
Secret volumes are backed by memory (tmpfs) rather than persistent node disk.
To restrict access to sensitive keys (e.g. TLS private keys), you should specify:
1. `defaultMode: 0400` (octal 0400 = decimal 256: read-only by owner).
2. `readOnly: true` on the container volumeMount.

Complete the Pod manifest below:
- Name: 'secure-cert-pod'
- Volume 'tls-certs' from secret 'tls-secret' with defaultMode 256 (0400 octal).
- Mount 'tls-certs' at '/etc/tls' with readOnly: true.
"""

import yaml

from kubelings.validator import validate_manifest

POD_MANIFEST = """
apiVersion: v1
kind: Pod
metadata:
  name: secure-cert-pod
spec:
  volumes:
  - name: tls-certs
    secret:
      secretName: tls-secret
      # TODO: Configure defaultMode to 256 (0400 octal)
      # WHY: Restricts POSIX file permissions to read-only for the container owner, preventing unauthorized processes from accessing private keys.
  containers:
  - name: secure-web
    image: nginx:alpine
    volumeMounts:
    - name: tls-certs
      mountPath: /etc/tls
      # TODO: Set readOnly: true
      # WHY: Prevents the container process from modifying or writing over mounted secret files on the tmpfs filesystem.
"""


def verify():
    manifest = yaml.safe_load(POD_MANIFEST)
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(manifest, expected_kind="Pod", expected_api_version="v1")

    assert manifest["metadata"]["name"] == "secure-cert-pod"

    vol = manifest["spec"]["volumes"][0]
    assert vol["name"] == "tls-certs"
    assert vol["secret"]["secretName"] == "tls-secret"
    default_mode = vol["secret"].get("defaultMode")
    # Accept either integer 256 (0o400) or 0o400
    assert default_mode in (256, 0o400), f"defaultMode must be 256 (0400 octal), got {default_mode}"

    mount = manifest["spec"]["containers"][0]["volumeMounts"][0]
    assert mount["name"] == "tls-certs"
    assert mount["mountPath"] == "/etc/tls"
    assert mount.get("readOnly") is True, "VolumeMount must specify readOnly: true"

    print("✓ config04 passed!")


if __name__ == "__main__":
    verify()

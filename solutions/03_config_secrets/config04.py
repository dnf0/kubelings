"""
Exercise: solutions/03_config_secrets/config04.py
Topic: Secret Volume Mounts & Permissions (defaultMode)

Reference Solution
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
      defaultMode: 256
  containers:
  - name: secure-web
    image: nginx:alpine
    volumeMounts:
    - name: tls-certs
      mountPath: /etc/tls
      readOnly: true
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

"""
Exercise: solutions/04_storage/storage01.py
Topic: Volume Types (emptyDir & hostPath)

Reference Solution
"""

import yaml

from kubelings.validator import validate_manifest

POD_MANIFEST = """
apiVersion: v1
kind: Pod
metadata:
  name: log-collector-pod
spec:
  containers:
  - name: collector
    image: busybox:1.36
    command: ["sh", "-c", "tail -f /dev/null"]
    volumeMounts:
    - name: scratch-volume
      mountPath: /tmp/scratch
    - name: host-log-volume
      mountPath: /var/log/host-app
      readOnly: true
  volumes:
  - name: scratch-volume
    emptyDir: {}
  - name: host-log-volume
    hostPath:
      path: /var/log/app
      type: DirectoryOrCreate
"""


def verify():
    manifest = yaml.safe_load(POD_MANIFEST)
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(manifest, expected_kind="Pod", expected_api_version="v1")

    assert manifest["metadata"]["name"] == "log-collector-pod", (
        "Pod name must be 'log-collector-pod'"
    )
    container = manifest["spec"]["containers"][0]
    assert container["name"] == "collector"
    assert container["image"] == "busybox:1.36"

    mounts = {m["name"]: m for m in container.get("volumeMounts", [])}
    assert "scratch-volume" in mounts, "scratch-volume must be mounted"
    assert mounts["scratch-volume"]["mountPath"] == "/tmp/scratch"
    assert "host-log-volume" in mounts, "host-log-volume must be mounted"
    assert mounts["host-log-volume"]["mountPath"] == "/var/log/host-app"
    assert mounts["host-log-volume"].get("readOnly") is True

    volumes = {v["name"]: v for v in manifest["spec"].get("volumes", [])}
    assert "scratch-volume" in volumes, "Volume 'scratch-volume' missing in spec.volumes"
    assert isinstance(volumes["scratch-volume"].get("emptyDir"), dict)

    assert "host-log-volume" in volumes, "Volume 'host-log-volume' missing in spec.volumes"
    host_path = volumes["host-log-volume"].get("hostPath", {})
    assert host_path.get("path") == "/var/log/app"
    assert host_path.get("type") == "DirectoryOrCreate"

    print("✓ storage01 passed!")


if __name__ == "__main__":
    verify()

"""
Exercise: exercises/01_pods/pods02.py
Topic: Multi-Container Pods & Sidecar Pattern

Instructions:
Construct a multi-container pod manifest named 'web-logger'.
1. Define an emptyDir volume named 'shared-logs' in spec.volumes.
2. The 'app' container (image: 'alpine:3.19') must mount 'shared-logs' at '/var/log/app'.
3. The 'sidecar-logger' container (image: 'busybox:1.36') must mount 'shared-logs' at '/var/log/shared' in readOnly mode.
"""

# I AM NOT DONE

import yaml
from kubelings.validator import validate_manifest

POD_MANIFEST = """
apiVersion: v1
kind: Pod
metadata:
  name: web-logger
spec:
  volumes:
  # TODO: define emptyDir volume 'shared-logs'
  containers:
  - name: app
    image: alpine:3.19
    volumeMounts:
    - name: ???
      mountPath: /var/log/app
  # TODO: add sidecar-logger container
"""


def verify():
    manifest = yaml.safe_load(POD_MANIFEST)
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(manifest, expected_kind="Pod", expected_api_version="v1")

    assert manifest["metadata"]["name"] == "web-logger", "Pod name must be 'web-logger'"

    volumes = manifest["spec"].get("volumes", [])
    assert len(volumes) >= 1, "Must define at least one volume"
    assert volumes[0]["name"] == "shared-logs", "Volume name must be 'shared-logs'"
    assert "emptyDir" in volumes[0], "Volume must be of type emptyDir"

    containers = manifest["spec"]["containers"]
    assert len(containers) == 2, "Pod must contain exactly 2 containers (app and sidecar-logger)"

    c1 = containers[0]
    assert c1["name"] == "app"
    assert c1["image"] == "alpine:3.19"
    assert c1["volumeMounts"][0]["name"] == "shared-logs"
    assert c1["volumeMounts"][0]["mountPath"] == "/var/log/app"

    c2 = containers[1]
    assert c2["name"] == "sidecar-logger"
    assert c2["image"] == "busybox:1.36"
    assert c2["volumeMounts"][0]["name"] == "shared-logs"
    assert c2["volumeMounts"][0]["mountPath"] == "/var/log/shared"
    assert c2["volumeMounts"][0].get("readOnly") is True, (
        "Sidecar volumeMount must be readOnly: true"
    )

    print("✓ pods02 passed!")


if __name__ == "__main__":
    verify()

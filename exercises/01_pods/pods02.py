"""
Exercise: exercises/01_pods/pods02.py
Topic: Multi-Container Pods & Sidecar Pattern

Context & Why:
Multi-container pods allow co-locating tightly coupled processes that must share
resources. Containers within the same Pod share the network namespace (accessing
each other over localhost) and can mount shared filesystem volumes. The sidecar
pattern offloads secondary responsibilities (such as log shipping, metrics collection,
or proxying) from the primary application container. Using an `emptyDir` volume
allows the main container to produce logs to a directory while the sidecar tails and
transmits them, adhering to separation of concerns without requiring modifications
to the core application container.

Instructions:
Construct a multi-container pod manifest named 'web-logger'.
1. Define an emptyDir volume named 'shared-logs' in spec.volumes.
2. The 'app' container (image: 'alpine:3.19') must mount 'shared-logs' at '/var/log/app'.
3. The 'sidecar-logger' container (image: 'busybox:1.36') must mount 'shared-logs' at '/var/log/shared' in readOnly mode.
"""

import yaml

from kubelings.validator import validate_manifest

POD_MANIFEST = """
apiVersion: v1
kind: Pod
metadata:
  name: web-logger
spec:
  volumes:
  # TODO: Define an emptyDir volume named 'shared-logs'
  # WHY: emptyDir creates an ephemeral shared filesystem directory on the host node, allowing co-located containers in the pod to exchange files.
  containers:
  - name: app
    image: alpine:3.19
    volumeMounts:
    # TODO: Mount the 'shared-logs' volume at '/var/log/app'
    # WHY: The primary application container writes its output logs to this directory for consumption by the sidecar.
    - name: ???
      mountPath: /var/log/app
  # TODO: Add the 'sidecar-logger' container using image 'busybox:1.36' mounting 'shared-logs' at '/var/log/shared' with readOnly: true
  # WHY: Mounting the shared volume as read-only in the sidecar enforces least privilege and prevents the log aggregator from corrupting application log files.
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

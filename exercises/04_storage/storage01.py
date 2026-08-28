"""
Exercise: exercises/04_storage/storage01.py
Topic: Volume Types (emptyDir & hostPath)

Context & Why:
Storage volumes in Kubernetes outlive container restarts within a Pod. Two common node-local volume types are:
1. `emptyDir`: Created when a Pod is assigned to a Node, and deleted when the Pod is evicted or removed.
   It provides fast scratch space, temporary disk cache, and a shared exchange medium between co-located containers.
2. `hostPath`: Mounts a specific file or directory from the host node's underlying filesystem directly into the container.
   `hostPath` is primarily used for system daemons (such as log shipping daemons reading host `/var/log` or monitoring
   agents accessing `/sys`), but should be used cautiously with readOnly mounts to prevent container breakout vulnerabilities.

Instructions:
Fix the Pod manifest below to define a Pod named 'log-collector-pod':
1. Container 'collector' using image 'busybox:1.36' with command `["sh", "-c", "tail -f /dev/null"]`.
2. Volume 1: 'scratch-volume' of type `emptyDir: {}`, mounted at `/tmp/scratch` in container 'collector'.
3. Volume 2: 'host-log-volume' of type `hostPath` with path `/var/log/app` and type `DirectoryOrCreate`,
   mounted at `/var/log/host-app` (readOnly: true) in container 'collector'.
"""

import yaml

from kubelings.validator import validate_manifest

POD_MANIFEST = """
apiVersion: v1
kind: Pod
metadata:
  # TODO: Set metadata.name to 'log-collector-pod'
  # WHY: Names the pod uniquely for identification by the cluster control plane.
  name: ???
spec:
  containers:
  - name: collector
    # TODO: Set container image to 'busybox:1.36'
    # WHY: Provides a lightweight Linux utility runtime for log tailing.
    image: ???
    command: ["sh", "-c", "tail -f /dev/null"]
    volumeMounts:
    # TODO: Mount 'scratch-volume' at '/tmp/scratch' and 'host-log-volume' at '/var/log/host-app'
    # WHY: Mounts scratch space for temporary processing and host logs read-only for ingestion.
    - name: scratch-volume
      mountPath: ???
    - name: host-log-volume
      mountPath: ???
      readOnly: true
  volumes:
  - name: scratch-volume
    # TODO: Configure emptyDir volume as {}
    # WHY: emptyDir provides ephemeral scratch space tied to the lifecycle of the pod.
  - name: host-log-volume
    # TODO: Configure hostPath with path: '/var/log/app' and type: 'DirectoryOrCreate'
    # WHY: DirectoryOrCreate ensures the host directory is created on the node if it does not already exist.
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

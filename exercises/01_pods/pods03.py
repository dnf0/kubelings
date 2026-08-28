"""
Exercise: exercises/01_pods/pods03.py
Topic: Init Containers for Initialization

Context & Why:
Init containers are specialized containers that run sequentially to completion
before any application containers start. If an init container fails, the kubelet
restarts the Pod repeatedly until it succeeds (or according to its restartPolicy).
In production architectures, init containers isolate setup logic—such as running
database schema migrations, seeding initial configuration files, or waiting for
dependent backend services to become reachable—preventing the main application
container from entering crash loops or needing embedded bootstrapping scripts.

Instructions:
Complete the Pod manifest named 'init-service-demo'.
1. Add an initContainer named 'init-db-wait' with image 'busybox:1.36'.
2. The init container must run the command: ["sh", "-c", "echo waiting for db..."]
3. The main container should be named 'main-app' with image 'nginx:alpine'.
"""

import yaml

from kubelings.validator import validate_manifest

POD_MANIFEST = """
apiVersion: v1
kind: Pod
metadata:
  name: init-service-demo
spec:
  # TODO: Define initContainers with container 'init-db-wait' running image 'busybox:1.36' and command ["sh", "-c", "echo waiting for db..."]
  # WHY: Init containers guarantee that environment setup and dependency checks finish before the primary application container is launched.
  containers:
  # TODO: Set the main application container name to 'main-app'
  # WHY: Naming application containers clearly differentiates core workloads from preceding initialization stages in pod inspection and log aggregation.
  - name: ???
    image: nginx:alpine
"""


def verify():
    manifest = yaml.safe_load(POD_MANIFEST)
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(manifest, expected_kind="Pod", expected_api_version="v1")

    assert manifest["metadata"]["name"] == "init-service-demo"

    init_containers = manifest["spec"].get("initContainers", [])
    assert len(init_containers) == 1, "Must define exactly 1 initContainer"
    init_c = init_containers[0]
    assert init_c["name"] == "init-db-wait", "Init container name must be 'init-db-wait'"
    assert init_c["image"] == "busybox:1.36", "Init container image must be 'busybox:1.36'"
    assert "waiting for db" in str(init_c.get("command", "")), (
        "Init command must contain 'waiting for db'"
    )

    containers = manifest["spec"]["containers"]
    assert len(containers) == 1, "Must define exactly 1 main container"
    assert containers[0]["name"] == "main-app"
    assert containers[0]["image"] == "nginx:alpine"

    print("✓ pods03 passed!")


if __name__ == "__main__":
    verify()

"""
Exercise: solutions/01_pods/pods03.py
Topic: Init Containers for Initialization

Reference Solution
"""

import yaml

from kubelings.validator import validate_manifest

POD_MANIFEST = """
apiVersion: v1
kind: Pod
metadata:
  name: init-service-demo
spec:
  initContainers:
  - name: init-db-wait
    image: busybox:1.36
    command: ["sh", "-c", "echo waiting for db..."]
  containers:
  - name: main-app
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

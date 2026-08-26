"""
Exercise: exercises/01_pods/pods01.py
Topic: First Pod Manifest & Spec

Instructions:
Fix the YAML manifest below to define a valid Pod named 'nginx-web'
running nginx:alpine on container port 80 with label 'app: web'.
"""

# I AM NOT DONE

import yaml
from kubelings.validator import validate_manifest

POD_MANIFEST = """
apiVersion: v1
kind: Pod
metadata:
  name: ???
  labels:
    app: ???
spec:
  containers:
  - name: nginx
    image: ???
    ports:
    - containerPort: 0
"""


def verify():
    manifest = yaml.safe_load(POD_MANIFEST)
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(manifest, expected_kind="Pod", expected_api_version="v1")

    assert manifest["metadata"]["name"] == "nginx-web", "Pod name must be 'nginx-web'"
    assert manifest["metadata"]["labels"]["app"] == "web", "Label 'app' must equal 'web'"
    container = manifest["spec"]["containers"][0]
    assert container["name"] == "nginx", "Container name must be 'nginx'"
    assert container["image"] == "nginx:alpine", "Container image must be 'nginx:alpine'"
    assert container["ports"][0]["containerPort"] == 80, "Container port must be 80"
    print("✓ pods01 passed!")


if __name__ == "__main__":
    verify()

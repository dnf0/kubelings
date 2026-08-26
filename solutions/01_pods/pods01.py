"""
Exercise: solutions/01_pods/pods01.py
Topic: First Pod Manifest & Spec

Reference Solution
"""

import yaml

from kubelings.validator import validate_manifest

POD_MANIFEST = """
apiVersion: v1
kind: Pod
metadata:
  name: nginx-web
  labels:
    app: web
spec:
  containers:
  - name: nginx
    image: nginx:alpine
    ports:
    - containerPort: 80
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

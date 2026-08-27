"""
Exercise: exercises/02_controllers/ctrl01.py
Topic: ReplicaSets & Label Selectors

Instructions:
Fix the ReplicaSet manifest below.
1. The ReplicaSet must manage exactly 3 replicas.
2. The selector matchLabels must match the pod template metadata labels exactly
   (app: frontend, env: prod).
3. The pod template container should run 'nginx:alpine'.
"""

import yaml

from kubelings.validator import validate_manifest

REPLICA_SET_MANIFEST = """
apiVersion: apps/v1
kind: ReplicaSet
metadata:
  name: frontend-rs
spec:
  replicas: 0
  selector:
    matchLabels:
      app: frontend
      env: prod
  template:
    metadata:
      labels:
        app: backend
        env: dev
    spec:
      containers:
      - name: web
        image: ???
"""


def verify():
    manifest = yaml.safe_load(REPLICA_SET_MANIFEST)
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(manifest, expected_kind="ReplicaSet", expected_api_version="apps/v1")

    assert manifest["metadata"]["name"] == "frontend-rs"
    assert manifest["spec"]["replicas"] == 3, "spec.replicas must be 3"

    selector_labels = manifest["spec"]["selector"]["matchLabels"]
    template_labels = manifest["spec"]["template"]["metadata"]["labels"]
    assert selector_labels == {
        "app": "frontend",
        "env": "prod",
    }, "selector.matchLabels must be {app: frontend, env: prod}"
    assert template_labels == selector_labels, "template labels must match selector matchLabels"

    container = manifest["spec"]["template"]["spec"]["containers"][0]
    assert container["image"] == "nginx:alpine"

    print("✓ ctrl01 passed!")


if __name__ == "__main__":
    verify()

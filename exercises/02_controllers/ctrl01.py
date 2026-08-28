"""
Exercise: exercises/02_controllers/ctrl01.py
Topic: ReplicaSets & Label Selectors

Context & Why:
The ReplicaSet controller's primary purpose is to maintain a stable, specified number of
identical Pod replicas running at all times. It uses label selectors (`spec.selector.matchLabels`)
to continuously query the cluster state and determine how many matching pods currently exist.
A critical rule in Kubernetes controller design is that the labels defined in the pod template
(`spec.template.metadata.labels`) MUST satisfy the controller's selector (`spec.selector.matchLabels`).
If they do not match, the controller would spawn pods that it immediately fails to recognize,
leading to an infinite loop of runaway pod creation.

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
  # TODO: Set replicas to 3
  # WHY: Declares the desired replica count that the ReplicaSet reconciliation loop will enforce.
  replicas: 0
  selector:
    matchLabels:
      app: frontend
      env: prod
  template:
    metadata:
      # TODO: Update template labels to match selector matchLabels ({app: frontend, env: prod})
      # WHY: Kubernetes enforces that template labels must match selector labels so the controller owns and tracks the pods it creates.
      labels:
        app: backend
        env: dev
    spec:
      containers:
      - name: web
        # TODO: Set container image to 'nginx:alpine'
        # WHY: Specifies the application container image to run across all managed pod replicas.
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

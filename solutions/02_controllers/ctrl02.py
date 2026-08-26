"""
Exercise: solutions/02_controllers/ctrl02.py
Topic: Deployments & Rolling Updates

Reference Solution
"""

import yaml

from kubelings.validator import validate_manifest

DEPLOYMENT_MANIFEST = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-deployment
spec:
  replicas: 4
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 25%
      maxUnavailable: 0
  selector:
    matchLabels:
      app: api
  template:
    metadata:
      labels:
        app: api
    spec:
      containers:
      - name: api
        image: python:3.12-slim
"""


def verify():
    manifest = yaml.safe_load(DEPLOYMENT_MANIFEST)
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(manifest, expected_kind="Deployment", expected_api_version="apps/v1")

    assert manifest["metadata"]["name"] == "api-deployment"
    assert manifest["spec"]["replicas"] == 4, "Replicas must equal 4"

    strategy = manifest["spec"].get("strategy", {})
    assert strategy.get("type") == "RollingUpdate", "Strategy type must be 'RollingUpdate'"

    rolling_update = strategy.get("rollingUpdate", {})
    assert rolling_update.get("maxSurge") == "25%", "maxSurge must be '25%'"
    assert rolling_update.get("maxUnavailable") == 0, "maxUnavailable must be 0"

    container = manifest["spec"]["template"]["spec"]["containers"][0]
    assert container["image"] == "python:3.12-slim"

    print("✓ ctrl02 passed!")


if __name__ == "__main__":
    verify()

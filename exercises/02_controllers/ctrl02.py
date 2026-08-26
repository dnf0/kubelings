"""
Exercise: exercises/02_controllers/ctrl02.py
Topic: Deployments & Rolling Updates

Instructions:
Deployments support zero-downtime rolling updates.
Configure the Deployment manifest below:
1. Name: 'api-deployment' with 4 replicas.
2. Strategy type: 'RollingUpdate'
3. rollingUpdate parameters:
   - maxSurge: "25%" (allow at most 1 extra pod above replica count during rollout)
   - maxUnavailable: 0 (ensure 100% available capacity at all times)
4. Pod template runs container 'api' with image 'python:3.12-slim'.
"""

# I AM NOT DONE

import yaml
from kubelings.validator import validate_manifest

DEPLOYMENT_MANIFEST = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-deployment
spec:
  replicas: 0
  strategy:
    type: Recreate
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
        image: ???
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

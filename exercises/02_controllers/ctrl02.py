"""
Exercise: exercises/02_controllers/ctrl02.py
Topic: Deployments & Rolling Updates

Context & Why:
Deployments provide declarative updates for Pods and ReplicaSets. While the `Recreate`
strategy terminates all existing pods simultaneously before starting new ones (introducing
service downtime), the `RollingUpdate` strategy incrementally replaces old pods with new
ones to achieve zero-downtime deployments. Two key parameters tune this behavior:
- `maxSurge`: The maximum number or percentage of pods that can be created above the desired replica count.
- `maxUnavailable`: The maximum number or percentage of pods that can be unavailable during the update.
Setting `maxUnavailable: 0` ensures 100% service capacity is maintained at all times during rollouts.

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

import yaml

from kubelings.validator import validate_manifest

DEPLOYMENT_MANIFEST = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-deployment
spec:
  # TODO: Set replicas to 4
  # WHY: Maintains high availability across multiple pod instances for load balancing and fault tolerance.
  replicas: 0
  strategy:
    # TODO: Configure strategy type to RollingUpdate with maxSurge: "25%" and maxUnavailable: 0
    # WHY: Setting maxUnavailable: 0 ensures no capacity degradation occurs while the Deployment progressively updates replicas.
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
        # TODO: Set container image to 'python:3.12-slim'
        # WHY: Deploys a minimal, standard Python runtime environment for the API service.
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

"""
Exercise: exercises/10_lifecycle_probes/health02.py
Topic: Readiness Probes

Instructions:
Readiness probes indicate whether a container is ready to accept incoming client requests.
When a readiness probe fails, the pod is NOT restarted; instead, the endpoints controller
removes the Pod IP from all Services matching the pod's selectors until the probe succeeds again.

1. Configure Pod 'db-service-pod' with container 'db-worker':
   - image: 'postgres:16-alpine'
   - readinessProbe using exec:
     - command: ["pg_isready", "-h", "127.0.0.1", "-p", "5432", "-q"]
     - initialDelaySeconds: 5
     - periodSeconds: 5
     - successThreshold: 1
     - failureThreshold: 2
2. Implement `simulate_service_endpoints(pods_state)`:
   - Takes a list of pod state dictionaries `[{"ip": "10.244.1.2", "is_ready": True}, ...]`
   - Returns a list of IP strings for pods that are currently ready to receive traffic.
"""

from typing import Any, Dict, List

import yaml

from kubelings.validator import validate_manifest

POD_MANIFEST = """
apiVersion: v1
kind: Pod
metadata:
  name: db-service-pod
spec:
  containers:
  - name: db-worker
    image: postgres:16-alpine
    readinessProbe:
      exec:
        command:
        - ???
        - "-h"
        - "127.0.0.1"
        - "-p"
        - "5432"
        - "-q"
      initialDelaySeconds: ???
      periodSeconds: 5
      successThreshold: 1
      failureThreshold: ???
"""


def simulate_service_endpoints(pods_state: List[Dict[str, Any]]) -> List[str]:
    """Filter the list of pod endpoints to only include IPs of pods with is_ready=True."""
    # TODO: Implement endpoint filtering based on readiness state
    return []


def verify():
    manifest = yaml.safe_load(POD_MANIFEST)
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(manifest, expected_kind="Pod", expected_api_version="v1")

    assert manifest["metadata"]["name"] == "db-service-pod"
    container = manifest["spec"]["containers"][0]
    assert container["name"] == "db-worker"
    assert container["image"] == "postgres:16-alpine"

    probe = container.get("readinessProbe")
    assert isinstance(probe, dict), "readinessProbe must be defined"

    exec_action = probe.get("exec")
    assert isinstance(exec_action, dict), "readinessProbe.exec must be defined"
    assert exec_action.get("command") == ["pg_isready", "-h", "127.0.0.1", "-p", "5432", "-q"]

    assert probe.get("initialDelaySeconds") == 5
    assert probe.get("periodSeconds") == 5
    assert probe.get("successThreshold") == 1
    assert probe.get("failureThreshold") == 2

    # Test endpoint simulation
    fleet = [
        {"ip": "10.244.1.10", "is_ready": True},
        {"ip": "10.244.1.11", "is_ready": False},
        {"ip": "10.244.2.15", "is_ready": True},
        {"ip": "10.244.3.20", "is_ready": False},
    ]
    active_endpoints = simulate_service_endpoints(fleet)
    assert active_endpoints == ["10.244.1.10", "10.244.2.15"], (
        f"Unexpected active endpoints: {active_endpoints}"
    )

    print("✓ health02 passed!")


if __name__ == "__main__":
    verify()

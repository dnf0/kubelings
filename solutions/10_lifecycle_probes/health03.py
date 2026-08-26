"""
Exercise: solutions/10_lifecycle_probes/health03.py
Topic: Startup Probes

Reference Solution
"""

from typing import Any, Dict

import yaml

from kubelings.validator import validate_manifest

POD_MANIFEST = """
apiVersion: v1
kind: Pod
metadata:
  name: legacy-app-pod
spec:
  containers:
  - name: legacy-app
    image: openjdk:21-slim
    startupProbe:
      tcpSocket:
        port: 8080
      initialDelaySeconds: 10
      periodSeconds: 10
      failureThreshold: 30
    livenessProbe:
      httpGet:
        path: /alive
        port: 8080
      periodSeconds: 10
      failureThreshold: 3
"""


def calculate_max_startup_budget(startup_probe: Dict[str, Any]) -> int:
    """Calculate the maximum startup budget duration in seconds before liveness checks kick in."""
    initial = startup_probe.get("initialDelaySeconds", 0)
    period = startup_probe.get("periodSeconds", 10)
    threshold = startup_probe.get("failureThreshold", 3)
    return initial + (period * threshold)


def verify():
    manifest = yaml.safe_load(POD_MANIFEST)
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(manifest, expected_kind="Pod", expected_api_version="v1")

    assert manifest["metadata"]["name"] == "legacy-app-pod"
    container = manifest["spec"]["containers"][0]
    assert container["name"] == "legacy-app"
    assert container["image"] == "openjdk:21-slim"

    startup = container.get("startupProbe")
    assert isinstance(startup, dict), "startupProbe must be defined"
    assert startup.get("tcpSocket", {}).get("port") == 8080
    assert startup.get("initialDelaySeconds") == 10
    assert startup.get("periodSeconds") == 10
    assert startup.get("failureThreshold") == 30

    liveness = container.get("livenessProbe")
    assert isinstance(liveness, dict), "livenessProbe must be defined"
    assert liveness.get("httpGet", {}).get("path") == "/alive"
    assert liveness.get("httpGet", {}).get("port") == 8080
    assert liveness.get("periodSeconds") == 10
    assert liveness.get("failureThreshold") == 3

    # Test budget calculation
    assert calculate_max_startup_budget(startup) == 310, (
        "Startup budget should be 10 + (10 * 30) = 310 seconds"
    )

    custom_probe = {"initialDelaySeconds": 5, "periodSeconds": 2, "failureThreshold": 10}
    assert calculate_max_startup_budget(custom_probe) == 25

    print("✓ health03 passed!")


if __name__ == "__main__":
    verify()

"""
Exercise: exercises/10_lifecycle_probes/health03.py
Topic: Startup Probes

Context & Why:
Complex enterprise workloads (such as JVM applications, large machine learning models, or services
running schema migrations on boot) often require several minutes to complete initial boot sequence.
If configured solely with standard liveness probes, the kubelet may fail the probe during boot and
enter a crash loop, killing the container before it ever completes startup. Startup probes solve this
by establishing an initial boot grace period: all liveness and readiness probes are completely disabled
until the startup probe succeeds once. This decouples slow cold-start handling from sensitive fast-failing
runtime liveness checks.

Instructions:
1. Configure Pod 'legacy-app-pod' with container 'legacy-app':
   - image: 'openjdk:21-slim'
   - startupProbe using tcpSocket:
     - port: 8080
     - initialDelaySeconds: 10
     - periodSeconds: 10
     - failureThreshold: 30 (Allows up to 10 + (10 * 30) = 310 seconds to start up)
   - livenessProbe using httpGet:
     - path: '/alive'
     - port: 8080
     - periodSeconds: 10
     - failureThreshold: 3
2. Implement `calculate_max_startup_budget(startup_probe)`:
   - Returns the maximum time in seconds the container is allowed to initialize:
     initialDelaySeconds + (periodSeconds * failureThreshold).
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
        # TODO: Set the TCP socket check port to 8080.
        # WHY: Kubelet will probe whether the TCP socket opens when the JVM finishes binding its listener.
        port: ???
      initialDelaySeconds: 10
      periodSeconds: 10
      # TODO: Set failureThreshold to 30.
      # WHY: Grants 30 attempts of 10s periods (300s) + 10s initial delay = 310s maximum startup window.
      failureThreshold: ???
    livenessProbe:
      httpGet:
        # TODO: Set liveness HTTP check path to '/alive'.
        # WHY: Once startup succeeds, regular runtime liveness polling verifies application responsiveness on /alive.
        path: ???
        port: 8080
      periodSeconds: 10
      failureThreshold: 3
"""


def calculate_max_startup_budget(startup_probe: Dict[str, Any]) -> int:
    """Calculate the maximum startup budget duration in seconds before liveness checks kick in."""
    # TODO: Calculate the total startup time budget: initialDelaySeconds + (periodSeconds * failureThreshold).
    # WHY: Identifies the maximum time budget kubelet allows the container to initialize before marking it dead.
    return 0


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

"""
Exercise: exercises/10_lifecycle_probes/health01.py
Topic: Liveness Probes

Context & Why:
In production environments, applications can experience fatal edge cases like unrecoverable deadlocks,
corrupted heap memory, or infinite loops where the container process remains alive (PID exists) but is
incapable of making forward progress. Kubelet liveness probes regularly query container health (via HTTP GET,
TCP socket, or exec command). If the probe fails consecutively beyond `failureThreshold`, kubelet terminates
the unhealthy container and triggers a restart according to its `restartPolicy`, restoring service availability
without requiring human intervention.

Instructions:
1. Configure Pod 'web-liveness-pod' with container 'web':
   - image: 'nginx:1.25-alpine'
   - livenessProbe using httpGet:
     - path: '/healthz'
     - port: 8080
     - httpHeaders: [{'name': 'X-Custom-Header', 'value': 'Awesome'}]
     - initialDelaySeconds: 15
     - periodSeconds: 10
     - timeoutSeconds: 2
     - failureThreshold: 3
"""

import yaml

from kubelings.validator import validate_manifest

POD_MANIFEST = """
apiVersion: v1
kind: Pod
metadata:
  name: web-liveness-pod
spec:
  containers:
  - name: web
    image: nginx:1.25-alpine
    livenessProbe:
      httpGet:
        # TODO: Set the HTTP health check path to '/healthz'.
        # WHY: Directs kubelet to query the internal health diagnostic route.
        path: ???
        # TODO: Set the HTTP probe port to 8080.
        # WHY: Targets the application listening port for health endpoint probing.
        port: ???
        httpHeaders:
        # TODO: Configure custom HTTP header 'X-Custom-Header: Awesome'.
        # WHY: Provides authentication or custom routing headers required by the internal health check handler.
        - name: ???
          value: ???
      # TODO: Configure initial delay of 15 seconds.
      # WHY: Gives the container runtime sufficient time to initialize before health checks begin.
      initialDelaySeconds: ???
      periodSeconds: 10
      timeoutSeconds: 2
      failureThreshold: 3
"""


def verify():
    manifest = yaml.safe_load(POD_MANIFEST)
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(manifest, expected_kind="Pod", expected_api_version="v1")

    assert manifest["metadata"]["name"] == "web-liveness-pod"
    container = manifest["spec"]["containers"][0]
    assert container["name"] == "web"
    assert container["image"] == "nginx:1.25-alpine"

    probe = container.get("livenessProbe")
    assert isinstance(probe, dict), "livenessProbe must be defined"

    http_get = probe.get("httpGet")
    assert isinstance(http_get, dict), "livenessProbe.httpGet must be defined"
    assert http_get.get("path") == "/healthz", "httpGet path must be '/healthz'"
    assert http_get.get("port") == 8080, "httpGet port must be 8080"

    headers = http_get.get("httpHeaders", [])
    assert len(headers) == 1
    assert headers[0]["name"] == "X-Custom-Header"
    assert headers[0]["value"] == "Awesome"

    assert probe.get("initialDelaySeconds") == 15
    assert probe.get("periodSeconds") == 10
    assert probe.get("timeoutSeconds") == 2
    assert probe.get("failureThreshold") == 3

    print("✓ health01 passed!")


if __name__ == "__main__":
    verify()

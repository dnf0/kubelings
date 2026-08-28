"""
Exercise: exercises/10_lifecycle_probes/health04.py
Topic: Lifecycle Hooks & Graceful Shutdown

Context & Why:
During rolling updates, node drains, or autoscaling scale-down events, Kubernetes pods are terminated.
If an application process is immediately terminated via abrupt signals, active in-flight HTTP requests
are dropped and database transactions may be left incomplete. The `preStop` lifecycle hook executes
synchronously before the container receives `SIGTERM`, allowing the workload to notify service meshes,
drain active connections, and persist state. Setting an appropriate `terminationGracePeriodSeconds` (e.g. 60s)
ensures the container is given adequate time to complete graceful drainage before kubelet issues `SIGKILL`.

Instructions:
1. Configure Pod 'graceful-web-pod':
   - terminationGracePeriodSeconds: 60
   - Container 'web-server': image 'nginx:alpine'
   - lifecycle.postStart (exec): command `["/bin/sh", "-c", "echo Ready > /var/log/started.log"]`
   - lifecycle.preStop (httpGet): path '/prepare-shutdown', port 80
"""

import yaml

from kubelings.validator import validate_manifest

POD_MANIFEST = """
apiVersion: v1
kind: Pod
metadata:
  name: graceful-web-pod
spec:
  # TODO: Configure termination grace period of 60 seconds.
  # WHY: Grants sufficient time for in-flight requests to complete before kubelet sends SIGKILL.
  terminationGracePeriodSeconds: ???
  containers:
  - name: web-server
    image: nginx:alpine
    lifecycle:
      postStart:
        exec:
          command:
          # TODO: Specify the shell executable '/bin/sh'.
          # WHY: Runs initialization command immediately after the container is created.
          - ???
          - "-c"
          - "echo Ready > /var/log/started.log"
      preStop:
        httpGet:
          # TODO: Set preStop hook path to '/prepare-shutdown'.
          # WHY: Signals the web server to stop accepting new requests and drain connections before SIGTERM.
          path: ???
          # TODO: Set target HTTP port to 80.
          # WHY: Routes the shutdown signal to the active web listener.
          port: ???
"""


def verify():
    manifest = yaml.safe_load(POD_MANIFEST)
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(manifest, expected_kind="Pod", expected_api_version="v1")

    assert manifest["metadata"]["name"] == "graceful-web-pod"
    assert manifest["spec"].get("terminationGracePeriodSeconds") == 60, (
        "terminationGracePeriodSeconds must be 60"
    )

    container = manifest["spec"]["containers"][0]
    assert container["name"] == "web-server"
    assert container["image"] == "nginx:alpine"

    lifecycle = container.get("lifecycle")
    assert isinstance(lifecycle, dict), "lifecycle must be defined"

    # Verify postStart
    post_start = lifecycle.get("postStart", {})
    assert post_start.get("exec", {}).get("command") == [
        "/bin/sh",
        "-c",
        "echo Ready > /var/log/started.log",
    ]

    # Verify preStop
    pre_stop = lifecycle.get("preStop", {})
    assert pre_stop.get("httpGet", {}).get("path") == "/prepare-shutdown"
    assert pre_stop.get("httpGet", {}).get("port") == 80

    print("✓ health04 passed!")


if __name__ == "__main__":
    verify()

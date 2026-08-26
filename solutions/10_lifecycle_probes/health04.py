"""
Exercise: solutions/10_lifecycle_probes/health04.py
Topic: Lifecycle Hooks & Graceful Shutdown

Reference Solution
"""

import yaml

from kubelings.validator import validate_manifest

POD_MANIFEST = """
apiVersion: v1
kind: Pod
metadata:
  name: graceful-web-pod
spec:
  terminationGracePeriodSeconds: 60
  containers:
  - name: web-server
    image: nginx:alpine
    lifecycle:
      postStart:
        exec:
          command:
          - /bin/sh
          - "-c"
          - "echo Ready > /var/log/started.log"
      preStop:
        httpGet:
          path: /prepare-shutdown
          port: 80
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

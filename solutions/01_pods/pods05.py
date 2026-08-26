"""
Exercise: solutions/01_pods/pods05.py
Topic: Downward API & Environment Variables

Reference Solution
"""

import yaml
from kubelings.validator import validate_manifest

POD_MANIFEST = """
apiVersion: v1
kind: Pod
metadata:
  name: downward-api-pod
spec:
  containers:
  - name: client-app
    image: alpine:3.19
    env:
    - name: MY_POD_NAME
      valueFrom:
        fieldRef:
          fieldPath: metadata.name
    - name: MY_POD_NAMESPACE
      valueFrom:
        fieldRef:
          fieldPath: metadata.namespace
    - name: MY_POD_IP
      valueFrom:
        fieldRef:
          fieldPath: status.podIP
    - name: MY_NODE_NAME
      valueFrom:
        fieldRef:
          fieldPath: spec.nodeName
"""


def verify():
    manifest = yaml.safe_load(POD_MANIFEST)
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(manifest, expected_kind="Pod", expected_api_version="v1")

    assert manifest["metadata"]["name"] == "downward-api-pod"
    env_vars = manifest["spec"]["containers"][0].get("env", [])
    assert len(env_vars) == 4, "Must define all 4 Downward API environment variables"

    env_map = {item["name"]: item["valueFrom"]["fieldRef"]["fieldPath"] for item in env_vars}
    assert env_map.get("MY_POD_NAME") == "metadata.name", "MY_POD_NAME must reference metadata.name"
    assert env_map.get("MY_POD_NAMESPACE") == "metadata.namespace", (
        "MY_POD_NAMESPACE must reference metadata.namespace"
    )
    assert env_map.get("MY_POD_IP") == "status.podIP", "MY_POD_IP must reference status.podIP"
    assert env_map.get("MY_NODE_NAME") == "spec.nodeName", (
        "MY_NODE_NAME must reference spec.nodeName"
    )

    print("✓ pods05 passed!")


if __name__ == "__main__":
    verify()

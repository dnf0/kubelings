"""
Exercise: exercises/02_controllers/ctrl05.py
Topic: DaemonSets for Node-Level Daemons

Instructions:
DaemonSets ensure that all (or some) nodes run a copy of a Pod (e.g. log shippers, monitoring agents).
Important: Unlike Deployments or ReplicaSets, DaemonSets do NOT accept a `replicas` field!

Fix and complete the DaemonSet manifest below:
1. Remove the invalid `replicas` field.
2. Ensure selector matchLabels and template labels match {name: fluentbit}.
3. Add a nodeSelector to target nodes labeled 'logging: enabled'.
4. Add a toleration so the daemon can run on control-plane nodes:
   key: "node-role.kubernetes.io/control-plane", operator: "Exists", effect: "NoSchedule"
"""

# I AM NOT DONE

import yaml
from kubelings.validator import validate_manifest

DAEMONSET_MANIFEST = """
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: fluentbit-daemon
spec:
  replicas: 5  # ERROR: DaemonSets do not have replicas!
  selector:
    matchLabels:
      name: fluentbit
  template:
    metadata:
      labels:
        name: fluentbit
    spec:
      containers:
      - name: fluentbit
        image: fluent/fluent-bit:2.2
      # TODO: add nodeSelector and tolerations
"""


def verify():
    manifest = yaml.safe_load(DAEMONSET_MANIFEST)
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(manifest, expected_kind="DaemonSet", expected_api_version="apps/v1")

    assert manifest["metadata"]["name"] == "fluentbit-daemon"
    assert "replicas" not in manifest["spec"], "DaemonSet spec must NOT contain 'replicas'"

    pod_spec = manifest["spec"]["template"]["spec"]
    assert pod_spec.get("nodeSelector") == {"logging": "enabled"}, (
        "nodeSelector must be {'logging': 'enabled'}"
    )

    tolerations = pod_spec.get("tolerations", [])
    assert len(tolerations) == 1, "Must define control-plane toleration"
    assert tolerations[0].get("key") == "node-role.kubernetes.io/control-plane"
    assert tolerations[0].get("operator") == "Exists"
    assert tolerations[0].get("effect") == "NoSchedule"

    print("✓ ctrl05 passed!")


if __name__ == "__main__":
    verify()

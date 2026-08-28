"""
Exercise: exercises/02_controllers/ctrl05.py
Topic: DaemonSets for Node-Level Daemons

Context & Why:
DaemonSets guarantee that all (or a selected subset of) nodes in a Kubernetes cluster run
exactly one copy of a Pod. When new nodes are added to the cluster, the DaemonSet controller
automatically schedules a pod onto them, and cleans them up when nodes are removed.
DaemonSets power foundational node-level infrastructure: log collectors (Fluent Bit, Promtail),
metrics agents (Prometheus Node Exporter, Datadog), and CNI networking/storage plugins.
Because pod count is dynamically driven by node topology, specifying `replicas` is illegal.
Furthermore, because control-plane nodes have default taints (`node-role.kubernetes.io/control-plane:NoSchedule`),
cluster-wide daemons must define explicit tolerations to monitor or collect logs from master nodes.

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

import yaml

from kubelings.validator import validate_manifest

DAEMONSET_MANIFEST = """
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: fluentbit-daemon
spec:
  # TODO: Remove the invalid 'replicas' field
  # WHY: DaemonSets automatically run exactly one pod per matching node based on cluster topology; specifying replicas is invalid and rejected by the API server.
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
      # TODO: Add nodeSelector for {'logging': 'enabled'} and toleration for control-plane nodes
      # WHY: nodeSelector restricts daemon placement to specific nodes, while tolerations allow the daemon to schedule on tainted control-plane nodes for cluster-wide log collection.
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

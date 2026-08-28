"""
Exercise: exercises/07_scheduling/sched04.py
Topic: Taints and Tolerations

Context & Why:
While Node Affinity attracts Pods to certain nodes, `Taints` allow a Node to repel a set of Pods.
Taints and Tolerations work together to dedicate nodes to specific workloads (e.g., reserving expensive
NVIDIA H100 GPU nodes exclusively for ML training) or handle node lifecycle states (e.g. `node.kubernetes.io/unreachable`).
Taint Effects:
- `NoSchedule`: The scheduler will not place the pod on the node unless the pod has a matching toleration.
- `PreferNoSchedule`: The scheduler attempts to avoid the node, but will place the pod there if no other node is available.
- `NoExecute`: Immediately evicts running pods from the node unless they tolerate the taint. Specifying
  `tolerationSeconds` (e.g. 120s) grants a grace period before eviction, preventing immediate cascading failovers during transient network blips.

Instructions:
Taints allow a node to repel a set of pods. Tolerations are applied to pods to allow
(but not require) the pods to schedule onto nodes with matching taints.

Taint Effects:
- `NoSchedule`: Kube-scheduler will not schedule the pod onto the node unless tolerated.
- `PreferNoSchedule`: Kube-scheduler will try to avoid placing the pod on the node.
- `NoExecute`: Pod is evicted if already running on the node (unless tolerated, optionally with `tolerationSeconds`).

1. Configure the Pod manifest:
   - name: 'ml-trainer'
   - toleration 1: key 'gpu-type', operator 'Equal', value 'h100', effect 'NoSchedule'
   - toleration 2: key 'node.kubernetes.io/unreachable', operator 'Exists', effect 'NoExecute', tolerationSeconds 120
2. Implement `can_schedule_on_tainted_node(pod_tolerations, node_taints)`:
   - Returns True if every taint on the node with effect 'NoSchedule' or 'NoExecute'
     is matched by at least one toleration in `pod_tolerations`.
"""

from typing import Any, Dict, List

import yaml

from kubelings.validator import validate_manifest

POD_MANIFEST = """
apiVersion: v1
kind: Pod
metadata:
  name: ml-trainer
spec:
  tolerations:
  # TODO: Configure toleration with key: 'gpu-type', operator: 'Equal', value: 'h100', effect: 'NoSchedule'
  # WHY: Permits this ML workload to schedule on dedicated GPU nodes tainted with gpu-type=h100:NoSchedule.
  - key: gpu-type
    operator: ???
    value: ???
    effect: NoSchedule
  # TODO: Configure toleration for key: 'node.kubernetes.io/unreachable', operator: 'Exists', effect: 'NoExecute'
  # WHY: Allows a 120-second grace window before evicting the pod if the host node enters an unreachable network state.
  - key: node.kubernetes.io/unreachable
    operator: ???
    effect: ???
    tolerationSeconds: 120
  containers:
  - name: trainer
    image: pytorch/pytorch:2.2.0-cuda12.1-cudnn8-runtime
"""


def can_schedule_on_tainted_node(
    pod_tolerations: List[Dict[str, Any]],
    node_taints: List[Dict[str, Any]],
) -> bool:
    """Check whether a pod tolerates all blocking taints (NoSchedule/NoExecute) on a node."""
    # TODO: Implement taint/toleration matching logic comparing key, value, operator, and effect
    # WHY: Replicates the TaintToleration plugin in kube-scheduler that filters out nodes with un-tolerated taints.
    return False


def verify():
    manifest = yaml.safe_load(POD_MANIFEST)
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(manifest, expected_kind="Pod", expected_api_version="v1")

    tolerations = manifest["spec"]["tolerations"]
    assert len(tolerations) == 2

    t1 = tolerations[0]
    assert t1["key"] == "gpu-type"
    assert t1["operator"] == "Equal"
    assert t1["value"] == "h100"
    assert t1["effect"] == "NoSchedule"

    t2 = tolerations[1]
    assert t2["key"] == "node.kubernetes.io/unreachable"
    assert t2["operator"] == "Exists"
    assert t2["effect"] == "NoExecute"
    assert t2["tolerationSeconds"] == 120

    # Test taint checker
    h100_taints = [{"key": "gpu-type", "value": "h100", "effect": "NoSchedule"}]
    a100_taints = [{"key": "gpu-type", "value": "a100", "effect": "NoSchedule"}]
    unreachable_taints = [
        {"key": "node.kubernetes.io/unreachable", "value": "true", "effect": "NoExecute"}
    ]
    no_taints = []

    assert can_schedule_on_tainted_node(tolerations, h100_taints) is True
    assert can_schedule_on_tainted_node(tolerations, no_taints) is True
    assert can_schedule_on_tainted_node(tolerations, unreachable_taints) is True
    assert can_schedule_on_tainted_node(tolerations, a100_taints) is False, (
        "A100 taint not tolerated"
    )

    print("✓ sched04 passed!")


if __name__ == "__main__":
    verify()

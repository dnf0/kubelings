"""
Exercise: exercises/07_scheduling/sched04.py
Topic: Taints and Tolerations

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

# I AM NOT DONE

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
  - key: gpu-type
    operator: ???
    value: ???
    effect: NoSchedule
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
    # TODO: Implement taint/toleration matching logic
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

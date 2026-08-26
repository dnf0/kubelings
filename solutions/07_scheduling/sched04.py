"""
Exercise: solutions/07_scheduling/sched04.py
Topic: Taints and Tolerations

Reference Solution
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
  - key: gpu-type
    operator: Equal
    value: h100
    effect: NoSchedule
  - key: node.kubernetes.io/unreachable
    operator: Exists
    effect: NoExecute
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
    for taint in node_taints:
        effect = taint.get("effect")
        if effect not in ("NoSchedule", "NoExecute"):
            continue

        taint_key = taint.get("key")
        taint_value = taint.get("value")

        tolerated = False
        for tol in pod_tolerations:
            tol_effect = tol.get("effect")
            if tol_effect and tol_effect != effect:
                continue

            tol_key = tol.get("key")
            tol_op = tol.get("operator", "Equal")
            tol_val = tol.get("value")

            if tol_op == "Exists":
                if not tol_key or tol_key == taint_key:
                    tolerated = True
                    break
            elif tol_op == "Equal":
                if tol_key == taint_key and tol_val == taint_value:
                    tolerated = True
                    break

        if not tolerated:
            return False

    return True


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

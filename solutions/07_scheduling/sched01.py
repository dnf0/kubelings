"""
Exercise: solutions/07_scheduling/sched01.py
Topic: Node Placement (nodeName & nodeSelector)

Reference Solution
"""

from typing import Any, Dict
import yaml
from kubelings.validator import validate_manifests

PODS_MANIFEST = """
apiVersion: v1
kind: Pod
metadata:
  name: pinned-pod
spec:
  nodeName: worker-node-03
  containers:
  - name: app
    image: nginx:alpine
---
apiVersion: v1
kind: Pod
metadata:
  name: gpu-pod
spec:
  nodeSelector:
    accelerator: nvidia-tesla-v100
    disktype: nvme
  containers:
  - name: cuda-runner
    image: nvidia/cuda:12.0-base
"""


def match_node_selector(
    pod_manifest: Dict[str, Any],
    node_name: str,
    node_labels: Dict[str, str],
) -> bool:
    """Evaluate whether a candidate node satisfies the pod placement constraints."""
    spec = pod_manifest.get("spec", {})
    if "nodeName" in spec:
        return spec["nodeName"] == node_name

    selector = spec.get("nodeSelector", {})
    for k, v in selector.items():
        if node_labels.get(k) != v:
            return False

    return True


def verify():
    manifests = list(yaml.safe_load_all(PODS_MANIFEST))
    assert len(manifests) == 2, "Must define 2 pods"
    validate_manifests(manifests, expected_kinds=["Pod", "Pod"])

    pinned, gpu = manifests[0], manifests[1]

    assert pinned["metadata"]["name"] == "pinned-pod"
    assert pinned["spec"]["nodeName"] == "worker-node-03"

    assert gpu["metadata"]["name"] == "gpu-pod"
    assert gpu["spec"]["nodeSelector"]["accelerator"] == "nvidia-tesla-v100"
    assert gpu["spec"]["nodeSelector"]["disktype"] == "nvme"

    node_a = {"accelerator": "nvidia-tesla-v100", "disktype": "nvme", "zone": "us-east-1a"}
    node_b = {"accelerator": "tpu-v3", "disktype": "ssd", "zone": "us-east-1b"}

    assert match_node_selector(pinned, "worker-node-03", node_b) is True
    assert match_node_selector(pinned, "worker-node-01", node_a) is False

    assert match_node_selector(gpu, "worker-gpu-01", node_a) is True
    assert match_node_selector(gpu, "worker-gpu-02", node_b) is False

    print("✓ sched01 passed!")


if __name__ == "__main__":
    verify()

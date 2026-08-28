"""
Exercise: exercises/07_scheduling/sched01.py
Topic: Node Placement (nodeName & nodeSelector)

Context & Why:
Kubernetes provides several tiers of node placement control to map workloads to specialized hardware:
1. `nodeName`: The most direct (and rigid) placement mechanism. Setting `spec.nodeName` assigns the Pod
   directly to a named node, completely bypassing the `kube-scheduler` scheduling loop and filter plugins.
   This is primarily used by internal system components or custom schedulers.
2. `nodeSelector`: The simplest declarative constraint mechanism. It specifies a map of key-value pairs
   that candidate worker nodes must possess in their `metadata.labels` (e.g. `accelerator: nvidia-tesla-v100`)
   for the `kube-scheduler` to consider them eligible during the filtering phase.

Instructions:
Kubernetes provides basic node assignment mechanisms:
1. `nodeName`: Hardcodes the exact node where the pod runs, completely bypassing the kube-scheduler.
2. `nodeSelector`: Simple key-value label matching against candidate nodes.

1. Configure Pod 1 'pinned-pod':
   - Hardcode placement to node 'worker-node-03' via `nodeName`
2. Configure Pod 2 'gpu-pod':
   - Select nodes with labels: `accelerator: nvidia-tesla-v100` and `disktype: nvme`
3. Implement `match_node_selector(pod_manifest, node_name, node_labels)`:
   - If `nodeName` is defined: returns True only if `node_name == spec.nodeName`.
   - If `nodeSelector` is defined: returns True only if every key-value pair in `nodeSelector` exists in `node_labels`.
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
  # TODO: Set nodeName to 'worker-node-03'
  # WHY: Directly assigns the pod to worker-node-03, bypassing the scheduler algorithm entirely.
  nodeName: ???
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
    # TODO: Require node labels accelerator: 'nvidia-tesla-v100' and disktype: 'nvme'
    # WHY: Ensures the GPU training pod is scheduled only on worker nodes equipped with specialized hardware.
    accelerator: ???
    disktype: ???
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
    # TODO: Implement placement evaluator checking nodeName equality or subset matching for nodeSelector
    # WHY: Replicates the NodeName and NodeSelector filter plugins inside kube-scheduler.
    return False


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

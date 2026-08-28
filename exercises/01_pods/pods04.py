"""
Exercise: exercises/01_pods/pods04.py
Topic: Resource Requests, Limits & Quality of Service (QoS) Classes

Context & Why:
Resource management is essential for multi-tenant cluster stability and workload packing.
Kubernetes uses `requests` for scheduling decisions (ensuring the target node has enough
allocatable capacity) and `limits` to enforce hard boundaries via Linux cgroups (throttling
CPU when limits are exceeded, and OOM-killing containers when memory limits are breached).
Based on how requests and limits are configured across all containers in a Pod, Kubernetes
automatically assigns one of three Quality of Service (QoS) classes:
- Guaranteed: Every container specifies both CPU and Memory, with requests exactly equal to limits.
- Burstable: At least one container specifies a request or limit, but the pod does not meet Guaranteed criteria.
- BestEffort: No container specifies any CPU or Memory requests or limits.
During node memory pressure, the kubelet evicts BestEffort pods first, then Burstable pods,
and finally Guaranteed pods as a last resort.

Instructions:
Kubernetes assigns a QoS class to Pods based on container compute resources:
- Guaranteed: Every container has both CPU and Memory requests equal to limits.
- Burstable: At least one container has a memory or CPU request/limit, but not Guaranteed.
- BestEffort: No container has any memory or CPU requests or limits set.

1. Configure the POD_MANIFEST below for 'qos-guaranteed-pod' with equal requests and limits:
   CPU: "500m", Memory: "256Mi".
2. Implement the `compute_qos_class` function to calculate the QoS class for any pod manifest.
"""

from typing import Any, Dict

import yaml

from kubelings.validator import validate_manifest

POD_MANIFEST = """
apiVersion: v1
kind: Pod
metadata:
  name: qos-guaranteed-pod
spec:
  containers:
  - name: backend
    image: redis:alpine
    resources:
      # TODO: Set requests and limits for cpu to "500m" and memory to "256Mi"
      # WHY: Setting requests equal to limits across all containers ensures the Pod receives 'Guaranteed' QoS status with lowest eviction priority.
      requests:
        cpu: ???
        memory: ???
      limits:
        cpu: ???
        memory: ???
"""


def compute_qos_class(pod_dict: Dict[str, Any]) -> str:
    """Calculate the Kubernetes QoS class (Guaranteed, Burstable, BestEffort)."""
    # TODO: Implement QoS class calculation based on container resource requests and limits
    # WHY: Understanding QoS derivation rules allows operators to predict eviction behavior under node resource pressure.
    return "Unknown"


def verify():
    manifest = yaml.safe_load(POD_MANIFEST)
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(manifest, expected_kind="Pod", expected_api_version="v1")

    res = manifest["spec"]["containers"][0]["resources"]
    assert res["requests"]["cpu"] == "500m"
    assert res["requests"]["memory"] == "256Mi"
    assert res["limits"]["cpu"] == "500m"
    assert res["limits"]["memory"] == "256Mi"

    # Test Guaranteed class calculation
    assert compute_qos_class(manifest) == "Guaranteed"

    # Test Burstable class calculation
    burstable_manifest = {
        "apiVersion": "v1",
        "kind": "Pod",
        "metadata": {"name": "burstable-pod"},
        "spec": {
            "containers": [
                {
                    "name": "worker",
                    "image": "busybox",
                    "resources": {
                        "requests": {"cpu": "100m", "memory": "128Mi"},
                        "limits": {"cpu": "200m", "memory": "256Mi"},
                    },
                }
            ]
        },
    }
    assert compute_qos_class(burstable_manifest) == "Burstable"

    # Test BestEffort class calculation
    best_effort_manifest = {
        "apiVersion": "v1",
        "kind": "Pod",
        "metadata": {"name": "best-effort-pod"},
        "spec": {"containers": [{"name": "worker", "image": "busybox"}]},
    }
    assert compute_qos_class(best_effort_manifest) == "BestEffort"

    print("✓ pods04 passed!")


if __name__ == "__main__":
    verify()

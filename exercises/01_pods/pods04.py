"""
Exercise: exercises/01_pods/pods04.py
Topic: Resource Requests, Limits & Quality of Service (QoS) Classes

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
      requests:
        cpu: ???
        memory: ???
      limits:
        cpu: ???
        memory: ???
"""


def compute_qos_class(pod_dict: Dict[str, Any]) -> str:
    """Calculate the Kubernetes QoS class (Guaranteed, Burstable, BestEffort)."""
    # TODO: Implement QoS class calculation logic
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

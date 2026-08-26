"""
Exercise: solutions/01_pods/pods04.py
Topic: Resource Requests, Limits & Quality of Service (QoS) Classes

Reference Solution
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
        cpu: 500m
        memory: 256Mi
      limits:
        cpu: 500m
        memory: 256Mi
"""


def compute_qos_class(pod_dict: Dict[str, Any]) -> str:
    """Calculate the Kubernetes QoS class (Guaranteed, Burstable, BestEffort)."""
    containers = pod_dict.get("spec", {}).get("containers", [])
    if not containers:
        return "BestEffort"

    has_any_request_or_limit = False
    all_have_equal_limits_and_requests = True

    for c in containers:
        res = c.get("resources", {})
        requests = res.get("requests", {})
        limits = res.get("limits", {})

        req_cpu = requests.get("cpu")
        req_mem = requests.get("memory")
        lim_cpu = limits.get("cpu")
        lim_mem = limits.get("memory")

        if req_cpu or req_mem or lim_cpu or lim_mem:
            has_any_request_or_limit = True

        # For Guaranteed: every container must have CPU and Memory limits and requests specified,
        # and request == limit (or if limit is specified without request, K8s defaults request=limit).
        if not lim_cpu or not lim_mem:
            all_have_equal_limits_and_requests = False
        else:
            effective_req_cpu = req_cpu if req_cpu is not None else lim_cpu
            effective_req_mem = req_mem if req_mem is not None else lim_mem
            if effective_req_cpu != lim_cpu or effective_req_mem != lim_mem:
                all_have_equal_limits_and_requests = False

    if not has_any_request_or_limit:
        return "BestEffort"
    if all_have_equal_limits_and_requests:
        return "Guaranteed"
    return "Burstable"


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

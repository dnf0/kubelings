"""
Exercise: exercises/13_troubleshooting/troubleshoot03.py
Topic: Debugging Pending Pods & Scheduling Failures

Instructions:
When a pod remains in the `Pending` phase, the Kubernetes scheduler (`kube-scheduler`)
cannot find an eligible node that satisfies all filtering predicates.
Running `kubectl describe pod` reveals the scheduling failure reasons:
1. `Insufficient cpu`: Pod requests exceed capacity of any cluster node.
2. `node(s) didn't match Pod's node selector`: Invalid or non-existent node labels.
3. `node(s) had untolerated taint`: Nodes have taints without matching pod tolerations.

Fix Pod 'gpu-worker' in namespace 'ml-workloads':
1. Reduce CPU requests to '1' and memory requests to '2Gi'.
2. Correct nodeSelector from 'quantum-compute-node' to 'gpu-compute-node'.
3. Add toleration for taint: key='sku', operator='Equal', value='gpu-worker', effect='NoSchedule'.
"""

# I AM NOT DONE

import yaml
from kubelings.validator import validate_manifest

POD_MANIFEST = """
apiVersion: v1
kind: Pod
metadata:
  name: gpu-worker
  namespace: ml-workloads
spec:
  nodeSelector:
    node-type: quantum-compute-node
  tolerations:
  - key: sku
    operator: ???
    value: ???
    effect: ???
  containers:
  - name: trainer
    image: nvidia/cuda:12.2.0-base-ubuntu22.04
    resources:
      requests:
        cpu: "128"
        memory: "512Gi"
"""


def verify():
    manifest = yaml.safe_load(POD_MANIFEST)
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(manifest, expected_kind="Pod", expected_api_version="v1")

    metadata = manifest.get("metadata", {})
    assert metadata.get("name") == "gpu-worker"
    assert metadata.get("namespace") == "ml-workloads"

    spec = manifest.get("spec", {})

    # Check nodeSelector
    node_sel = spec.get("nodeSelector", {})
    assert node_sel.get("node-type") == "gpu-compute-node", (
        "nodeSelector must target 'gpu-compute-node'"
    )

    # Check tolerations
    tolerations = spec.get("tolerations", [])
    assert len(tolerations) >= 1, "Must define at least one toleration"
    tol = next((t for t in tolerations if t.get("key") == "sku"), None)
    assert tol is not None, "Must define toleration for key 'sku'"
    assert tol.get("operator") == "Equal"
    assert tol.get("value") == "gpu-worker"
    assert tol.get("effect") == "NoSchedule"

    # Check resources
    container = spec.get("containers", [])[0]
    reqs = container.get("resources", {}).get("requests", {})
    assert reqs.get("cpu") == "1", "CPU request must be '1'"
    assert reqs.get("memory") == "2Gi", "Memory request must be '2Gi'"

    print("✓ troubleshoot03 passed!")


if __name__ == "__main__":
    verify()

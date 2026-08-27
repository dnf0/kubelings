"""
Exercise: exercises/24_kuberay_ml/ray02.py
Topic: Heterogeneous Worker Pools & Autoscaling

Instructions:
Configure a heterogeneous RayCluster named 'ray-cluster-heterogeneous':
1. Set 'apiVersion' to 'ray.io/v1' and 'kind' to 'RayCluster'.
2. In 'spec.headGroupSpec', configure container 'ray-head' with image 'rayproject/ray:2.35.0'.
3. In 'spec.workerGroupSpecs', define two distinct worker pools:
   a. 'cpu-workers': replicas: 2, minReplicas: 2, maxReplicas: 10, container 'ray-cpu-worker'
      with image 'rayproject/ray:2.35.0'.
   b. 'gpu-workers': replicas: 1, minReplicas: 0, maxReplicas: 4, container 'ray-gpu-worker'
      with image 'rayproject/ray:2.35.0-gpu' and resource limit 'nvidia.com/gpu: 1'.
"""

import yaml

from kubelings.validator import validate_manifest_text

RAY_HETEROGENEOUS_MANIFEST = """
apiVersion: ray.io/v1
kind: RayCluster
metadata:
  name: ray-cluster-heterogeneous
spec:
  headGroupSpec:
    rayStartParams:
      dashboard-host: '0.0.0.0'
    template:
      spec:
        containers:
          - name: ray-head
            image: rayproject/ray:2.35.0
  workerGroupSpecs:
    - groupName: ???
      replicas: 0
      minReplicas: 0
      maxReplicas: 0
      template:
        spec:
          containers:
            - name: ray-cpu-worker
              image: rayproject/ray:2.35.0
"""


def verify():
    passed, errors = validate_manifest_text(RAY_HETEROGENEOUS_MANIFEST, "ray02")
    assert passed, f"Heterogeneous RayCluster validation failed: {errors}"

    manifest = yaml.safe_load(RAY_HETEROGENEOUS_MANIFEST)
    worker_groups = manifest["spec"]["workerGroupSpecs"]
    assert len(worker_groups) == 2, "Must have exactly 2 worker groups"

    cpu_group = next((g for g in worker_groups if g.get("groupName") == "cpu-workers"), None)
    assert cpu_group is not None, "Missing 'cpu-workers' group"
    assert cpu_group["replicas"] == 2
    assert cpu_group["minReplicas"] == 2
    assert cpu_group["maxReplicas"] == 10

    gpu_group = next((g for g in worker_groups if g.get("groupName") == "gpu-workers"), None)
    assert gpu_group is not None, "Missing 'gpu-workers' group"
    assert gpu_group["replicas"] == 1
    assert gpu_group["minReplicas"] == 0
    assert gpu_group["maxReplicas"] == 4

    gpu_container = gpu_group["template"]["spec"]["containers"][0]
    assert (
        gpu_container["resources"]["limits"]["nvidia.com/gpu"] == 1
        or gpu_container["resources"]["limits"]["nvidia.com/gpu"] == "1"
    )

    print("✓ ray02 passed!")


if __name__ == "__main__":
    verify()

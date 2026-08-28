"""
Exercise: exercises/24_kuberay_ml/ray02.py
Topic: Heterogeneous Worker Pools & Autoscaling

Context & Why:
Real-world machine learning and LLM fine-tuning pipelines require heterogeneous compute tiers:
- CPU nodes for data ingestion, preprocessing, tokenization, and batching.
- GPU nodes (e.g. NVIDIA A100/H100) for tensor computations and backward passes.

Running preprocessing on expensive GPU nodes leads to massive cloud budget waste. KubeRay solves
this via heterogeneous worker groups (`spec.workerGroupSpecs`):
- `cpu-workers`: High `maxReplicas` (e.g. 10) to scale with dataset size during preprocessing.
- `gpu-workers`: Dedicated accelerator limit (`nvidia.com/gpu: 1`), with `minReplicas: 0` so expensive
  GPU nodes scale down to zero when no active training job requires GPU acceleration.

Task:
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

# TODO: Configure the RayCluster manifest with heterogeneous worker groups separating CPU worker pools from GPU-accelerated worker pools with autoscaling bounds.
# WHY: Heterogeneous worker pools optimize cloud compute costs and performance by provisioning specialized hardware (CPUs vs GPUs) only for the specific pipeline stages that require them, preventing idle GPU waste during preprocessing.
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

"""
Exercise: exercises/26_hardware_acceleration_dra/accel01.py
Topic: NVIDIA Multi-Instance GPU (MIG) Slicing & Partitioning

Instructions:
Fix the Pod manifest below to schedule an inference workload on an NVIDIA A100 GPU sliced with Multi-Instance GPU (MIG):
1. Set 'apiVersion' to 'v1' and 'kind' to 'Pod'.
2. Set 'metadata.name' to 'mig-inference-pod'.
3. In 'spec.nodeSelector', constrain scheduling to nodes with 'nvidia.com/gpu.product: NVIDIA-A100-SXM4-80GB'.
4. In 'spec.containers', define container 'inference-worker' using image 'nvcr.io/nvidia/tritonserver:24.01-py3'.
5. Under 'resources.limits' and 'resources.requests', allocate 1 slice of 'nvidia.com/mig-3g.40gb: 1'.
6. Under 'env', set 'NVIDIA_VISIBLE_DEVICES' to 'all'.
"""

import yaml

from kubelings.validator import validate_manifest_text

MIG_MANIFEST = """
apiVersion: ???
kind: ???
metadata:
  name: ???
spec:
  nodeSelector:
    nvidia.com/gpu.product: ???
  containers:
    - name: ???
      image: ???
      resources:
        limits:
          nvidia.com/mig-3g.40gb: 0
        requests:
          nvidia.com/mig-3g.40gb: 0
      env:
        - name: ???
          value: ???
"""


def verify():
    passed, errors = validate_manifest_text(MIG_MANIFEST, "accel01")
    assert passed, f"MIG Pod manifest validation failed: {errors}"

    manifest = yaml.safe_load(MIG_MANIFEST)
    assert manifest["metadata"]["name"] == "mig-inference-pod", (
        "Pod name must be 'mig-inference-pod'"
    )

    node_sel = manifest["spec"].get("nodeSelector", {})
    assert node_sel.get("nvidia.com/gpu.product") == "NVIDIA-A100-SXM4-80GB", (
        "nodeSelector must specify 'nvidia.com/gpu.product: NVIDIA-A100-SXM4-80GB'"
    )

    container = manifest["spec"]["containers"][0]
    assert container["name"] == "inference-worker", "Container name must be 'inference-worker'"
    assert container["image"] == "nvcr.io/nvidia/tritonserver:24.01-py3", (
        "Container image must be 'nvcr.io/nvidia/tritonserver:24.01-py3'"
    )

    limits = container["resources"]["limits"]
    requests = container["resources"]["requests"]
    assert str(limits.get("nvidia.com/mig-3g.40gb")) == "1", (
        "Resource limit nvidia.com/mig-3g.40gb must be 1"
    )
    assert str(requests.get("nvidia.com/mig-3g.40gb")) == "1", (
        "Resource request nvidia.com/mig-3g.40gb must be 1"
    )

    env_vars = {e["name"]: e["value"] for e in container.get("env", []) if isinstance(e, dict)}
    assert env_vars.get("NVIDIA_VISIBLE_DEVICES") == "all", "NVIDIA_VISIBLE_DEVICES must be 'all'"

    print("✓ accel01 passed!")


if __name__ == "__main__":
    verify()

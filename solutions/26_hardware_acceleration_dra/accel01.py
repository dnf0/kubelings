"""
Solution: solutions/26_hardware_acceleration_dra/accel01.py
Topic: NVIDIA Multi-Instance GPU (MIG) Slicing & Partitioning
"""

import yaml

from kubelings.validator import validate_manifest_text

MIG_MANIFEST = """
apiVersion: v1
kind: Pod
metadata:
  name: mig-inference-pod
spec:
  nodeSelector:
    nvidia.com/gpu.product: NVIDIA-A100-SXM4-80GB
  containers:
    - name: inference-worker
      image: nvcr.io/nvidia/tritonserver:24.01-py3
      resources:
        limits:
          nvidia.com/mig-3g.40gb: 1
        requests:
          nvidia.com/mig-3g.40gb: 1
      env:
        - name: NVIDIA_VISIBLE_DEVICES
          value: "all"
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

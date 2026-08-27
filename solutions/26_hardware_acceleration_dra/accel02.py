"""
Solution: solutions/26_hardware_acceleration_dra/accel02.py
Topic: Apple Silicon GPU & Metal Performance Shaders (MPS) Acceleration
"""

import yaml

from kubelings.validator import validate_manifest_text

APPLE_GPU_MANIFEST = """
apiVersion: v1
kind: Pod
metadata:
  name: apple-silicon-mlx-pod
spec:
  nodeSelector:
    kubernetes.io/arch: arm64
  containers:
    - name: local-llm
      image: python:3.11-slim
      resources:
        limits:
          apple.com/gpu: 1
      env:
        - name: PYTORCH_ENABLE_MPS_FALLBACK
          value: "1"
        - name: DEVICE
          value: "mps"
"""


def verify():
    passed, errors = validate_manifest_text(APPLE_GPU_MANIFEST, "accel02")
    assert passed, f"Apple Silicon GPU Pod manifest validation failed: {errors}"

    manifest = yaml.safe_load(APPLE_GPU_MANIFEST)
    assert manifest["metadata"]["name"] == "apple-silicon-mlx-pod", (
        "Pod name must be 'apple-silicon-mlx-pod'"
    )

    node_sel = manifest["spec"].get("nodeSelector", {})
    assert node_sel.get("kubernetes.io/arch") == "arm64", (
        "nodeSelector must specify 'kubernetes.io/arch: arm64'"
    )

    container = manifest["spec"]["containers"][0]
    assert container["name"] == "local-llm", "Container name must be 'local-llm'"
    assert container["image"] == "python:3.11-slim", "Container image must be 'python:3.11-slim'"

    limits = container["resources"]["limits"]
    assert str(limits.get("apple.com/gpu")) == "1", "Resource limit apple.com/gpu must be 1"

    env_vars = {e["name"]: e["value"] for e in container.get("env", []) if isinstance(e, dict)}
    assert env_vars.get("PYTORCH_ENABLE_MPS_FALLBACK") == "1", (
        "PYTORCH_ENABLE_MPS_FALLBACK must be '1'"
    )
    assert env_vars.get("DEVICE") == "mps", "DEVICE must be 'mps'"

    print("✓ accel02 passed!")


if __name__ == "__main__":
    verify()

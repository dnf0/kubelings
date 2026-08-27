"""
Exercise: exercises/26_hardware_acceleration_dra/accel02.py
Topic: Apple Silicon GPU & Metal Performance Shaders (MPS) Acceleration

Instructions:
Fix the Pod manifest below to enable Apple Silicon GPU acceleration and PyTorch MPS fallback for local AI development:
1. Set 'apiVersion' to 'v1' and 'kind' to 'Pod'.
2. Set 'metadata.name' to 'apple-silicon-mlx-pod'.
3. In 'spec.nodeSelector', pin the Pod to ARM64 architecture nodes using 'kubernetes.io/arch: arm64'.
4. In 'spec.containers', define container 'local-llm' using image 'python:3.11-slim'.
5. Under 'resources.limits', request 1 Apple GPU with 'apple.com/gpu: 1'.
6. Under 'env', configure MPS fallback by setting 'PYTORCH_ENABLE_MPS_FALLBACK' to '1' and 'DEVICE' to 'mps'.
"""

import yaml

from kubelings.validator import validate_manifest_text

APPLE_GPU_MANIFEST = """
apiVersion: ???
kind: ???
metadata:
  name: ???
spec:
  nodeSelector:
    kubernetes.io/arch: ???
  containers:
    - name: ???
      image: ???
      resources:
        limits:
          apple.com/gpu: 0
      env:
        - name: PYTORCH_ENABLE_MPS_FALLBACK
          value: "0"
        - name: DEVICE
          value: "cpu"
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

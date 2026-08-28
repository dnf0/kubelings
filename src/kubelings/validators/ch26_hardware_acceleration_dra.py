"""
Validators for Chapter 26: Hardware Acceleration: NVIDIA MIG, Apple Silicon GPU & DRA
"""

from typing import Any

from kubelings.validator import validate_manifest_text
from kubelings.validators import register_validator


@register_validator("accel01")
def validate_accel01(manifest: Any, raw_yaml: str = "") -> None:
    passed, errors = validate_manifest_text(raw_yaml, "accel01")
    assert passed, f"MIG Pod manifest validation failed: {errors}"
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


@register_validator("accel02")
def validate_accel02(manifest: Any, raw_yaml: str = "") -> None:
    passed, errors = validate_manifest_text(raw_yaml, "accel02")
    assert passed, f"Apple Silicon GPU Pod manifest validation failed: {errors}"
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


@register_validator("accel03")
def validate_accel03(manifest: Any, raw_yaml: str = "") -> None:
    passed, errors = validate_manifest_text(raw_yaml, "accel03")
    assert passed, f"DRA manifest validation failed: {errors}"
    docs = manifest if isinstance(manifest, list) else [manifest]
    assert len(docs) == 2, (
        "Manifest must define exactly 2 documents (ResourceClaimTemplate and Pod)"
    )
    template_doc = next((d for d in docs if d.get("kind") == "ResourceClaimTemplate"), None)
    assert template_doc is not None, "Missing ResourceClaimTemplate document"
    assert template_doc["metadata"]["name"] == "gpu-dra-claim-template", (
        "ResourceClaimTemplate name must be 'gpu-dra-claim-template'"
    )
    req = template_doc["spec"]["spec"]["devices"]["requests"][0]
    assert req["name"] == "dedicated-gpu", "Device request name must be 'dedicated-gpu'"
    assert req["deviceClassName"] == "gpu.example.com", "deviceClassName must be 'gpu.example.com'"
    assert req["count"] == 1, "Device count must be 1"
    pod_doc = next((d for d in docs if d.get("kind") == "Pod"), None)
    assert pod_doc is not None, "Missing Pod document"
    assert pod_doc["metadata"]["name"] == "dra-workload-pod", "Pod name must be 'dra-workload-pod'"
    pod_claims = pod_doc["spec"]["resourceClaims"]
    assert pod_claims[0]["name"] == "gpu-claim", "resourceClaim name must be 'gpu-claim'"
    assert pod_claims[0]["resourceClaimTemplateName"] == "gpu-dra-claim-template", (
        "resourceClaimTemplateName must be 'gpu-dra-claim-template'"
    )
    container = pod_doc["spec"]["containers"][0]
    assert container["name"] == "workload", "Container name must be 'workload'"
    assert container["image"] == "ubuntu:22.04", "Container image must be 'ubuntu:22.04'"
    c_claims = container["resources"]["claims"]
    assert c_claims[0]["name"] == "gpu-claim", "Container resource claim name must be 'gpu-claim'"


@register_validator("accel04")
def validate_accel04(manifest: Any, raw_yaml: str = "") -> None:
    passed, errors = validate_manifest_text(raw_yaml, "accel04")
    assert passed, f"vLLM Deployment manifest validation failed: {errors}"
    assert manifest["kind"] == "Deployment", "Kind must be 'Deployment'"
    assert manifest["metadata"]["name"] == "vllm-openai-server", "Name must be 'vllm-openai-server'"
    assert manifest["spec"]["replicas"] == 1, "Replicas must be 1"
    match_labels = manifest["spec"]["selector"]["matchLabels"]
    assert match_labels.get("app") == "vllm-server", (
        "Selector matchLabels must include 'app: vllm-server'"
    )
    template_labels = manifest["spec"]["template"]["metadata"]["labels"]
    assert template_labels.get("app") == "vllm-server", (
        "Template labels must include 'app: vllm-server'"
    )
    c = manifest["spec"]["template"]["spec"]["containers"][0]
    assert c["name"] == "vllm", "Container name must be 'vllm'"
    assert c["image"] == "vllm/vllm-openai:latest", "Image must be 'vllm/vllm-openai:latest'"
    args = c["args"]
    assert "--model" in args and "meta-llama/Llama-3-8B-Instruct" in args, (
        "Args must specify model 'meta-llama/Llama-3-8B-Instruct'"
    )
    assert "--gpu-memory-utilization" in args and "0.90" in args, (
        "Args must specify '--gpu-memory-utilization 0.90'"
    )
    ports = c["ports"]
    assert any((p.get("containerPort") == 8000 for p in ports)), (
        "Container port 8000 must be defined"
    )
    limits = c["resources"]["limits"]
    assert str(limits.get("nvidia.com/gpu")) == "1", "Resource limit nvidia.com/gpu must be 1"
    probe = c["readinessProbe"]["httpGet"]
    assert probe.get("path") == "/health", "Readiness probe path must be '/health'"
    assert str(probe.get("port")) in ("8000", "http"), "Readiness probe port must be 8000 or http"
    mount = c["volumeMounts"][0]
    assert mount["mountPath"] == "/root/.cache/huggingface", (
        "Volume mountPath must be '/root/.cache/huggingface'"
    )
    vol = manifest["spec"]["template"]["spec"]["volumes"][0]
    assert vol["persistentVolumeClaim"]["claimName"] == "model-weights-pvc", (
        "PVC claimName must be 'model-weights-pvc'"
    )

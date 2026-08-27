"""
Solution: solutions/26_hardware_acceleration_dra/accel04.py
Topic: High-Throughput Production LLM Inference Server with vLLM
"""

import yaml

from kubelings.validator import validate_manifest_text

VLLM_MANIFEST = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vllm-openai-server
spec:
  replicas: 1
  selector:
    matchLabels:
      app: vllm-server
  template:
    metadata:
      labels:
        app: vllm-server
    spec:
      containers:
        - name: vllm
          image: vllm/vllm-openai:latest
          args:
            - "--model"
            - "meta-llama/Llama-3-8B-Instruct"
            - "--gpu-memory-utilization"
            - "0.90"
            - "--port"
            - "8000"
          ports:
            - containerPort: 8000
              name: http
          resources:
            limits:
              nvidia.com/gpu: 1
          readinessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 30
          volumeMounts:
            - name: model-cache
              mountPath: /root/.cache/huggingface
      volumes:
        - name: model-cache
          persistentVolumeClaim:
            claimName: model-weights-pvc
"""


def verify():
    passed, errors = validate_manifest_text(VLLM_MANIFEST, "accel04")
    assert passed, f"vLLM Deployment manifest validation failed: {errors}"

    manifest = yaml.safe_load(VLLM_MANIFEST)
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
    assert any(p.get("containerPort") == 8000 for p in ports), "Container port 8000 must be defined"

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

    print("✓ accel04 passed!")


if __name__ == "__main__":
    verify()

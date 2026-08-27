import importlib.util
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from kubelings.validator import validate_manifest_text


def _load_module_from_path(file_path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(file_path.stem, file_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_ray01_raycluster_validation():
    valid_yaml = """
apiVersion: ray.io/v1
kind: RayCluster
metadata:
  name: ray-cluster-ml
spec:
  rayVersion: '2.35.0'
  headGroupSpec:
    rayStartParams:
      dashboard-host: '0.0.0.0'
      block: 'true'
    template:
      spec:
        containers:
          - name: ray-head
            image: rayproject/ray:2.35.0
            ports:
              - containerPort: 6379
                name: gcs
              - containerPort: 8265
                name: dashboard
  workerGroupSpecs:
    - groupName: worker-group
      replicas: 2
      minReplicas: 1
      maxReplicas: 5
      template:
        spec:
          containers:
            - name: ray-worker
              image: rayproject/ray:2.35.0
              resources:
                limits:
                  cpu: "2"
                  memory: 4Gi
"""
    passed, errors = validate_manifest_text(valid_yaml, "ray01")
    assert passed, f"Expected valid RayCluster to pass, got: {errors}"


def test_ray02_heterogeneous_pools():
    valid_yaml = """
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
    - groupName: cpu-workers
      replicas: 2
      minReplicas: 2
      maxReplicas: 10
      template:
        spec:
          containers:
            - name: ray-cpu-worker
              image: rayproject/ray:2.35.0
    - groupName: gpu-workers
      replicas: 1
      minReplicas: 0
      maxReplicas: 4
      template:
        spec:
          containers:
            - name: ray-gpu-worker
              image: rayproject/ray:2.35.0-gpu
              resources:
                limits:
                  nvidia.com/gpu: 1
"""
    passed, errors = validate_manifest_text(valid_yaml, "ray02")
    assert passed, f"Expected valid heterogeneous RayCluster to pass, got: {errors}"


def test_ray03_rayjob_validation():
    valid_yaml = """
apiVersion: ray.io/v1
kind: RayJob
metadata:
  name: ray-finetune-job
spec:
  entrypoint: python fine_tune.py --epochs 3
  shutdownAfterJobFinishes: true
  ttlSecondsAfterFinished: 300
  rayClusterSpec:
    rayVersion: '2.35.0'
    headGroupSpec:
      rayStartParams:
        dashboard-host: '0.0.0.0'
      template:
        spec:
          containers:
            - name: ray-head
              image: rayproject/ray:2.35.0
"""
    passed, errors = validate_manifest_text(valid_yaml, "ray03")
    assert passed, f"Expected valid RayJob to pass, got: {errors}"


def test_ray04_rayservice_validation():
    valid_yaml = """
apiVersion: ray.io/v1
kind: RayService
metadata:
  name: ray-llm-service
spec:
  serviceUnhealthyThreshold: 300
  rayClusterSpec:
    rayVersion: '2.35.0'
    headGroupSpec:
      rayStartParams:
        dashboard-host: '0.0.0.0'
      template:
        spec:
          containers:
            - name: ray-head
              image: rayproject/ray:2.35.0
  serveConfigV2: |
    applications:
      - name: llm_app
        route_prefix: /v1
        import_path: llm_serve:model
        runtime_env: {}
"""
    passed, errors = validate_manifest_text(valid_yaml, "ray04")
    assert passed, f"Expected valid RayService to pass, got: {errors}"


def test_ray_invalid_manifests():
    # Empty manifest
    passed, errors = validate_manifest_text("", "ray01")
    assert not passed
    assert len(errors) > 0

    # RayCluster missing workerGroupSpecs
    invalid_cluster = """
apiVersion: ray.io/v1
kind: RayCluster
metadata:
  name: bad-cluster
spec:
  headGroupSpec:
    template:
      spec:
        containers:
          - name: ray-head
            image: rayproject/ray:2.35.0
"""
    passed, errors = validate_manifest_text(invalid_cluster, "ray01")
    assert not passed
    assert any("workerGroupSpecs" in err for err in errors)

    # RayJob missing entrypoint
    invalid_job = """
apiVersion: ray.io/v1
kind: RayJob
metadata:
  name: bad-job
spec:
  shutdownAfterJobFinishes: true
  ttlSecondsAfterFinished: 300
"""
    passed, errors = validate_manifest_text(invalid_job, "ray03")
    assert not passed
    assert any("entrypoint" in err for err in errors)

    # RayService missing serveConfigV2
    invalid_service = """
apiVersion: ray.io/v1
kind: RayService
metadata:
  name: bad-service
spec:
  serviceUnhealthyThreshold: 300
"""
    passed, errors = validate_manifest_text(invalid_service, "ray04")
    assert not passed
    assert any("serveConfigV2" in err for err in errors)


@pytest.mark.parametrize("ex_num", ["01", "02", "03", "04"])
def test_chapter_24_solutions_pass(ex_num: str):
    sol_path = Path(f"solutions/24_kuberay_ml/ray{ex_num}.py")
    assert sol_path.exists(), f"Solution file missing: {sol_path}"
    mod = _load_module_from_path(sol_path)
    mod.verify()


@pytest.mark.parametrize("ex_num", ["01", "02", "03", "04"])
def test_chapter_24_starters_fail(ex_num: str):
    ex_path = Path(f"exercises/24_kuberay_ml/ray{ex_num}.py")
    assert ex_path.exists(), f"Exercise file missing: {ex_path}"

    env = os.environ.copy()
    env["PYTHONPATH"] = f"{Path.cwd() / 'src'}:{env.get('PYTHONPATH', '')}".strip(":")
    proc = subprocess.run(
        [sys.executable, str(ex_path)],
        capture_output=True,
        text=True,
        timeout=10,
        env=env,
    )
    assert proc.returncode != 0, f"Starter {ex_path} should fail initially but returned 0."


def test_kueue01_resource_flavor_and_cluster_queue():
    valid_yaml = """
apiVersion: kueue.x-k8s.io/v1beta1
kind: ResourceFlavor
metadata:
  name: default-flavor
---
apiVersion: kueue.x-k8s.io/v1beta1
kind: ClusterQueue
metadata:
  name: cluster-queue-ai
spec:
  cohort: ai-research-cohort
  resourceGroups:
    - coveredResources: ["cpu", "memory", "nvidia.com/gpu"]
      flavors:
        - name: default-flavor
          resources:
            - name: cpu
              nominalQuota: "64"
              borrowingLimit: "32"
            - name: memory
              nominalQuota: 256Gi
            - name: nvidia.com/gpu
              nominalQuota: "8"
              borrowingLimit: "4"
"""
    passed, errors = validate_manifest_text(valid_yaml, "kueue01")
    assert passed, f"Expected valid Kueue ResourceFlavor & ClusterQueue to pass, got: {errors}"


def test_kueue02_local_queue_and_workload():
    valid_yaml = """
apiVersion: kueue.x-k8s.io/v1beta1
kind: LocalQueue
metadata:
  name: team-a-queue
  namespace: team-a
spec:
  clusterQueue: cluster-queue-ai
---
apiVersion: batch/v1
kind: Job
metadata:
  name: train-job
  namespace: team-a
  labels:
    kueue.x-k8s.io/queue-name: team-a-queue
spec:
  suspend: true
  template:
    spec:
      restartPolicy: Never
      containers:
        - name: trainer
          image: pytorch/pytorch:2.2.0-cuda12.1-cudnn8-runtime
"""
    passed, errors = validate_manifest_text(valid_yaml, "kueue02")
    assert passed, f"Expected valid Kueue LocalQueue and suspended Job to pass, got: {errors}"


def test_volcano01_gang_scheduling_job():
    valid_yaml = """
apiVersion: batch.volcano.sh/v1alpha1
kind: Job
metadata:
  name: distributed-training-gang
spec:
  minAvailable: 4
  schedulerName: volcano
  tasks:
    - replicas: 1
      name: master
      template:
        spec:
          restartPolicy: OnFailure
          containers:
            - name: train-master
              image: pytorch/pytorch:2.2.0-cuda12.1-cudnn8-runtime
    - replicas: 3
      name: worker
      template:
        spec:
          restartPolicy: OnFailure
          containers:
            - name: train-worker
              image: pytorch/pytorch:2.2.0-cuda12.1-cudnn8-runtime
"""
    passed, errors = validate_manifest_text(valid_yaml, "volcano01")
    assert passed, f"Expected valid Volcano gang scheduling job to pass, got: {errors}"


def test_volcano02_queue_fairshare():
    valid_yaml = """
apiVersion: scheduling.volcano.sh/v1beta1
kind: Queue
metadata:
  name: ai-research-queue
spec:
  weight: 1
  capability:
    cpu: "64"
    memory: 256Gi
  reclaimable: true
"""
    passed, errors = validate_manifest_text(valid_yaml, "volcano02")
    assert passed, f"Expected valid Volcano Queue to pass, got: {errors}"


def test_kueue_volcano_invalid_manifests():
    # Empty manifest
    passed, errors = validate_manifest_text("", "kueue01")
    assert not passed
    assert len(errors) > 0

    # ClusterQueue missing resourceGroups
    invalid_cluster_queue = """
apiVersion: kueue.x-k8s.io/v1beta1
kind: ClusterQueue
metadata:
  name: bad-cluster-queue
spec:
  cohort: ai-cohort
"""
    passed, errors = validate_manifest_text(invalid_cluster_queue, "kueue01")
    assert not passed
    assert any("resourceGroups" in err for err in errors)

    # LocalQueue missing clusterQueue
    invalid_local_queue = """
apiVersion: kueue.x-k8s.io/v1beta1
kind: LocalQueue
metadata:
  name: bad-local-queue
spec: {}
"""
    passed, errors = validate_manifest_text(invalid_local_queue, "kueue02")
    assert not passed
    assert any("clusterQueue" in err for err in errors)

    # Volcano Job missing minAvailable
    invalid_volcano_job = """
apiVersion: batch.volcano.sh/v1alpha1
kind: Job
metadata:
  name: bad-volcano-job
spec:
  tasks:
    - replicas: 2
      name: worker
      template:
        spec:
          containers:
            - name: worker
              image: ubuntu:22.04
"""
    passed, errors = validate_manifest_text(invalid_volcano_job, "volcano01")
    assert not passed
    assert any("minAvailable" in err for err in errors)

    # Volcano Queue missing weight
    invalid_volcano_queue = """
apiVersion: scheduling.volcano.sh/v1beta1
kind: Queue
metadata:
  name: bad-volcano-queue
spec:
  capability:
    cpu: "32"
"""
    passed, errors = validate_manifest_text(invalid_volcano_queue, "volcano02")
    assert not passed
    assert any("weight" in err for err in errors)


@pytest.mark.parametrize("ex_name", ["kueue01", "kueue02", "volcano01", "volcano02"])
def test_chapter_25_solutions_pass(ex_name: str):
    sol_path = Path(f"solutions/25_batch_kueue_volcano/{ex_name}.py")
    assert sol_path.exists(), f"Solution file missing: {sol_path}"
    mod = _load_module_from_path(sol_path)
    mod.verify()


@pytest.mark.parametrize("ex_name", ["kueue01", "kueue02", "volcano01", "volcano02"])
def test_chapter_25_starters_fail(ex_name: str):
    ex_path = Path(f"exercises/25_batch_kueue_volcano/{ex_name}.py")
    assert ex_path.exists(), f"Exercise file missing: {ex_path}"

    env = os.environ.copy()
    env["PYTHONPATH"] = f"{Path.cwd() / 'src'}:{env.get('PYTHONPATH', '')}".strip(":")
    proc = subprocess.run(
        [sys.executable, str(ex_path)],
        capture_output=True,
        text=True,
        timeout=10,
        env=env,
    )
    assert proc.returncode != 0, f"Starter {ex_path} should fail initially but returned 0."


def test_accel01_nvidia_mig_partitioning():
    valid_yaml = """
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
    passed, errors = validate_manifest_text(valid_yaml, "accel01")
    assert passed, f"Expected valid MIG pod to pass, got: {errors}"


def test_accel02_apple_silicon_gpu():
    valid_yaml = """
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
    passed, errors = validate_manifest_text(valid_yaml, "accel02")
    assert passed, f"Expected valid Apple Silicon GPU pod to pass, got: {errors}"


def test_accel03_dynamic_resource_allocation():
    valid_yaml = """
apiVersion: resource.k8s.io/v1alpha3
kind: ResourceClaimTemplate
metadata:
  name: gpu-dra-claim-template
spec:
  spec:
    devices:
      requests:
        - name: dedicated-gpu
          deviceClassName: gpu.example.com
          count: 1
---
apiVersion: v1
kind: Pod
metadata:
  name: dra-workload-pod
spec:
  resourceClaims:
    - name: gpu-claim
      resourceClaimTemplateName: gpu-dra-claim-template
  containers:
    - name: workload
      image: ubuntu:22.04
      resources:
        claims:
          - name: gpu-claim
"""
    passed, errors = validate_manifest_text(valid_yaml, "accel03")
    assert passed, f"Expected valid DRA claim and pod to pass, got: {errors}"


def test_accel04_vllm_llm_inference():
    valid_yaml = """
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
    passed, errors = validate_manifest_text(valid_yaml, "accel04")
    assert passed, f"Expected valid vLLM deployment to pass, got: {errors}"


def test_accel_invalid_manifests():
    # Empty manifest
    passed, errors = validate_manifest_text("", "accel01")
    assert not passed
    assert len(errors) > 0

    # MIG mismatched requests and limits
    mismatched_mig = """
apiVersion: v1
kind: Pod
metadata:
  name: bad-mig-pod
spec:
  nodeSelector:
    nvidia.com/gpu.product: NVIDIA-A100-SXM4-80GB
  containers:
    - name: worker
      image: nvcr.io/nvidia/tritonserver:24.01-py3
      resources:
        limits:
          nvidia.com/mig-3g.40gb: 1
        requests:
          nvidia.com/mig-1g.10gb: 1
"""
    passed, errors = validate_manifest_text(mismatched_mig, "accel01")
    assert not passed
    assert any(
        "match" in err.lower() or "mismatch" in err.lower() or "mig" in err.lower()
        for err in errors
    )

    # Apple GPU missing arch arm64 or MPS env
    missing_mps = """
apiVersion: v1
kind: Pod
metadata:
  name: bad-apple-pod
spec:
  nodeSelector:
    kubernetes.io/arch: amd64
  containers:
    - name: worker
      image: python:3.11-slim
      resources:
        limits:
          apple.com/gpu: 1
"""
    passed, errors = validate_manifest_text(missing_mps, "accel02")
    assert not passed
    assert any("arm64" in err.lower() or "mps" in err.lower() for err in errors)

    # DRA missing deviceClassName
    invalid_dra = """
apiVersion: resource.k8s.io/v1alpha3
kind: ResourceClaimTemplate
metadata:
  name: bad-dra-template
spec:
  spec:
    devices:
      requests:
        - name: gpu-req
"""
    passed, errors = validate_manifest_text(invalid_dra, "accel03")
    assert not passed
    assert any("deviceClassName" in err or "requests" in err for err in errors)

    # vLLM missing readiness probe
    invalid_vllm = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: bad-vllm
spec:
  replicas: 1
  selector:
    matchLabels:
      app: vllm
  template:
    metadata:
      labels:
        app: vllm
    spec:
      containers:
        - name: vllm
          image: vllm/vllm-openai:latest
          args:
            - "--gpu-memory-utilization"
            - "0.90"
          resources:
            limits:
              nvidia.com/gpu: 1
"""
    passed, errors = validate_manifest_text(invalid_vllm, "accel04")
    assert not passed
    assert any("probe" in err.lower() or "volume" in err.lower() for err in errors)


@pytest.mark.parametrize("ex_name", ["accel01", "accel02", "accel03", "accel04"])
def test_chapter_26_solutions_pass(ex_name: str):
    sol_path = Path(f"solutions/26_hardware_acceleration_dra/{ex_name}.py")
    assert sol_path.exists(), f"Solution file missing: {sol_path}"
    mod = _load_module_from_path(sol_path)
    mod.verify()


@pytest.mark.parametrize("ex_name", ["accel01", "accel02", "accel03", "accel04"])
def test_chapter_26_starters_fail(ex_name: str):
    ex_path = Path(f"exercises/26_hardware_acceleration_dra/{ex_name}.py")
    assert ex_path.exists(), f"Exercise file missing: {ex_path}"

    env = os.environ.copy()
    env["PYTHONPATH"] = f"{Path.cwd() / 'src'}:{env.get('PYTHONPATH', '')}".strip(":")
    proc = subprocess.run(
        [sys.executable, str(ex_path)],
        capture_output=True,
        text=True,
        timeout=10,
        env=env,
    )
    assert proc.returncode != 0, f"Starter {ex_path} should fail initially but returned 0."


def test_chapters_24_26_manifest_registration():
    from kubelings.manifest import get_exercise_by_name, get_manifest

    manifest = get_manifest()
    assert len(manifest.chapters) == 26
    assert len(manifest.all_exercises) == 114

    ch24 = next((c for c in manifest.chapters if c.number == 24), None)
    assert ch24 is not None
    assert ch24.name == "24_kuberay_ml"
    assert len(ch24.exercises) == 4
    for ex_name in ["ray01", "ray02", "ray03", "ray04"]:
        ex = get_exercise_by_name(ex_name)
        assert ex is not None
        assert ex.chapter_name == "24_kuberay_ml"

    ch25 = next((c for c in manifest.chapters if c.number == 25), None)
    assert ch25 is not None
    assert ch25.name == "25_batch_kueue_volcano"
    assert len(ch25.exercises) == 4
    for ex_name in ["kueue01", "kueue02", "volcano01", "volcano02"]:
        ex = get_exercise_by_name(ex_name)
        assert ex is not None
        assert ex.chapter_name == "25_batch_kueue_volcano"

    ch26 = next((c for c in manifest.chapters if c.number == 26), None)
    assert ch26 is not None
    assert ch26.name == "26_hardware_acceleration_dra"
    assert len(ch26.exercises) == 4
    for ex_name in ["accel01", "accel02", "accel03", "accel04"]:
        ex = get_exercise_by_name(ex_name)
        assert ex is not None
        assert ex.chapter_name == "26_hardware_acceleration_dra"

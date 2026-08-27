# AI & ML Platform Engineering Curriculum Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expand Kubelings to 26 chapters and 114 exercises (+12 exercises) with Tier 6: AI & ML Platform Engineering, covering KubeRay, Kueue & Volcano batch scheduling, NVIDIA MIG slicing, Apple Silicon GPU & Metal acceleration, and Dynamic Resource Allocation (DRA).

**Architecture:** 
- In-memory schema and behavioral evaluators in `src/kubelings/validator.py` validate manifests offline in `< 15ms` without requiring physical GPU hardware or cloud CRDs.
- Chapter 24 introduces KubeRay (`ray.io/v1` `RayCluster`, `RayJob`, `RayService`, heterogeneous worker pools).
- Chapter 25 covers AI batch queueing & gang scheduling (`kueue.x-k8s.io/v1beta1`, `batch.volcano.sh/v1alpha1` `minAvailable` deadlocks prevention).
- Chapter 26 covers hardware acceleration: NVIDIA MIG slicing (`nvidia.com/mig-3g.40gb`), Apple Silicon GPU & MPS environment (`apple.com/gpu`), Dynamic Resource Allocation (`resource.k8s.io/v1alpha3` / `v1beta1`), and production LLM serving (vLLM / Ollama).
- Manifest and curriculum expand to 26 chapters with 114 starter exercises and 114 passing reference solutions.

**Tech Stack:** Python 3.10+, Typer, Rich, Pytest, Ruff, Pyright, Hatchling.

---

### Task 1: Chapter 24 — Distributed AI & ML with KubeRay (`24_kuberay_ml`)

**Files:**
- Create: `exercises/24_kuberay_ml/ray01.py` to `ray04.py`
- Create: `solutions/24_kuberay_ml/ray01.py` to `ray04.py`
- Modify: `src/kubelings/validator.py`
- Create: `tests/test_chapters_24_26.py`

- [ ] **Step 1: Write the failing tests for Chapter 24 in `tests/test_chapters_24_26.py`**

```python
# tests/test_chapters_24_26.py
import pytest
from kubelings.validator import validate_manifest_text


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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_chapters_24_26.py -v`  
Expected: FAIL

- [ ] **Step 3: Implement Chapter 24 schema validator in `src/kubelings/validator.py`**

Add `ray.io/v1` validation logic for `RayCluster`, `RayJob`, and `RayService`.

- [ ] **Step 4: Create starter exercises and reference solutions for Chapter 24**

Create:
- `exercises/24_kuberay_ml/ray01.py` to `ray04.py` (broken starter manifests with clear docstrings and hints)
- `solutions/24_kuberay_ml/ray01.py` to `ray04.py` (working reference solutions)

- [ ] **Step 5: Run tests and verify Chapter 24 passes**

Run: `uv run pytest tests/test_chapters_24_26.py -v`  
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add exercises/24_kuberay_ml/ solutions/24_kuberay_ml/ src/kubelings/validator.py tests/test_chapters_24_26.py
git commit --no-gpg-sign -m "feat(curriculum): implement Chapter 24 (Distributed ML with KubeRay)"
```

---

### Task 2: Chapter 25 — AI Batch Scheduling with Kueue & Volcano (`25_batch_kueue_volcano`)

**Files:**
- Create: `exercises/25_batch_kueue_volcano/kueue01.py` to `kueue02.py`
- Create: `exercises/25_batch_kueue_volcano/volcano01.py` to `volcano02.py`
- Create: `solutions/25_batch_kueue_volcano/kueue01.py` to `kueue02.py`
- Create: `solutions/25_batch_kueue_volcano/volcano01.py` to `volcano02.py`
- Modify: `src/kubelings/validator.py`
- Modify: `tests/test_chapters_24_26.py`

- [ ] **Step 1: Write failing tests for Chapter 25 in `tests/test_chapters_24_26.py`**

```python
def test_kueue01_queues_validation():
    valid_yaml = """
apiVersion: kueue.x-k8s.io/v1beta1
kind: ClusterQueue
metadata:
  name: cluster-queue-team-a
spec:
  cohort: team-cohort
  resourceGroups:
    - coveredResources: ["cpu", "memory"]
      flavors:
        - name: default-flavor
          resources:
            - name: cpu
              nominalQuota: "100"
            - name: memory
              nominalQuota: 500Gi
---
apiVersion: kueue.x-k8s.io/v1beta1
kind: LocalQueue
metadata:
  name: user-queue
  namespace: team-a
spec:
  clusterQueue: cluster-queue-team-a
"""
    passed, errors = validate_manifest_text(valid_yaml, "kueue01")
    assert passed, f"Expected valid Kueue queues to pass, got: {errors}"


def test_kueue02_priority_preemption():
    valid_yaml = """
apiVersion: kueue.x-k8s.io/v1beta1
kind: WorkloadPriorityClass
metadata:
  name: high-priority-training
value: 10000
description: "High priority model training workloads"
---
apiVersion: kueue.x-k8s.io/v1beta1
kind: ClusterQueue
metadata:
  name: preemption-queue
spec:
  preemption:
    reclaimWithinCohort: LowerPriority
    borrowWithinCohort:
      policy: LowerPriority
    withinClusterQueue: LowerPriority
"""
    passed, errors = validate_manifest_text(valid_yaml, "kueue02")
    assert passed, f"Expected valid priority preemption to pass, got: {errors}"


def test_volcano01_gang_scheduling():
    valid_yaml = """
apiVersion: batch.volcano.sh/v1alpha1
kind: Job
metadata:
  name: pytorch-ddp-gang
spec:
  minAvailable: 4
  schedulerName: volcano
  plugins:
    env: []
    svc: []
  tasks:
    - replicas: 1
      name: master
      template:
        spec:
          restartPolicy: OnFailure
          containers:
            - name: pytorch
              image: pytorch/pytorch:2.2.0-cuda12.1-cudnn8-runtime
    - replicas: 3
      name: worker
      template:
        spec:
          restartPolicy: OnFailure
          containers:
            - name: pytorch
              image: pytorch/pytorch:2.2.0-cuda12.1-cudnn8-runtime
"""
    passed, errors = validate_manifest_text(valid_yaml, "volcano01")
    assert passed, f"Expected valid Volcano gang scheduling job to pass, got: {errors}"


def test_volcano02_queue_weight():
    valid_yaml = """
apiVersion: batch.volcano.sh/v1alpha1
kind: Queue
metadata:
  name: ml-research-queue
spec:
  weight: 60
  capability:
    cpu: "64"
    memory: 256Gi
  reclaimable: true
"""
    passed, errors = validate_manifest_text(valid_yaml, "volcano02")
    assert passed, f"Expected valid Volcano Queue to pass, got: {errors}"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_chapters_24_26.py -k "kueue or volcano" -v`  
Expected: FAIL

- [ ] **Step 3: Implement Chapter 25 schema validator in `src/kubelings/validator.py`**

Add `kueue.x-k8s.io/v1beta1` (`ClusterQueue`, `LocalQueue`, `WorkloadPriorityClass`) and `batch.volcano.sh/v1alpha1` (`Job`, `Queue`) validation logic.

- [ ] **Step 4: Create starter exercises and reference solutions for Chapter 25**

Create:
- `exercises/25_batch_kueue_volcano/kueue01.py`, `kueue02.py`, `volcano01.py`, `volcano02.py`
- `solutions/25_batch_kueue_volcano/kueue01.py`, `kueue02.py`, `volcano01.py`, `volcano02.py`

- [ ] **Step 5: Run tests and verify Chapter 25 passes**

Run: `uv run pytest tests/test_chapters_24_26.py -v`  
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add exercises/25_batch_kueue_volcano/ solutions/25_batch_kueue_volcano/ src/kubelings/validator.py tests/test_chapters_24_26.py
git commit --no-gpg-sign -m "feat(curriculum): implement Chapter 25 (AI Batch Scheduling with Kueue & Volcano)"
```

---

### Task 3: Chapter 26 — Hardware Acceleration, Apple Silicon & DRA (`26_hardware_acceleration_dra`)

**Files:**
- Create: `exercises/26_hardware_acceleration_dra/accel01.py` to `accel04.py`
- Create: `solutions/26_hardware_acceleration_dra/accel01.py` to `accel04.py`
- Modify: `src/kubelings/validator.py`
- Modify: `tests/test_chapters_24_26.py`

- [ ] **Step 1: Write failing tests for Chapter 26 in `tests/test_chapters_24_26.py`**

```python
def test_accel01_mig_slicing():
    valid_yaml = """
apiVersion: v1
kind: Pod
metadata:
  name: mig-inference-pod
spec:
  containers:
    - name: inference-worker
      image: nvcr.io/nvidia/tritonserver:24.01-py3
      resources:
        limits:
          nvidia.com/mig-3g.40gb: 1
      env:
        - name: NVIDIA_VISIBLE_DEVICES
          value: "all"
"""
    passed, errors = validate_manifest_text(valid_yaml, "accel01")
    assert passed, f"Expected valid MIG pod to pass, got: {errors}"


def test_accel02_apple_silicon_mps():
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


def test_accel03_dra_resource_claims():
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


def test_accel04_production_vllm():
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_chapters_24_26.py -k "accel" -v`  
Expected: FAIL

- [ ] **Step 3: Implement Chapter 26 schema validator in `src/kubelings/validator.py`**

Add MIG, Apple Silicon GPU / MPS, DRA `resource.k8s.io` claim, and vLLM server validation logic.

- [ ] **Step 4: Create starter exercises and reference solutions for Chapter 26**

Create:
- `exercises/26_hardware_acceleration_dra/accel01.py` to `accel04.py`
- `solutions/26_hardware_acceleration_dra/accel01.py` to `accel04.py`

- [ ] **Step 5: Run tests and verify Chapter 26 passes**

Run: `uv run pytest tests/test_chapters_24_26.py -v`  
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add exercises/26_hardware_acceleration_dra/ solutions/26_hardware_acceleration_dra/ src/kubelings/validator.py tests/test_chapters_24_26.py
git commit --no-gpg-sign -m "feat(curriculum): implement Chapter 26 (Hardware Acceleration, Apple GPU & DRA)"
```

---

### Task 4: Manifest Registration, Test Matrix Expansion & Documentation Updates

**Files:**
- Modify: `src/kubelings/manifest.py`
- Modify: `src/kubelings/tour.py`
- Modify: `tests/test_manifest.py`
- Modify: `tests/test_cli.py`
- Modify: `tests/test_cli_json.py`
- Modify: `tests/test_tour.py`
- Modify: `tests/test_solutions_and_exercises.py`
- Modify: `docs/syllabus.md`
- Modify: `docs/onboarding-guide.md`
- Modify: `README.md`
- Modify: `docs/index.md`
- Modify: `docs/getting-started.md`
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Update `src/kubelings/manifest.py`**
  - Register Chapter 24 (`24_kuberay_ml`, 4 exercises).
  - Register Chapter 25 (`25_batch_kueue_volcano`, 4 exercises).
  - Register Chapter 26 (`26_hardware_acceleration_dra`, 4 exercises).
  - Total chapters = 26, total exercises = 114.

- [ ] **Step 2: Update `src/kubelings/tour.py` and test suites**
  - Update tour step 5 syllabus summary to reflect 26 chapters / 114 exercises.
  - Update `tests/test_manifest.py`, `tests/test_cli.py`, `tests/test_cli_json.py`, and `tests/test_tour.py` assertions.

- [ ] **Step 3: Update documentation and syllabus tables**
  - Update `docs/syllabus.md` with full Tier 6 table.
  - Update `docs/onboarding-guide.md`, `README.md`, `docs/index.md`, `docs/getting-started.md`, and `CHANGELOG.md`.

- [ ] **Step 4: Run full end-to-end verification suite**
  - `uv run pytest` (all tests passing)
  - `make vscode-test` (all extension tests passing)
  - `uv run ruff check .`
  - `uv run ruff format --check .`
  - `uv run pyright`
  - `uv run mkdocs build --strict`
  - `uvx --from graphifyy graphify update .`

- [ ] **Step 5: Commit**

```bash
git add src/ tests/ docs/ README.md CHANGELOG.md
git commit --no-gpg-sign -m "feat(curriculum): register Chapters 24-26 and update syllabus documentation"
```

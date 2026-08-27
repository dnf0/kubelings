# Design Specification: AI & ML Platform Engineering Curriculum (Chapters 24–26)

**Date:** 2026-08-27  
**Status:** Approved  
**Author:** AI Assistant & Pair Programmer  
**Target Version:** Kubelings v0.6.0  

---

## 1. Executive Summary

As Kubernetes cements its role as the de facto operating system for Artificial Intelligence and Machine Learning workloads, platform engineers need hands-on mastery of distributed training orchestration, batch queueing, gang scheduling, and hardware acceleration.

This specification defines **Tier 6: AI & ML Platform Engineering** for Kubelings, expanding the curriculum from 23 chapters / 102 exercises to **26 chapters and 114 interactive micro-exercises** (+12 exercises). 

The expansion covers:
1. **Chapter 24 (`24_kuberay_ml`)**: Distributed ML training, heterogeneous worker pools, batch fine-tuning (`RayJob`), and production serving (`RayService`) with KubeRay.
2. **Chapter 25 (`25_batch_kueue_volcano`)**: Advanced AI batch scheduling, quota management & cohort borrowing (`Kueue`), and gang scheduling to prevent distributed deadlocks (`Volcano`).
3. **Chapter 26 (`26_hardware_acceleration_dra`)**: Hardware acceleration architectures across NVIDIA Multi-Instance GPU (MIG) slicing, Apple Silicon GPU & Metal acceleration for local workstations, next-gen Dynamic Resource Allocation (DRA), and production LLM inference serving (vLLM / Ollama).

All exercises run in `< 15ms` using in-memory schema evaluators without requiring physical GPUs, expensive cloud clusters, or specialized hardware.

---

## 2. Curriculum Architecture & Exercises

```
+---------------------------------------------------------------------------------------------------+
|                                   KUBELINGS 6-TIER ROADMAP                                        |
+---------------------------------------------------------------------------------------------------+
| Tier 1: Core Essentials       | Ch 01 - 06 (Pods, Controllers, Config, Storage, Services, Ingress)|
| Tier 2: Operations & Admin    | Ch 07 - 10 (Scheduling, RBAC, NetworkPolicies, Probes)           |
| Tier 3: Production & Scaling  | Ch 11 - 13 (Autoscaling, Operators/CRDs, Troubleshooting)        |
| Tier 4: GitOps & Mesh         | Ch 14 - 18 (ArgoCD, Cilium, Policy-as-Code, vcluster, Webhooks)   |
| Tier 5: Packaging & Platform  | Ch 19 - 23 (Helm, Kustomize, Gateway API, Crossplane, Tetragon)  |
| Tier 6: AI & ML Platforms     | Ch 24 - 26 (KubeRay, Kueue & Volcano, Hardware Accel & DRA)      |  <-- NEW
+---------------------------------------------------------------------------------------------------+
```

### Chapter 24: Distributed AI & ML with KubeRay (`24_kuberay_ml`)
- **`ray01.py` — RayCluster Core Architecture**:
  - **Objective**: Author a `RayCluster` (`ray.io/v1`) with Head Node (dashboard on 8265, GCS on 6379, `rayStartParams` with `block: "true"`) and worker group.
  - **Verification**: Evaluates `headGroupSpec` and `workerGroupSpecs` configurations.
- **`ray02.py` — Heterogeneous Worker Pools & Autoscaler**:
  - **Objective**: Configure multi-worker groups separating CPU data preprocessing workers (`minReplicas: 2`, `maxReplicas: 10`) from GPU training nodes (`minReplicas: 0`, `maxReplicas: 4`).
  - **Verification**: Validates group names, replica bounds, and resource limit declarations.
- **`ray03.py` — RayJob for Distributed Batch Training**:
  - **Objective**: Author a `RayJob` manifest for distributed model fine-tuning with `entrypoint: "python train.py"`, `shutdownAfterJobFinishes: true`, and TTL cleanup.
  - **Verification**: Validates entrypoint command, embedded cluster spec, and lifecycle cleanup parameters.
- **`ray04.py` — RayService for Production LLM Serving**:
  - **Objective**: Author a `RayService` manifest managing multi-model serving deployments under `serveConfigV2` with zero-downtime rolling upgrades and route prefixes.
  - **Verification**: Validates service routing, deployment configuration, and health check endpoints.

---

### Chapter 25: AI Batch Scheduling & Queueing (`25_batch_kueue_volcano`)
- **`kueue01.py` — Kueue LocalQueue & ClusterQueue Quotas**:
  - **Objective**: Define a `ClusterQueue` (`kueue.x-k8s.io/v1beta1`) with nominal quotas and cohort sharing, bound to a developer-facing `LocalQueue`.
  - **Verification**: Validates `resourceGroups`, `flavors`, `nominalQuota`, and namespace queue binding.
- **`kueue02.py` — Priority Classes & Fair-Share Preemption**:
  - **Objective**: Configure `WorkloadPriorityClass` and `ClusterQueue` preemption policies (`reclaimWithinCohort: LowerPriority`, `preemptionRule: Workload`) for multi-tenant fairness.
  - **Verification**: Validates priority values and cohort reclamation rules.
- **`volcano01.py` — Volcano Gang Scheduling for Distributed Training**:
  - **Objective**: Define a Volcano `Job` (`batch.volcano.sh/v1alpha1`) with `minAvailable: 4` gang scheduling policy, ensuring all-or-nothing allocation for distributed PyTorch DDP without deadlocks.
  - **Verification**: Validates `minAvailable` invariant matching total task replicas and `plugins.env` configuration.
- **`volcano02.py` — Volcano Queue & Elastic Resource Allocation**:
  - **Objective**: Configure a Volcano `Queue` with weight allocation, capability limits, and elastic pod group task topology.
  - **Verification**: Validates queue weights, CPU/memory capacity limits, and scheduler policy plugins.

---

### Chapter 26: Hardware Acceleration: NVIDIA MIG, Apple Silicon & DRA (`26_hardware_acceleration_dra`)
- **`accel01.py` — NVIDIA Multi-Instance GPU (MIG) Slicing**:
  - **Objective**: Author a pod manifest requesting sliced GPU instances (`nvidia.com/mig-1g.10gb: 1` or `nvidia.com/mig-3g.40gb: 1`) with CUDA environment variable controls.
  - **Verification**: Validates MIG resource syntax, limit consistency, and container environment declarations.
- **`accel02.py` — Apple Silicon GPU & Metal Acceleration**:
  - **Objective**: Author a local development pod leveraging Apple Silicon GPU (`apple.com/gpu: 1`), MPS (Metal Performance Shaders) environment flags (`PYTORCH_ENABLE_MPS_FALLBACK=1`), and MLX / PyTorch runtime mounts.
  - **Verification**: Validates Apple GPU resource requests, MPS fallback configuration, and architecture node selectors (`kubernetes.io/arch: arm64`).
- **`accel03.py` — Dynamic Resource Allocation (DRA) Standard**:
  - **Objective**: Define modern Kubernetes Dynamic Resource Allocation resources using `ResourceClaimTemplate` and `ResourceClaim` (`resource.k8s.io/v1alpha3` or `v1beta1`) for fine-grained device parameter binding.
  - **Verification**: Validates `spec.devices.requests`, driver selectors, and pod `resourceClaims` binding.
- **`accel04.py` — Production High-Throughput LLM Server (vLLM / Ollama)**:
  - **Objective**: Deploy a production-ready LLM inference server with optimized KV cache memory allocation (`--gpu-memory-utilization 0.90`), model storage PVC mount, DRA device claim, and health probes.
  - **Verification**: Validates container startup flags, persistent storage mounts, resource requests, and liveness endpoints.

---

## 3. In-Memory Validation Engine Design

To maintain sub-15ms test times without external dependencies:

```python
def validate_ray_cluster(manifest_dict: dict) -> Tuple[bool, List[str]]:
    # Validates ray.io/v1 RayCluster structure, head node, and worker groups
    ...

def validate_ray_job(manifest_dict: dict) -> Tuple[bool, List[str]]:
    # Validates ray.io/v1 RayJob entrypoint and cleanup rules
    ...

def validate_ray_service(manifest_dict: dict) -> Tuple[bool, List[str]]:
    # Validates ray.io/v1 RayService serveConfigV2 and deployment routes
    ...

def validate_kueue_queue(manifest_dict: dict) -> Tuple[bool, List[str]]:
    # Validates kueue.x-k8s.io/v1beta1 ClusterQueue and LocalQueue
    ...

def validate_volcano_job(manifest_dict: dict) -> Tuple[bool, List[str]]:
    # Validates batch.volcano.sh/v1alpha1 minAvailable gang scheduling invariant
    ...

def validate_hardware_acceleration(manifest_dict: dict) -> Tuple[bool, List[str]]:
    # Validates MIG resources, Apple Silicon MPS environment, and DRA ResourceClaims
    ...
```

The validation engine is integrated directly into `src/kubelings/validator.py` and invoked by the offline runner.

---

## 4. Hardware Simulation Strategy

1. **Offline Mode**: Pure AST and semantic evaluation against exact schema specifications and environment variable contracts.
2. **Cluster / Live Mode (`--cluster`)**: Simulated via node status capacity patching (`kubectl patch node ...`) or KWOK synthetic nodes, enabling learners to test scheduling on local `kind`/`k3d` clusters without physical GPUs.

---

## 5. Implementation Roadmap & Quality Gates

1. **Task 1: Chapter 24 (KubeRay ML)**:
   - 4 starter exercises in `exercises/24_kuberay_ml/`.
   - 4 reference solutions in `solutions/24_kuberay_ml/`.
   - Validator schemas for `ray.io/v1`.
2. **Task 2: Chapter 25 (Batch Scheduling with Kueue & Volcano)**:
   - 4 starter exercises in `exercises/25_batch_kueue_volcano/`.
   - 4 reference solutions in `solutions/25_batch_kueue_volcano/`.
   - Validator schemas for `kueue.x-k8s.io` and `batch.volcano.sh`.
3. **Task 3: Chapter 26 (Hardware Acceleration, Apple GPU & DRA)**:
   - 4 starter exercises in `exercises/26_hardware_acceleration_dra/`.
   - 4 reference solutions in `solutions/26_hardware_acceleration_dra/`.
   - Validator schemas for MIG, Apple MPS, and DRA claims.
4. **Task 4: Manifest Registration, Test Matrix & Documentation**:
   - Register 26 chapters / 114 exercises in `src/kubelings/manifest.py`.
   - Expand `tests/test_chapters_24_26.py`, `tests/test_manifest.py`, and `tests/test_solutions_and_exercises.py`.
   - Update `docs/syllabus.md`, `docs/onboarding-guide.md`, `README.md`, `CHANGELOG.md`, `mkdocs.yml`, and `src/kubelings/tour.py`.

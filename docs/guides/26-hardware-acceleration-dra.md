# Chapter 26: Hardware Acceleration: NVIDIA MIG, Apple Silicon GPU & DRA

<div class="grid cards" markdown>

-   :material-school: **Topic Focus** &bull; NVIDIA MIG Slicing, Apple Silicon GPU / MPS Acceleration, Dynamic Resource Allocation (DRA), and Production vLLM LLM Serving
-   :material-api: **Primary APIs** &bull; `resource.k8s.io/v1alpha3` &bull; `ResourceClaim`, `ResourceClaimTemplate`, `DeviceClass`
-   :material-rocket-launch: [**Launch Playground in Wasm →**](../playground/index.html?chapter=26){ .md-button .md-button--primary }

</div>

---

## 1. Architectural Overview & Control Plane Mechanics

In Kubernetes, **Hardware Acceleration: NVIDIA MIG, Apple Silicon GPU & DRA** is reconciled through declarative state loops managed by the control plane:

```text
┌───────────────────────────┐
    │     Pod Specification     │ ──► References `ResourceClaim`
    └─────────────┬─────────────┘
                  │
                  ▼
    ┌───────────────────────────┐
    │       ResourceClaim       │ ◄── Requests Specific Device Attributes
    │  (DRA: GPU, TPU, FPGA)    │     (e.g., 20GB VRAM, NVLink Mesh)
    └─────────────┬─────────────┘
                  │ Dynamic Driver Allocation
                  ▼
    ┌───────────────────────────┐
    │   DRA Node Driver Plugin  │ ──► Configures Hardware & Binds to Container
    └───────────────────────────┘
```

When resources in this chapter are submitted, the `kube-apiserver` validates the OpenAPI v3 schema, stores state in `etcd`, and triggers the responsible controllers or node daemons to reconcile actual cluster state.

---

## 2. Annotated Production YAML Anatomy & Field Reference

Below is a production-grade declarative manifest demonstrating field definitions and operational patterns:

```yaml
apiVersion: resource.k8s.io/v1alpha3
kind: ResourceClaim
metadata:
  name: gpu-claim
  namespace: default
spec:
  devices:
    requests:
    - name: high-mem-gpu
      deviceClassName: gpu.nvidia.com
      selectors:
      - cel:
          expression: "device.attributes['gpu.nvidia.com'].memory >= 24 * 1024 * 1024 * 1024"
---
apiVersion: v1
kind: Pod
metadata:
  name: dra-accelerated-inference
  namespace: default
spec:
  resourceClaims:
  - name: gpu-resource
    resourceClaimName: gpu-claim
  containers:
  - name: inference-engine
    image: nvidia/cuda:12.4.1-runtime-ubuntu22.04
    command: ["nvidia-smi"]
    resources:
      claims:
      - name: gpu-resource
```

### Key Field Schema Reference

| Field | Type | Description |
| :--- | :--- | :--- |
| `DeviceClass` | `Cluster Resource` | Defines the hardware class and selecting driver (e.g. `gpu.nvidia.com`, `dra.intel.com`). |
| `ResourceClaim` | `Claim Resource` | Requests fine-grained device properties (memory, architecture, interconnects) using CEL expressions. |
| `spec.resourceClaims` | `Pod Spec` | Binds claims to container instances dynamically during scheduling. |

---

## 3. Real-World Architectural Patterns

### NVIDIA Multi-Instance GPU (MIG) Partitioning

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: mig-partitioned-pod
spec:
  containers:
  - name: cuda-task
    image: nvidia/cuda:12.4.1-base-ubuntu22.04
    resources:
      limits:
        nvidia.com/mig-1g.10gb: 1
```

### ResourceClaimTemplate with Stateful Deployment

```yaml
apiVersion: resource.k8s.io/v1alpha3
kind: ResourceClaimTemplate
metadata:
  name: per-pod-gpu-template
spec:
  spec:
    devices:
      requests:
      - name: dedicated-gpu
        deviceClassName: gpu.nvidia.com
```


---

## 4. Production Hardening & Operational Governance

- Use Dynamic Resource Allocation (DRA) for complex hardware constraints rather than static integer extended resources (`nvidia.com/gpu: 1`).
- Leverage NVIDIA MIG to slice large A100/H100 GPUs into isolated compute instances for lightweight inference tasks.
- Enforce resource limits on GPU-enabled namespaces using dedicated quotas.

---

## 5. Failure Modes & Diagnostic Triage Tree

??? failure "`Failed to allocate device for claim`"
    **Root Cause:** No node in cluster has a hardware device satisfying the CEL selector expression.

    **Diagnostic Triage Sequence:**
    1. Inspect claim state: `kubectl describe resourceclaim <name>`
2. Check DRA driver plugin daemonset: `kubectl get pods -n kube-system -l app=nvidia-dra-driver-kubelet-plugin`


---

## 6. Interactive Practice Matrix

Practice concepts from this chapter directly in the interactive WebAssembly sandbox:

| Exercise ID | Challenge Description | Direct Link | Action |
| :--- | :--- | :--- | :--- |
| **`accel01`** | NVIDIA MIG Slicing & Partitioning | [`../playground/index.html?exercise=accel01`](../playground/index.html?exercise=accel01) | [**⚡ Solve in Playground →**](../playground/index.html?exercise=accel01){ .md-button .md-button--primary } |
| **`accel02`** | Apple Silicon GPU & Metal MPS Acceleration | [`../playground/index.html?exercise=accel02`](../playground/index.html?exercise=accel02) | [**⚡ Solve in Playground →**](../playground/index.html?exercise=accel02){ .md-button .md-button--primary } |
| **`accel03`** | Dynamic Resource Allocation (DRA) Standard | [`../playground/index.html?exercise=accel03`](../playground/index.html?exercise=accel03) | [**⚡ Solve in Playground →**](../playground/index.html?exercise=accel03){ .md-button .md-button--primary } |
| **`accel04`** | Production vLLM LLM Inference Server | [`../playground/index.html?exercise=accel04`](../playground/index.html?exercise=accel04) | [**⚡ Solve in Playground →**](../playground/index.html?exercise=accel04){ .md-button .md-button--primary } |

# Chapter 24: Distributed AI & ML Orchestration with KubeRay

<div class="grid cards" markdown>

-   :material-school: **Topic Focus** &bull; RayCluster Architectures, Heterogeneous Worker Pools, RayJob Batch Fine-Tuning, and RayService Serving
-   :material-api: **Primary APIs** &bull; `ray.io/v1` &bull; `RayCluster`, `RayJob`, `RayService`
-   :material-rocket-launch: [**Launch Playground in Wasm →**](../playground/index.html?chapter=24){ .md-button .md-button--primary }

</div>

---

## 1. Architectural Overview & Control Plane Mechanics

In Kubernetes, **Distributed AI & ML Orchestration with KubeRay** is reconciled through declarative state loops managed by the control plane:

```text
┌─────────────────────────────────────────────────────────────┐
│                     RayCluster Topology                     │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                  Ray Head Node Pod                    │  │
│  │  (GCS Metadata Store, Dashboard, Global Scheduler)   │  │
│  └──────────────────────────┬────────────────────────────┘  │
│                             │ Distributed Tasks & Actors    │
│              ┌──────────────┴──────────────┐                │
│              ▼                             ▼                │
│  ┌───────────────────────┐     ┌───────────────────────┐    │
│  │   Ray Worker Pod 1    │     │   Ray Worker Pod 2    │    │
│  │   (GPU Worker Group)  │     │   (CPU Worker Group)  │    │
│  └───────────────────────┘     └───────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

When resources in this chapter are submitted, the `kube-apiserver` validates the OpenAPI v3 schema, stores state in `etcd`, and triggers the responsible controllers or node daemons to reconcile actual cluster state.

---

## 2. Annotated Production YAML Anatomy & Field Reference

Below is a production-grade declarative manifest demonstrating field definitions and operational patterns:

```yaml
apiVersion: ray.io/v1
kind: RayCluster
metadata:
  name: distributed-training-cluster
  namespace: ml-workloads
spec:
  rayVersion: "2.35.0"
  headGroupSpec:
    rayStartParams:
      dashboard-host: "0.0.0.0"
    template:
      spec:
        containers:
        - name: ray-head
          image: rayproject/ray:2.35.0-py310
          resources:
            limits:
              cpu: "2"
              memory: "8Gi"
            requests:
              cpu: "1"
              memory: "4Gi"
  workerGroupSpecs:
  - groupName: gpu-workers
    replicas: 2
    minReplicas: 1
    maxReplicas: 8
    rayStartParams: {}
    template:
      spec:
        containers:
        - name: ray-worker
          image: rayproject/ray:2.35.0-py310-gpu
          resources:
            limits:
              cpu: "4"
              memory: "16Gi"
            requests:
              cpu: "2"
              memory: "8Gi"
```

### Key Field Schema Reference

| Field | Type | Description |
| :--- | :--- | :--- |
| `headGroupSpec` | `Object` | Configuration for Ray Head node (Global Control Store, scheduler, web dashboard). |
| `workerGroupSpecs` | `Array` | Heterogeneous worker pools (CPU, GPU, high-memory) with independent autoscaling bounds. |
| `RayJob` / `RayService` | `CRD` | `RayJob` submits batch training tasks to completion; `RayService` provides zero-downtime serving with Ray Serve. |

---

## 3. Real-World Architectural Patterns

### RayJob Batch Submission Spec

```yaml
apiVersion: ray.io/v1
kind: RayJob
metadata:
  name: llm-finetuning-job
  namespace: ml-workloads
spec:
  entrypoint: "python train.py --epochs 10"
  shutdownAfterJobFinishes: true
  rayClusterSpec:
    rayVersion: "2.35.0"
    headGroupSpec:
      template:
        spec:
          containers:
          - name: ray-head
            image: rayproject/ray:2.35.0
```

### RayService for Multi-Model Inference

```yaml
apiVersion: ray.io/v1
kind: RayService
metadata:
  name: embedding-service
  namespace: ml-workloads
spec:
  serviceUnhealthyThreshold: 300
  rayClusterConfig:
    rayVersion: "2.35.0"
    headGroupSpec:
      template:
        spec:
          containers:
          - name: ray-head
            image: rayproject/ray:2.35.0
```


---

## 4. Production Hardening & Operational Governance

- Use `shutdownAfterJobFinishes: true` on `RayJob` resources to release expensive cloud GPU instances immediately after training.
- Deploy Ray clusters in isolated namespaces paired with ResourceQuotas.
- Expose the Ray Dashboard (port 8265) through secure Ingress with OAuth/OIDC authentication.

---

## 5. Failure Modes & Diagnostic Triage Tree

??? failure "Ray Worker Nodes Not Joining Cluster"
    **Root Cause:** GCS connection failure or mismatched `rayVersion`.

    **Diagnostic Triage Sequence:**
    1. Inspect Head logs: `kubectl logs <head-pod-name> -c ray-head`
    2. Inspect Worker logs: `kubectl logs <worker-pod-name> -c ray-worker`


---

## 6. Interactive Practice Matrix

Practice concepts from this chapter directly in the interactive WebAssembly sandbox:

| Exercise ID | Challenge Description | Direct Link | Action |
| :--- | :--- | :--- | :--- |
| **`ray01`** | RayCluster Core Architecture & Head Node | [`../playground/index.html?exercise=ray01`](../playground/index.html?exercise=ray01) | [**⚡ Solve in Playground →**](../playground/index.html?exercise=ray01){ .md-button .md-button--primary } |
| **`ray02`** | Heterogeneous Worker Pools & Autoscaling | [`../playground/index.html?exercise=ray02`](../playground/index.html?exercise=ray02) | [**⚡ Solve in Playground →**](../playground/index.html?exercise=ray02){ .md-button .md-button--primary } |
| **`ray03`** | RayJob for Distributed Batch Fine-Tuning | [`../playground/index.html?exercise=ray03`](../playground/index.html?exercise=ray03) | [**⚡ Solve in Playground →**](../playground/index.html?exercise=ray03){ .md-button .md-button--primary } |
| **`ray04`** | RayService for Production LLM Serving | [`../playground/index.html?exercise=ray04`](../playground/index.html?exercise=ray04) | [**⚡ Solve in Playground →**](../playground/index.html?exercise=ray04){ .md-button .md-button--primary } |

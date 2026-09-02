# Chapter 25: AI Batch Scheduling & Queuing with Kueue and Volcano

<div class="grid cards" markdown>

-   :material-school: **Topic Focus** &bull; Kueue Cohort Borrowing, Suspended Workloads, Volcano Gang Scheduling, and Fair-Share Queues
-   :material-api: **Primary APIs** &bull; `kueue.x-k8s.io/v1beta1`, `scheduling.volcano.sh/v1beta1` &bull; `ClusterQueue`, `LocalQueue`, `PodGroup`
-   :material-rocket-launch: [**Launch Playground in Wasm →**](../playground/index.html?chapter=25){ .md-button .md-button--primary }

</div>

---

## 1. Architectural Overview & Control Plane Mechanics

In Kubernetes, **AI Batch Scheduling & Queuing with Kueue and Volcano** is reconciled through declarative state loops managed by the control plane:

```text
┌───────────────────────────┐
    │   User Submitted Jobs     │ ──► [ LocalQueue (Namespace A) ]
    └───────────────────────────┘                     │
                                                      ▼
    ┌─────────────────────────────────────────────────────────────┐
    │                      ClusterQueue                           │
    │  • Cohort Borrowing (Shares idle capacity between teams)    │
    │  • Preemption & Fair-Share Scheduling                       │
    └─────────────────────────────┬───────────────────────────────┘
                                  │ Admits Workload
                                  ▼
    ┌─────────────────────────────────────────────────────────────┐
    │          Gang Scheduling (Volcano / Coscheduling)           │
    │          [ All N Pods Scheduled Simultaneously or None ]   │
    └─────────────────────────────────────────────────────────────┘
```

When resources in this chapter are submitted, the `kube-apiserver` validates the OpenAPI v3 schema, stores state in `etcd`, and triggers the responsible controllers or node daemons to reconcile actual cluster state.

---

## 2. Annotated Production YAML Anatomy & Field Reference

Below is a production-grade declarative manifest demonstrating field definitions and operational patterns:

```yaml
apiVersion: kueue.x-k8s.io/v1beta1
kind: ClusterQueue
metadata:
  name: research-cluster-queue
spec:
  namespaceSelector: {}
  cohort: engineering-cohort
  resourceGroups:
  - coveredResources: ["cpu", "memory", "nvidia.com/gpu"]
    flavors:
    - name: standard-flavor
      resources:
      - name: "cpu"
        nominalQuota: "32"
        borrowingLimit: "16"
      - name: "memory"
        nominalQuota: 128Gi
      - name: "nvidia.com/gpu"
        nominalQuota: "8"
---
apiVersion: kueue.x-k8s.io/v1beta1
kind: LocalQueue
metadata:
  name: research-team-queue
  namespace: research-ns
spec:
  clusterQueue: research-cluster-queue
```

### Key Field Schema Reference

| Field | Type | Description |
| :--- | :--- | :--- |
| `ClusterQueue` | `Cluster Resource` | Pools cluster-wide compute resources and establishes quotas, borrowing limits, and preemption policies. |
| `cohort` | `String` | Enables capacity sharing: queues in the same cohort can borrow unused quota from sister queues. |
| `LocalQueue` | `Namespace Resource` | Submission queue in a specific namespace pointing to an upstream ClusterQueue. |

---

## 3. Real-World Architectural Patterns

### Volcano Gang Scheduling PodGroup

```yaml
apiVersion: scheduling.volcano.sh/v1beta1
kind: PodGroup
metadata:
  name: distributed-training-pg
  namespace: default
spec:
  minMember: 4
  minResources:
    cpu: "8"
    memory: "32Gi"
```

### Kueue-Managed Batch Job Submission

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: sample-batch-analysis
  namespace: research-ns
  labels:
    kueue.x-k8s.io/queue-name: research-team-queue
spec:
  parallelism: 4
  completions: 4
  template:
    spec:
      restartPolicy: Never
      containers:
      - name: worker
        image: python:3.12-slim
        command: ["python", "-c", "print('Batch step complete')"]
```


---

## 4. Production Hardening & Operational Governance

- Use Gang Scheduling (`minMember`) for distributed PyTorch/JAX training to avoid deadlock where half the workers occupy GPUs waiting forever for missing peers.
- Establish `borrowingLimit` bounds to prevent a single team from monopolizing cohort resources.
- Enable preemption rules to allow high-priority production jobs to reclaim borrowed capacity.

---

## 5. Failure Modes & Diagnostic Triage Tree

??? failure "Job Inactive / Workload Not Admitted by Kueue"
    **Root Cause:** ClusterQueue nominal quota and borrowing limits are exhausted.

    **Diagnostic Triage Sequence:**
    1. Inspect Kueue Workload: `kubectl get workloads -n <namespace>`
2. Check ClusterQueue status: `kubectl describe clusterqueue <name>`


---

## 6. Interactive Practice Matrix

Practice concepts from this chapter directly in the interactive WebAssembly sandbox:

| Exercise ID | Challenge Description | Direct Link | Action |
| :--- | :--- | :--- | :--- |
| **`kueue01`** | Kueue ResourceFlavor & ClusterQueue Cohort Borrowing | [`../playground/index.html?exercise=kueue01`](../playground/index.html?exercise=kueue01) | [**⚡ Solve in Playground →**](../playground/index.html?exercise=kueue01){ .md-button .md-button--primary } |
| **`kueue02`** | Kueue LocalQueue & Suspended Workload Gating | [`../playground/index.html?exercise=kueue02`](../playground/index.html?exercise=kueue02) | [**⚡ Solve in Playground →**](../playground/index.html?exercise=kueue02){ .md-button .md-button--primary } |
| **`volcano01`** | Volcano Gang Scheduling & Deadlock Prevention | [`../playground/index.html?exercise=volcano01`](../playground/index.html?exercise=volcano01) | [**⚡ Solve in Playground →**](../playground/index.html?exercise=volcano01){ .md-button .md-button--primary } |
| **`volcano02`** | Volcano Queue & Fair-Share Scheduling | [`../playground/index.html?exercise=volcano02`](../playground/index.html?exercise=volcano02) | [**⚡ Solve in Playground →**](../playground/index.html?exercise=volcano02){ .md-button .md-button--primary } |

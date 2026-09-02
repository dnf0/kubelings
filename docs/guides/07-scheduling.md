# Chapter 07: Scheduling, Affinity & Advanced Placement

<div class="grid cards" markdown>

-   :material-school: **Topic Focus** &bull; Node Placement, Affinity, Taints, Tolerations, and Topology Spread
-   :material-api: **Primary APIs** &bull; `v1` &bull; `Pod`, `Node`
-   :material-rocket-launch: [**Launch Playground in Wasm →**](../playground/index.html?chapter=7){ .md-button .md-button--primary }

</div>

!!! tip "⚡ Interactive Problems in this Chapter (Click to solve in Playground)"
    - [**`sched01`**: Node Placement (nodeName & nodeSelector) →](../playground/index.html?exercise=sched01)
    - [**`sched02`**: Node Affinity & Constraints →](../playground/index.html?exercise=sched02)
    - [**`sched03`**: Pod Affinity & Pod Anti-Affinity →](../playground/index.html?exercise=sched03)
    - [**`sched04`**: Taints and Tolerations →](../playground/index.html?exercise=sched04)
    - [**`sched05`**: Topology Spread Constraints →](../playground/index.html?exercise=sched05)

---

## 1. Architectural Overview & Control Plane Mechanics

In Kubernetes, **Scheduling, Affinity & Advanced Placement** is reconciled through declarative state loops managed by the control plane:

```text
┌───────────────────────────┐
│      kube-scheduler       │
└─────────────┬─────────────┘
              │ 1. Filtering (Tolerations, NodeSelector, Affinity)
              │ 2. Scoring (Topology Spread, Resource Packing)
              ▼
┌───────────────────────────┬───────────────────────────┐
│  Zone: us-east-1a         │  Zone: us-east-1b         │
│  [ Node A ] [ Node B ]    │  [ Node C ] [ Node D ]    │
└───────────────────────────┴───────────────────────────┘
```

When resources in this chapter are submitted, the `kube-apiserver` validates the OpenAPI v3 schema, stores state in `etcd`, and triggers the responsible controllers or node daemons to reconcile actual cluster state.

---

## 2. Annotated Production YAML Anatomy & Field Reference

Below is a production-grade declarative manifest demonstrating field definitions and operational patterns:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ha-workload
spec:
  replicas: 4
  selector:
    matchLabels:
      app: ha-app
  template:
    metadata:
      labels:
        app: ha-app
    spec:
      topologySpreadConstraints:
      - maxSkew: 1
        topologyKey: topology.kubernetes.io/zone
        whenUnsatisfiable: DoNotSchedule
        labelSelector:
          matchLabels:
            app: ha-app
      affinity:
        nodeAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            nodeSelectorTerms:
            - matchExpressions:
              - key: node-role.kubernetes.io/worker
                operator: Exists
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchLabels:
                  app: ha-app
              topologyKey: kubernetes.io/hostname
      tolerations:
      - key: "dedicated"
        operator: "Equal"
        value: "compute"
        effect: "NoSchedule"
      containers:
      - name: app
        image: nginx:1.27-alpine
```

### Key Field Schema Reference

| Field | Type | Description |
| :--- | :--- | :--- |
| `topologySpreadConstraints` | `Array` | Distributes Pods evenly across zones/nodes to prevent single-zone outages (`maxSkew: 1`). |
| `affinity.nodeAffinity` | `Object` | Directs Pod placement onto nodes matching specific hardware/architectural labels. |
| `tolerations` | `Array` | Permits Pods to be scheduled on nodes tainted with `NoSchedule` or `NoExecute`. |

---

## 3. Real-World Architectural Patterns

### GPU Node Taint & Toleration Placement

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: ml-inference-task
spec:
  tolerations:
  - key: "nvidia.com/gpu"
    operator: "Exists"
    effect: "NoSchedule"
  nodeSelector:
    accelerator: nvidia-a100
  containers:
  - name: inference
    image: python:3.12-slim
    command: ["python", "-c", "print('Inference worker running...')"]
```

### Pod Anti-Affinity for Zero Co-location

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: singleton-per-node
spec:
  replicas: 3
  selector:
    matchLabels:
      app: singleton
  template:
    metadata:
      labels:
        app: singleton
    spec:
      affinity:
        podAntiAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
          - labelSelector:
              matchLabels:
                app: singleton
            topologyKey: kubernetes.io/hostname
      containers:
      - name: app
        image: nginx:alpine
```


---

## 4. Production Hardening & Operational Governance

- Use `topologySpreadConstraints` with `topologyKey: topology.kubernetes.io/zone` for multi-AZ clusters.
- Use `preferredDuringScheduling` when soft affinity is desired to prevent unschedulable pod deadlocks.
- Reserve specialized nodes (GPU, high-memory) using node taints to prevent general workloads from consuming expensive compute.

---

## 5. Failure Modes & Diagnostic Triage Tree

??? failure "Pod Stuck in `Pending` (`0/10 nodes available`)"
    **Root Cause:** Tolerations, affinity rules, or resource requests cannot be satisfied.

    **Diagnostic Triage Sequence:**
    1. Inspect scheduling failures: `kubectl describe pod <name>`
    2. Review node taints: `kubectl get nodes -o custom-columns=NAME:.metadata.name,TAINTS:.spec.taints`
    3. Review node labels: `kubectl get nodes --show-labels`


---

## 6. Interactive Practice Matrix

Practice concepts from this chapter directly in the interactive WebAssembly sandbox:

| Exercise ID | Challenge Description | Direct Link | Action |
| :--- | :--- | :--- | :--- |
| **`sched01`** | Node Placement (nodeName & nodeSelector) | [`../playground/index.html?exercise=sched01`](../playground/index.html?exercise=sched01) | [**⚡ Solve `sched01` in Playground →**](../playground/index.html?exercise=sched01){ .md-button .md-button--primary } |
| **`sched02`** | Node Affinity & Constraints | [`../playground/index.html?exercise=sched02`](../playground/index.html?exercise=sched02) | [**⚡ Solve `sched02` in Playground →**](../playground/index.html?exercise=sched02){ .md-button .md-button--primary } |
| **`sched03`** | Pod Affinity & Pod Anti-Affinity | [`../playground/index.html?exercise=sched03`](../playground/index.html?exercise=sched03) | [**⚡ Solve `sched03` in Playground →**](../playground/index.html?exercise=sched03){ .md-button .md-button--primary } |
| **`sched04`** | Taints and Tolerations | [`../playground/index.html?exercise=sched04`](../playground/index.html?exercise=sched04) | [**⚡ Solve `sched04` in Playground →**](../playground/index.html?exercise=sched04){ .md-button .md-button--primary } |
| **`sched05`** | Topology Spread Constraints | [`../playground/index.html?exercise=sched05`](../playground/index.html?exercise=sched05) | [**⚡ Solve `sched05` in Playground →**](../playground/index.html?exercise=sched05){ .md-button .md-button--primary } |

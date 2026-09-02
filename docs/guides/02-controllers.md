# Chapter 02: Controllers & Replication

<div class="grid cards" markdown>

-   :material-school: **Topic Focus** &bull; ReplicaSets, Deployments, StatefulSets, DaemonSets, and Jobs
-   :material-api: **Primary APIs** &bull; `apps/v1`, `batch/v1` &bull; `Deployment`, `StatefulSet`, `DaemonSet`, `Job`, `CronJob`
-   :material-rocket-launch: [**Launch Playground in Wasm →**](../playground/index.html?chapter=2){ .md-button .md-button--primary }

</div>

---

## 1. Architectural Overview & Control Plane Mechanics

In Kubernetes, **Controllers & Replication** is reconciled through declarative state loops managed by the control plane:

```text
┌───────────────────────────┐
│     Deployment Controller │
└─────────────┬─────────────┘
              │ Manages ReplicaSets (Rollouts, Revisions)
              ▼
┌───────────────────────────┐
│         ReplicaSet        │
└─────────────┬─────────────┘
              │ Maintains Desired Spec Replicas
              ▼
┌───────────┐   ┌───────────┐   ┌───────────┐
│  Pod 1    │   │  Pod 2    │   │  Pod 3    │
└───────────┘   └───────────┘   └───────────┘
```

When resources in this chapter are submitted, the `kube-apiserver` validates the OpenAPI v3 schema, stores state in `etcd`, and triggers the responsible controllers or node daemons to reconcile actual cluster state.

---

## 2. Annotated Production YAML Anatomy & Field Reference

Below is a production-grade declarative manifest demonstrating field definitions and operational patterns:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-service
  labels:
    app: api-service
spec:
  replicas: 3
  revisionHistoryLimit: 5
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: api-service
  template:
    metadata:
      labels:
        app: api-service
    spec:
      containers:
      - name: api
        image: nginx:1.27-alpine
        ports:
        - containerPort: 8080
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 250m
            memory: 256Mi
```

### Key Field Schema Reference

| Field | Type | Description |
| :--- | :--- | :--- |
| `spec.strategy.rollingUpdate` | `Object` | Controls zero-downtime rollouts via `maxSurge` (surge capacity) and `maxUnavailable` (tolerated disruption). |
| `spec.selector.matchLabels` | `Map` | Immutable label query used by the controller to discover its owned Pods. Must match `spec.template.metadata.labels`. |
| `spec.revisionHistoryLimit` | `Integer (Default: 10)` | Number of historical ReplicaSets retained for instant rollbacks. |

---

## 3. Real-World Architectural Patterns

### StatefulSet with VolumeClaimTemplates

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: redis-cluster
spec:
  serviceName: redis-headless
  replicas: 3
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:7.2-alpine
        ports:
        - containerPort: 6379
        volumeMounts:
        - name: data
          mountPath: /data
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 5Gi
```

### CronJob with Concurrency Policy

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: nightly-backup
spec:
  schedule: "0 2 * * *"
  concurrencyPolicy: Forbid
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 1
  jobTemplate:
    spec:
      backoffLimit: 2
      template:
        spec:
          restartPolicy: OnFailure
          containers:
          - name: backup
            image: busybox:1.36
            command: ["sh", "-c", "echo 'Running DB dump...'; exit 0"]
```


---

## 4. Production Hardening & Operational Governance

- Use `maxUnavailable: 0` during rolling updates to guarantee baseline capacity is never reduced.
- Avoid orphan ReplicaSets by always setting `revisionHistoryLimit`.
- StatefulSets should be paired with headless Services for stable network identities (`$(pod-name).$(service-name).$(namespace).svc.cluster.local`).

---

## 5. Failure Modes & Diagnostic Triage Tree

??? failure "Rollout Stuck / Deployment Blocked"
    **Root Cause:** New ReplicaSet cannot progress due to image pull or readiness probe failures.

    **Diagnostic Triage Sequence:**
    1. View rollout status: `kubectl rollout status deployment/<name>`
2. Inspect rollout history: `kubectl rollout history deployment/<name>`
3. Roll back immediately: `kubectl rollout undo deployment/<name>`

??? failure "StatefulSet Pod Stuck Terminating"
    **Root Cause:** Volume detach/attach cycle locked or node unready.

    **Diagnostic Triage Sequence:**
    1. Check PV status: `kubectl get pvc -l app=<name>`
2. Inspect node status: `kubectl describe node <node>`


---

## 6. Interactive Practice Matrix

Practice concepts from this chapter directly in the interactive WebAssembly sandbox:

| Exercise ID | Challenge Description | Direct Link | Action |
| :--- | :--- | :--- | :--- |
| **`ctrl01`** | ReplicaSets & Label Selectors | [`../playground/index.html?exercise=ctrl01`](../playground/index.html?exercise=ctrl01) | [**⚡ Solve in Playground →**](../playground/index.html?exercise=ctrl01){ .md-button .md-button--primary } |
| **`ctrl02`** | Deployments & Rolling Updates | [`../playground/index.html?exercise=ctrl02`](../playground/index.html?exercise=ctrl02) | [**⚡ Solve in Playground →**](../playground/index.html?exercise=ctrl02){ .md-button .md-button--primary } |
| **`ctrl03`** | Deployment Rollbacks & Revision History | [`../playground/index.html?exercise=ctrl03`](../playground/index.html?exercise=ctrl03) | [**⚡ Solve in Playground →**](../playground/index.html?exercise=ctrl03){ .md-button .md-button--primary } |
| **`ctrl04`** | StatefulSets & Stable Network IDs | [`../playground/index.html?exercise=ctrl04`](../playground/index.html?exercise=ctrl04) | [**⚡ Solve in Playground →**](../playground/index.html?exercise=ctrl04){ .md-button .md-button--primary } |
| **`ctrl05`** | DaemonSets for Node-Level Daemons | [`../playground/index.html?exercise=ctrl05`](../playground/index.html?exercise=ctrl05) | [**⚡ Solve in Playground →**](../playground/index.html?exercise=ctrl05){ .md-button .md-button--primary } |
| **`ctrl06`** | Jobs & CronJobs | [`../playground/index.html?exercise=ctrl06`](../playground/index.html?exercise=ctrl06) | [**⚡ Solve in Playground →**](../playground/index.html?exercise=ctrl06){ .md-button .md-button--primary } |

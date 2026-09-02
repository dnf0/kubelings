# Chapter 11: Autoscaling (HPA, VPA, KEDA)

<div class="grid cards" markdown>

-   :material-school: **Topic Focus** &bull; Horizontal, Vertical, and Event-Driven Workload Autoscaling
-   :material-api: **Primary APIs** &bull; `autoscaling/v2`, `keda.sh/v1alpha1` &bull; `HorizontalPodAutoscaler`, `ScaledObject`
-   :material-rocket-launch: [**Launch Playground in Wasm →**](../playground/index.html?chapter=11){ .md-button .md-button--primary }

</div>

---

## 1. Architectural Overview & Control Plane Mechanics

In Kubernetes, **Autoscaling (HPA, VPA, KEDA)** is reconciled through declarative state loops managed by the control plane:

```text
┌───────────────────────────┐
│    Metrics Server / KEDA  │ ◄── CPU, Memory, SQS, Kafka Lag
└─────────────┬─────────────┘
              │ Evaluates Target vs Current Metric
              ▼
┌───────────────────────────┐
│            HPA            │ ──► Scales Deployment Replicas (2 ──► 10)
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│     Cluster Autoscaler    │ ──► Provisions Additional Cloud Nodes
└───────────────────────────┘
```

When resources in this chapter are submitted, the `kube-apiserver` validates the OpenAPI v3 schema, stores state in `etcd`, and triggers the responsible controllers or node daemons to reconcile actual cluster state.

---

## 2. Annotated Production YAML Anatomy & Field Reference

Below is a production-grade declarative manifest demonstrating field definitions and operational patterns:

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-hpa
  namespace: default
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api-service
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 75
  - type: Resource
    resource:
      name: memory
      target:
        type: AverageValue
        averageValue: 200Mi
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
      - type: Percent
        value: 100
        periodSeconds: 15
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
```

### Key Field Schema Reference

| Field | Type | Description |
| :--- | :--- | :--- |
| `scaleTargetRef` | `Object` | Target controller to scale (`Deployment`, `ReplicaSet`, `StatefulSet`). |
| `metrics[*].type` | `Enum` | `Resource` (CPU/Memory via metrics-server), `Pods` (custom pod metrics), `External` (cloud queues/Prometheus). |
| `behavior.scaleDown.stabilizationWindowSeconds` | `Integer` | Prevents thrashing (flapping) by damping scale-down operations for specified duration. |

---

## 3. Real-World Architectural Patterns

### KEDA Event-Driven SQS Queue Scaler

```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: sqs-worker-scaler
  namespace: default
spec:
  scaleTargetRef:
    name: queue-worker
  minReplicaCount: 1
  maxReplicaCount: 20
  triggers:
  - type: aws-sqs-queue
    metadata:
      queueURL: https://sqs.us-east-1.amazonaws.com/123456789012/order-processing
      queueLength: "10"
      awsRegion: "us-east-1"
```

### Custom Prometheus Metric HPA

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: http-requests-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: web-frontend
  minReplicas: 3
  maxReplicas: 15
  metrics:
  - type: Pods
    pods:
      metric:
        name: http_requests_per_second
      target:
        type: AverageValue
        averageValue: 1k
```


---

## 4. Production Hardening & Operational Governance

- All scaled containers MUST define explicit `resources.requests.cpu` and `resources.requests.memory`; HPA cannot calculate percentages without requests.
- Use `behavior.scaleDown.stabilizationWindowSeconds: 300` to prevent premature scale-down during bursty traffic.
- Avoid running HPA and VPA (Vertical Pod Autoscaler) on the same CPU/memory metrics simultaneously to prevent scaling contention.

---

## 5. Failure Modes & Diagnostic Triage Tree

??? failure "HPA Status `<unknown>/75%`"
    **Root Cause:** Metrics Server is not installed or Pods lack CPU requests.

    **Diagnostic Triage Sequence:**
    1. Verify Metrics Server: `kubectl get apiservices | grep metrics`
    2. Verify Pod metrics: `kubectl top pods`
    3. Check HPA conditions: `kubectl describe hpa <name>`


---

## 6. Interactive Practice Matrix

Practice concepts from this chapter directly in the interactive WebAssembly sandbox:

| Exercise ID | Challenge Description | Direct Link | Action |
| :--- | :--- | :--- | :--- |
| **`autoscale01`** | Horizontal Pod Autoscaler (HPA v2) | [`../playground/index.html?exercise=autoscale01`](../playground/index.html?exercise=autoscale01) | [**⚡ Solve in Playground →**](../playground/index.html?exercise=autoscale01){ .md-button .md-button--primary } |
| **`autoscale02`** | HPA Custom Scaling Behavior | [`../playground/index.html?exercise=autoscale02`](../playground/index.html?exercise=autoscale02) | [**⚡ Solve in Playground →**](../playground/index.html?exercise=autoscale02){ .md-button .md-button--primary } |
| **`autoscale03`** | Vertical Pod Autoscaler (VPA) | [`../playground/index.html?exercise=autoscale03`](../playground/index.html?exercise=autoscale03) | [**⚡ Solve in Playground →**](../playground/index.html?exercise=autoscale03){ .md-button .md-button--primary } |
| **`autoscale04`** | Event-Driven Autoscaling (KEDA) | [`../playground/index.html?exercise=autoscale04`](../playground/index.html?exercise=autoscale04) | [**⚡ Solve in Playground →**](../playground/index.html?exercise=autoscale04){ .md-button .md-button--primary } |

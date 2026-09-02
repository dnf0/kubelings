# Chapter 01: Kubernetes Core Workloads & Pods

<div class="grid cards" markdown>

-   :material-school: **Topic Focus** &bull; Pod Specifications, Multi-Container Sidecars, and Lifecycle
-   :material-api: **Primary APIs** &bull; `v1` &bull; `Pod`, `PodDisruptionBudget`
-   :material-rocket-launch: [**Launch Playground in Wasm →**](../playground/index.html?chapter=1){ .md-button .md-button--primary }

</div>

---

## 1. Architectural Overview & Control Plane Mechanics

In Kubernetes, **Kubernetes Core Workloads & Pods** is reconciled through declarative state loops managed by the control plane:

```text
┌─────────────────────────────────────────────────────────────┐
    │                         Kubelet                             │
    │  ┌─────────────────┐             ┌───────────────────────┐  │
    │  │  Init Container │             │  Main App Container   │  │
    │  │  (runs to exit) │ ──(Shared)─►│  (nginx / python)     │  │
    │  └────────┬────────┘   Volumes   └───────────┬───────────┘  │
    │           │                                  │              │
    │           ▼                                  ▼              │
    │     [ emptyDir / ]                     [ emptyDir / ]       │
    │     [ ConfigMap  ]                     [ Secret     ]       │
    │                                              ▲              │
    │                                  ┌───────────┴───────────┐  │
    │                                  │   Sidecar Container   │  │
    │                                  │   (fluent-bit / proxy)│  │
    │                                  └───────────────────────┘  │
    └─────────────────────────────────────────────────────────────┘
```

When resources in this chapter are submitted, the `kube-apiserver` validates the OpenAPI v3 schema, stores state in `etcd`, and triggers the responsible controllers or node daemons to reconcile actual cluster state.

---

## 2. Annotated Production YAML Anatomy & Field Reference

Below is a production-grade declarative manifest demonstrating field definitions and operational patterns:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: production-web-service
  namespace: default
  labels:
    app.kubernetes.io/name: web-service
    app.kubernetes.io/component: frontend
    app.kubernetes.io/part-of: e-commerce
spec:
  restartPolicy: Always
  terminationGracePeriodSeconds: 30
  initContainers:
  - name: init-db-check
    image: busybox:1.36
    command: ['sh', '-c', 'echo "Waiting for database ready..."; sleep 2;']
    resources:
      limits:
        cpu: "100m"
        memory: "64Mi"
      requests:
        cpu: "50m"
        memory: "32Mi"
  containers:
  - name: web-app
    image: nginx:1.27-alpine
    ports:
    - name: http
      containerPort: 80
      protocol: TCP
    resources:
      limits:
        cpu: "500m"
        memory: "256Mi"
      requests:
        cpu: "250m"
        memory: "128Mi"
    volumeMounts:
    - name: shared-logs
      mountPath: /var/log/nginx
  - name: log-collector
    image: busybox:1.36
    command: ['sh', '-c', 'tail -F /var/log/nginx/access.log 2>/dev/null || true']
    volumeMounts:
    - name: shared-logs
      mountPath: /var/log/nginx
  volumes:
  - name: shared-logs
    emptyDir: {}
```

### Key Field Schema Reference

| Field | Type | Description |
| :--- | :--- | :--- |
| `spec.initContainers` | `Array` | Containers executed sequentially before app containers start. Must exit with code 0. |
| `spec.containers[*].resources` | `Object` | Compute requests (scheduler quota) and limits (cgroup enforcement). |
| `spec.volumes` | `Array` | Shared storage abstractions mounted into container filesystems. |
| `spec.terminationGracePeriodSeconds` | `Integer (Default: 30)` | Duration given for SIGTERM handling before SIGKILL is dispatched. |

---

## 3. Real-World Architectural Patterns

### Sidecar Logging Pattern

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: sidecar-log-processor
spec:
  containers:
  - name: app
    image: alpine:3.20
    command: ["sh", "-c", "while true; do date >> /logs/app.log; sleep 1; done"]
    volumeMounts:
    - name: log-volume
      mountPath: /logs
  - name: shipper
    image: busybox:1.36
    command: ["sh", "-c", "tail -f /logs/app.log"]
    volumeMounts:
    - name: log-volume
      mountPath: /logs
  volumes:
  - name: log-volume
    emptyDir: {}
```

### Downward API Metadata Injection

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: downward-api-env
  labels:
    tier: frontend
spec:
  containers:
  - name: client
    image: busybox:1.36
    command: ["sh", "-c", "env | grep POD_ && sleep 3600"]
    env:
    - name: POD_NAME
      valueFrom:
        fieldRef:
          fieldPath: metadata.name
    - name: POD_NAMESPACE
      valueFrom:
        fieldRef:
          fieldPath: metadata.namespace
    - name: POD_IP
      valueFrom:
        fieldRef:
          fieldPath: status.podIP
```


---

## 4. Production Hardening & Operational Governance

- Always set both `requests` and `limits` to establish predictable QoS classes (Guaranteed vs Burstable).
- Set `securityContext.runAsNonRoot: true` and `securityContext.readOnlyRootFilesystem: true`.
- Drop all Linux capabilities with `capabilities.drop: ['ALL']` and add back only strictly necessary capabilities (e.g. `NET_BIND_SERVICE`).
- Pair multi-instance workloads with `PodDisruptionBudget` to ensure high availability during node drains.

---

## 5. Failure Modes & Diagnostic Triage Tree

??? failure "`CrashLoopBackOff`"
    **Root Cause:** Container starts and exits immediately with an error code.

    **Diagnostic Triage Sequence:**
    1. Inspect exit code: `kubectl get pod <name> -o jsonpath='{.status.containerStatuses[*].state.terminated}'`
2. Check previous container logs: `kubectl logs <name> -c <container> --previous`
3. Verify entrypoint args and required environment variables.

??? failure "`OOMKilled` (Exit Code 137)"
    **Root Cause:** Container exceeded its memory limit cgroup.

    **Diagnostic Triage Sequence:**
    1. Run `kubectl describe pod <name>` and look for `Last State: Terminated / Reason: OOMKilled`.
2. Increase `resources.limits.memory` or profile application heap memory consumption.

??? failure "`Pending` (Scheduling Failure)"
    **Root Cause:** Scheduler cannot find a node meeting CPU/memory/taint requirements.

    **Diagnostic Triage Sequence:**
    1. Inspect scheduling events: `kubectl describe pod <name>`
2. Review cluster capacity: `kubectl describe nodes | grep -A 8 'Allocated resources'`.


---

## 6. Interactive Practice Matrix

Practice concepts from this chapter directly in the interactive WebAssembly sandbox:

| Exercise ID | Challenge Description | Direct Link | Action |
| :--- | :--- | :--- | :--- |
| **`pods01`** | First Pod Manifest & Spec | [`../playground/index.html?exercise=pods01`](../playground/index.html?exercise=pods01) | [**⚡ Solve in Playground →**](../playground/index.html?exercise=pods01){ .md-button .md-button--primary } |
| **`pods02`** | Multi-Container Pods & Sidecar Pattern | [`../playground/index.html?exercise=pods02`](../playground/index.html?exercise=pods02) | [**⚡ Solve in Playground →**](../playground/index.html?exercise=pods02){ .md-button .md-button--primary } |
| **`pods03`** | Init Containers for Initialization | [`../playground/index.html?exercise=pods03`](../playground/index.html?exercise=pods03) | [**⚡ Solve in Playground →**](../playground/index.html?exercise=pods03){ .md-button .md-button--primary } |
| **`pods04`** | Resource Requests, Limits & QoS | [`../playground/index.html?exercise=pods04`](../playground/index.html?exercise=pods04) | [**⚡ Solve in Playground →**](../playground/index.html?exercise=pods04){ .md-button .md-button--primary } |
| **`pods05`** | Downward API & Env Variables | [`../playground/index.html?exercise=pods05`](../playground/index.html?exercise=pods05) | [**⚡ Solve in Playground →**](../playground/index.html?exercise=pods05){ .md-button .md-button--primary } |
| **`pods06`** | Pod Disruption Budgets & Static Pods | [`../playground/index.html?exercise=pods06`](../playground/index.html?exercise=pods06) | [**⚡ Solve in Playground →**](../playground/index.html?exercise=pods06){ .md-button .md-button--primary } |

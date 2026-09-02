# Chapter 10: Health Checking, Probes & Lifecycle

<div class="grid cards" markdown>

-   :material-school: **Topic Focus** &bull; Liveness, Readiness, Startup Probes, and Termination Hooks
-   :material-api: **Primary APIs** &bull; `v1` &bull; `Pod`
-   :material-rocket-launch: [**Launch Playground in Wasm →**](../playground/index.html?chapter=10){ .md-button .md-button--primary }

</div>

---

## 1. Architectural Overview & Control Plane Mechanics

In Kubernetes, **Health Checking, Probes & Lifecycle** is reconciled through declarative state loops managed by the control plane:

```text
Container Startup
       │
       ▼
┌─────────────────────────┐
│      Startup Probe      │ ──(Fails)──► Kubelet Restarts Container
└────────────┬────────────┘
             │ (Passes)
             ▼
┌─────────────────────────┐          ┌─────────────────────────┐
│     Liveness Probe      │ ──Fail──►│ Kubelet Restarts Cont.  │
└─────────────────────────┘          └─────────────────────────┘
┌─────────────────────────┐          ┌─────────────────────────┐
│     Readiness Probe     │ ──Fail──►│ Remove from Endpoints   │
└─────────────────────────┘          └─────────────────────────┘
```

When resources in this chapter are submitted, the `kube-apiserver` validates the OpenAPI v3 schema, stores state in `etcd`, and triggers the responsible controllers or node daemons to reconcile actual cluster state.

---

## 2. Annotated Production YAML Anatomy & Field Reference

Below is a production-grade declarative manifest demonstrating field definitions and operational patterns:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: robust-lifecycle-service
spec:
  containers:
  - name: web-app
    image: nginx:1.27-alpine
    ports:
    - containerPort: 8080
    startupProbe:
      httpGet:
        path: /healthz
        port: 8080
      failureThreshold: 30
      periodSeconds: 2
    livenessProbe:
      httpGet:
        path: /healthz
        port: 8080
      initialDelaySeconds: 5
      periodSeconds: 10
      timeoutSeconds: 2
      failureThreshold: 3
    readinessProbe:
      httpGet:
        path: /ready
        port: 8080
      initialDelaySeconds: 2
      periodSeconds: 5
      successThreshold: 1
      failureThreshold: 2
    lifecycle:
      preStop:
        exec:
          command: ["sh", "-c", "sleep 10"]
```

### Key Field Schema Reference

| Field | Type | Description |
| :--- | :--- | :--- |
| `startupProbe` | `Object` | Disables liveness/readiness checks until application initialization is complete. Ideal for slow JVM / ML warmups. |
| `livenessProbe` | `Object` | Detects deadlocks or broken states; triggers kubelet container restart upon failure. |
| `readinessProbe` | `Object` | Determines if the container can receive traffic; triggers removal from Service EndpointSlices when failing. |
| `lifecycle.preStop` | `Object` | Executes synchronously before container receives SIGTERM, allowing in-flight requests to drain. |

---

## 3. Real-World Architectural Patterns

### TCP Socket Readiness & Exec Liveness

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: custom-probes
spec:
  containers:
  - name: redis
    image: redis:7.2-alpine
    ports:
    - containerPort: 6379
    livenessProbe:
      exec:
        command: ["redis-cli", "ping"]
      periodSeconds: 10
    readinessProbe:
      tcpSocket:
        port: 6379
      periodSeconds: 5
```

### gRPC Health Checking Protocol Probe

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: grpc-service
spec:
  containers:
  - name: grpc-app
    image: grpc-server:v1
    ports:
    - containerPort: 50051
    livenessProbe:
      grpc:
        port: 50051
        service: "HealthService"
      initialDelaySeconds: 10
```


---

## 4. Production Hardening & Operational Governance

- Always include a `preStop` hook with a brief `sleep` (e.g. 5–10s) to give kube-proxy / iptables time to propagate endpoint removal before SIGTERM.
- Never point liveness probes at downstream dependencies (e.g. database); liveness should test only local container health.
- Use `startupProbe` with high `failureThreshold` for slow-booting applications rather than inflated `initialDelaySeconds` on liveness probes.

---

## 5. Failure Modes & Diagnostic Triage Tree

??? failure "Container Constantly Restarting (`Unhealthy` events)"
    **Root Cause:** Liveness probe timeout or non-200 HTTP response code.

    **Diagnostic Triage Sequence:**
    1. Run `kubectl describe pod <name>` and inspect `Events`.
2. Check probe response manually: `kubectl exec -it <name> -- wget -qO- http://localhost:8080/healthz`.

??? failure "Pod Running but Service Not Serving Traffic"
    **Root Cause:** Readiness probe is failing, causing Pod exclusion from Endpoints.

    **Diagnostic Triage Sequence:**
    1. Check endpoint membership: `kubectl get endpoints <service-name>`
2. Check readiness status in `kubectl describe pod <name>`.


---

## 6. Interactive Practice Matrix

Practice concepts from this chapter directly in the interactive WebAssembly sandbox:

| Exercise ID | Challenge Description | Direct Link | Action |
| :--- | :--- | :--- | :--- |
| **`health01`** | Liveness Probes | [`../playground/index.html?exercise=health01`](../playground/index.html?exercise=health01) | [**⚡ Solve in Playground →**](../playground/index.html?exercise=health01){ .md-button .md-button--primary } |
| **`health02`** | Readiness Probes | [`../playground/index.html?exercise=health02`](../playground/index.html?exercise=health02) | [**⚡ Solve in Playground →**](../playground/index.html?exercise=health02){ .md-button .md-button--primary } |
| **`health03`** | Startup Probes | [`../playground/index.html?exercise=health03`](../playground/index.html?exercise=health03) | [**⚡ Solve in Playground →**](../playground/index.html?exercise=health03){ .md-button .md-button--primary } |
| **`health04`** | Lifecycle Hooks & Graceful Shutdown | [`../playground/index.html?exercise=health04`](../playground/index.html?exercise=health04) | [**⚡ Solve in Playground →**](../playground/index.html?exercise=health04){ .md-button .md-button--primary } |

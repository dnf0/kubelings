# Chapter 10: Health Checking, Probes & Lifecycle

<div class="grid cards" markdown>

-   :material-school: **Topic Focus** &bull; Liveness, Readiness, Startup Probes, and Termination Hooks
-   :material-api: **Primary APIs** &bull; `v1` &bull; `Pod`
-   :material-rocket-launch: [**Launch Playground in Wasm →**](../playground/index.html?chapter=10){ .md-button .md-button--primary }

</div>

!!! tip "⚡ Interactive Problems in this Chapter (Click to solve in Playground)"
    - [**`health01`**: Liveness Probes →](../playground/index.html?exercise=health01)
    - [**`health02`**: Readiness Probes →](../playground/index.html?exercise=health02)
    - [**`health03`**: Startup Probes →](../playground/index.html?exercise=health03)
    - [**`health04`**: Lifecycle Hooks & Graceful Shutdown →](../playground/index.html?exercise=health04)

---

## 1. Architectural Overview & Control Plane Mechanics

In Kubernetes, **Health Checking, Probes & Lifecycle** is reconciled through declarative state loops managed by the control plane and node daemons:

```mermaid
flowchart TD
    subgraph ContainerBoot["Container Startup Phase"]
        BOOT["Container Spawns (PID 1)"]
        STARTUP{"Startup Probe<br/><i>failureThreshold: 30, period: 10s</i>"}
        BOOT --> STARTUP
    end

    subgraph ActiveMonitoring["Operational Lifecycle Probes"]
        LIVENESS{"Liveness Probe<br/><i>(Is process deadlocked?)</i>"}
        READINESS{"Readiness Probe<br/><i>(Can process accept traffic?)</i>"}
    end

    subgraph EnforcementActions["Kubelet & Networking Actions"]
        RESTART["Kubelet kills container<br/><i>(CrashLoopBackOff trigger)</i>"]
        ADD_EP["EndpointSlice includes Pod IP<br/><i>(Receives Service Traffic)</i>"]
        REMOVE_EP["EndpointSlice removes Pod IP<br/><i>(Traffic Diverted)</i>"]
    end

    STARTUP -->|Passes| LIVENESS
    STARTUP -->|Passes| READINESS
    STARTUP -->|Fails 30x| RESTART

    LIVENESS -->|Fails threshold| RESTART
    LIVENESS -->|Healthy| READINESS
    READINESS -->|Success (Ready=True)| ADD_EP
    READINESS -->|Failure (Ready=False)| REMOVE_EP
```

### 1.1 Architectural Flow & Lifecycle Walkthrough

1. **Container Process Startup (PID 1)**: The container runtime launches the container process inside isolated namespaces.
2. **Phase 1: Startup Probe Evaluation**:
   - `kubelet` initiates the configured `startupProbe` (HTTP GET, TCP Socket, gRPC, or Exec).
   - All `livenessProbe` and `readinessProbe` checks remain **disabled** while the startup probe executes.
   - If the startup probe succeeds within its `failureThreshold * periodSeconds` budget, the container transitions to active operational monitoring. If the budget is exhausted without success, `kubelet` kills the container and initiates a restart.
3. **Phase 2: Operational Monitoring (Liveness & Readiness Parallel Loops)**:
   - **Liveness Probe**: `kubelet` periodically executes the liveness check (e.g., HTTP `/healthz`). If consecutive failures reach `failureThreshold`, `kubelet` terminates the container process with `SIGTERM` (followed by `SIGKILL` after `terminationGracePeriodSeconds`) and increments the restart counter.
   - **Readiness Probe**: `kubelet` periodically executes the readiness check (e.g., HTTP `/ready`).
     - **Success**: `kubelet` sets `.status.conditions[Type=Ready].status = "True"`. The `EndpointSlice` controller includes the Pod IP, enabling it to receive traffic from Kubernetes Services.
     - **Failure**: `kubelet` sets `Ready = False`. The `EndpointSlice` controller immediately removes the Pod IP from active endpoint pools, diverting traffic away from the unready container without killing the process.

### 1.2 Serialization, Protocols & Communication Pathways

- **HTTP/1.1 & HTTP/2 Prober Client**: Kubelet's internal Go HTTP prober sends standard HTTP requests with configurable headers and timeouts directly to the container IP.
- **gRPC Health Checking Protocol (v1)**: Kubelet invokes the standard `grpc.health.v1.Health/Check` RPC over HTTP/2, evaluating the returned `ServingStatus` enum (`SERVING`, `NOT_SERVING`).
- **Linux `/bin/sh -c` Exec RPC**: For Exec probes, kubelet issues a `ExecSync` CRI gRPC call, evaluating the process exit code (`0` = Success, non-zero = Failure).

### 1.3 Deep-Dive Component Breakdown

- **Kubelet Prober Worker**: Dedicated background goroutine pool inside kubelet executing non-blocking probe checks per container according to `periodSeconds` and `timeoutSeconds`.
- **EndpointSlice Controller**: Kubernetes controller that synchronizes Pod `Ready` status conditions into active load balancer and service routing tables.
- **Container Lifecycle Handler (`postStart` / `preStop`)**: Execution hooks run asynchronously (`postStart`) or blocking before SIGTERM (`preStop`) to enable graceful connection draining.
- **Linux Process Signal Manager**: Kubelet subsystem dispatching `SIGTERM` (15) and `SIGKILL` (9) to container PID 1.

### 1.4 Under-The-Hood Mechanics & Failure Modes

- **Cascading Failure Loop (Liveness on Overloaded Backends)**: Configuring a Liveness probe to check deep dependencies (like backend database connectivity) causes overloaded servers to fail liveness checks, prompting kubelet to kill and restart all instances simultaneously, amplifying the outage. Liveness probes must **only** verify shallow process health.
- **Readiness Flapping under Heavy Load**: If `timeoutSeconds` is set too low (e.g., 1s) and the application experiences transient CPU starvation, readiness probes timeout, dropping the Pod from service endpoints and overloading the remaining healthy replicas.
- **PID 1 Signal Swallowing**: If an application runs under a shell script without `exec` (e.g. `CMD ["sh", "-c", "node server.js"]`), the shell process becomes PID 1 and may swallow `SIGTERM`, preventing graceful connection shutdown until `terminationGracePeriodSeconds` expires and `SIGKILL` is issued.

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
| **`health01`** | Liveness Probes | [`../playground/index.html?exercise=health01`](../playground/index.html?exercise=health01) | [**⚡ Solve `health01` in Playground →**](../playground/index.html?exercise=health01){ .md-button .md-button--primary } |
| **`health02`** | Readiness Probes | [`../playground/index.html?exercise=health02`](../playground/index.html?exercise=health02) | [**⚡ Solve `health02` in Playground →**](../playground/index.html?exercise=health02){ .md-button .md-button--primary } |
| **`health03`** | Startup Probes | [`../playground/index.html?exercise=health03`](../playground/index.html?exercise=health03) | [**⚡ Solve `health03` in Playground →**](../playground/index.html?exercise=health03){ .md-button .md-button--primary } |
| **`health04`** | Lifecycle Hooks & Graceful Shutdown | [`../playground/index.html?exercise=health04`](../playground/index.html?exercise=health04) | [**⚡ Solve `health04` in Playground →**](../playground/index.html?exercise=health04){ .md-button .md-button--primary } |

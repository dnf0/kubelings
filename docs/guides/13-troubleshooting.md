# Chapter 13: Observability, Debugging & Production Troubleshooting

<div class="grid cards" markdown>

-   :material-school: **Topic Focus** &bull; CrashLoopBackOff, ImagePullBackOff, Pending Pods, Quotas, and kubectl debug
-   :material-api: **Primary APIs** &bull; `v1` &bull; `Pod`, `Event`, `Node`
-   :material-rocket-launch: [**Launch Playground in Wasm →**](../playground/index.html?chapter=13){ .md-button .md-button--primary }

</div>

!!! tip "⚡ Interactive Problems in this Chapter (Click to solve in Playground)"
    - [**`troubleshoot01`**: Debugging CrashLoopBackOff & Exit Codes →](../playground/index.html?exercise=troubleshoot01)
    - [**`troubleshoot02`**: Debugging ImagePullBackOff →](../playground/index.html?exercise=troubleshoot02)
    - [**`troubleshoot03`**: Debugging Pending Pods & Scheduling Failures →](../playground/index.html?exercise=troubleshoot03)
    - [**`troubleshoot04`**: ResourceQuotas & LimitRanges →](../playground/index.html?exercise=troubleshoot04)
    - [**`troubleshoot05`**: Ephemeral Debug Containers & Event Triage →](../playground/index.html?exercise=troubleshoot05)

---

## 1. Architectural Overview & Control Plane Mechanics

In Kubernetes, **Observability, Debugging & Production Troubleshooting** is reconciled through declarative state loops managed by the control plane and node daemons:

```mermaid
flowchart TD
    START(["🚨 Pod Failure Detected"]) --> STATUS{"Check Pod Phase"}

    STATUS -->|Pending| PEND{"Node Assignment Issue?"}
    PEND -->|Insufficient CPU/Memory| FIX_CAP["Scale Cluster Nodes / Reduce Resource Requests"]
    PEND -->|Node Affinity / Taint Conflict| FIX_TAINT["Add Toleration or Fix Node Labels"]

    STATUS -->|CrashLoopBackOff| CRASH{"Exit Code Analysis"}
    CRASH -->|Exit 137 (SIGKILL)| OOM["OOMKilled: Increase container memory limit"]
    CRASH -->|Exit 1 / 2| LOGS["Inspect <code>kubectl logs -p &lt;pod&gt;</code> for runtime exceptions"]
    CRASH -->|Exit 127 / 128| IMG["ImagePullBackOff / Missing Binary or Entrypoint"]

    STATUS -->|Running but No Traffic| READY{"Readiness Check"}
    READY -->|Ready: False| PROBE["Fix failing Readiness Probe / Backend Health endpoint"]
    READY -->|Ready: True| NET["Verify Service Selector matches Pod Labels & EndpointSlice"]
```

### 1.1 Architectural Flow & Lifecycle Walkthrough

1. **Failure Signal Detection**: An alert fires or a Pod fails to enter `Running` state. The engineer initiates diagnostic triage by querying `kubectl get pod -o wide` and inspecting the Pod phase and status conditions.
2. **Phase 1: Pending Phase Diagnostics**:
   - The Pod has not been assigned a node (`spec.nodeName` is empty).
   - Check scheduler events via `kubectl describe pod <name>`.
   - If `0/10 nodes available: Insufficient cpu/memory`: Cluster is out of allocatable capacity &rarr; Scale worker nodes or decrease container resource requests.
   - If `0/10 nodes available: node(s) had untolerated taint`: Add matching toleration to `spec.tolerations` or fix node taints.
3. **Phase 2: CrashLoopBackOff Diagnostics**:
   - The container starts but exits repeatedly with a non-zero exit code. Kubelet applies exponential restart backoff (10s, 20s, 40s, up to 300s).
   - Inspect previous container logs: `kubectl logs <pod> --previous`.
   - Analyze container termination exit code in `kubectl describe pod <name>`:
     - **Exit 137 (Fatal error signal 9 `SIGKILL`)**: The Linux kernel Out-Of-Memory (OOM) killer killed the container (`OOMKilled: true`). Increase `resources.limits.memory` or fix application memory leaks.
     - **Exit 1 / 2**: Application runtime crash, uncaught exception, or missing configuration file.
     - **Exit 127 / 128**: Container entrypoint binary not found or library dependency missing in image.
4. **Phase 3: ImagePullBackOff Diagnostics**:
   - Kubelet fails to download the container image.
   - Verify image tag existence in the remote container registry.
   - Verify registry authentication Secret (`imagePullSecrets`) and IAM repository permissions.
5. **Phase 4: Running but No Traffic (Readiness Failure)**:
   - The Pod is `Running` but receives zero HTTP traffic from its Service.
   - Inspect `.status.conditions[Type=Ready]`. If `Ready: False`, the `readinessProbe` is failing &rarr; Inspect health check endpoint.
   - If `Ready: True`, verify that `Service.spec.selector` labels match `Pod.metadata.labels` exactly, and confirm `kubectl get endpointslices` contains the Pod IP.

### 1.2 Serialization, Protocols & Communication Pathways

- **Linux Kernel Process Exit Codes**: Standard Unix exit status codes ($128 + \text{Signal Number}$) returned via `waitpid()` system call to the container runtime and passed to kubelet over CRI gRPC.
- **Kubelet `/logs` Streaming API**: Kubelet streams stdout/stderr log files directly from `/var/log/pods/` to the API server and `kubectl` over WebSocket or chunked HTTP/2 streams.
- **Kubernetes Events API**: Transient warning and error events (`v1.Event`) are emitted by controllers and kubelet to `kube-apiserver` as structured JSON/Protobuf messages.

### 1.3 Deep-Dive Component Breakdown

- **Kubelet PLEG (Pod Lifecycle Event Generator)**: Subsystem monitoring container lifecycle state changes via runtime relisting and Linux inotify events.
- **Linux Kernel OOM Killer**: Low-memory subsystem terminating processes when physical RAM + swap is exhausted, prioritizing processes with highest `/proc/[pid]/oom_score`.
- **ImagePullBackOff State Machine**: Kubelet backoff algorithm doubling pull retry intervals from 10s up to a maximum of 300s upon failed registry pulls.
- **EndpointSlice Sync Loop**: Network control loop removing unready Pod IPs from service routing tables within milliseconds of readiness probe failure.

### 1.4 Under-The-Hood Mechanics & Failure Modes

- **Silent OOMKilled without Logs**: When a process exceeds `limits.memory`, the Linux kernel dispatches an uncatchable `SIGKILL` (signal 9). The application cannot execute shutdown hooks or flush log buffers, leaving the container log file empty. Always verify `kubectl describe pod` for `OOMKilled: true` and `Exit Code: 137`.
- **Ephemeral Storage Eviction**: If an application writes unbounded log files or temporary data to the root container filesystem or `emptyDir` volumes exceeding `limits.ephemeral-storage`, kubelet evicts the Pod with `Evicted: Pod ephemeral local storage usage exceeds limit`.
- **Zombie / Stale DNS Caching**: Applications that resolve backend service DNS once at boot and cache the IP indefinitely will fail to connect when backend Pods are replaced during rolling updates. Ensure JVM/Node/Go DNS TTLs are configured to low values (e.g., 5-10s).

---

## 2. Annotated Production YAML Anatomy & Field Reference

Below is a production-grade declarative manifest demonstrating field definitions and operational patterns:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: diagnostic-pod
  namespace: default
spec:
  restartPolicy: OnFailure
  containers:
  - name: debug-shell
    image: busybox:1.36
    command: ["sh", "-c", "echo 'System Health Check'; env; df -h;"]
    resources:
      limits:
        memory: "64Mi"
        cpu: "100m"
```

### Key Field Schema Reference

| Field | Type | Description |
| :--- | :--- | :--- |
| `status.phase` | `Enum` | `Pending`, `Running`, `Succeeded`, `Failed`, `Unknown`. |
| `status.containerStatuses[*].state` | `Object` | `waiting`, `running`, or `terminated` (with reason and exit code). |
| `kubectl debug` | `CLI Command` | Attaches ephemeral container to running pod for live kernel/network inspection. |

---

## 3. Real-World Architectural Patterns

### Ephemeral Debugging Container Injection

```yaml
# Attach an ephemeral debug container with network tools to a running pod
# kubectl debug -it target-pod --image=nicolaka/netshoot --target=web-app
apiVersion: v1
kind: Pod
metadata:
  name: target-pod
spec:
  containers:
  - name: web-app
    image: nginx:alpine
```

### Node Problem Diagnostic Pod

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: node-debugger
  namespace: kube-system
spec:
  hostNetwork: true
  hostPID: true
  containers:
  - name: host-access
    image: busybox:1.36
    command: ["sh", "-c", "nsenter --target 1 --mount --uts --ipc --net --pid /bin/sh"]
    securityContext:
      privileged: true
```


---

## 4. Production Hardening & Operational Governance

- Restrict `kubectl debug` with ephemeral containers using RBAC to prevent unauthorized cluster privilege escalation.
- Export cluster events to centralized Elasticsearch/Loki sinks; etcd purges events after 1 hour by default.
- Use structured JSON logging in all container workloads to simplify log aggregation and alerting.

---

## 5. Failure Modes & Diagnostic Triage Tree

??? failure "Golden Triage Commands"
    **Root Cause:** Standard 4-step triage sequence for any broken Kubernetes workload.

    **Diagnostic Triage Sequence:**
    ```bash
    # 1. Identify failing resources
    kubectl get pods -A -o wide --sort-by=.status.startTime
    
    # 2. Inspect events & container state
    kubectl describe pod <pod-name>
    
    # 3. Read previous container crash logs
    kubectl logs <pod-name> -c <container> --previous --tail=100
    
    # 4. Check cluster-wide chronological warning events
    kubectl get events -A --field-selector type=Warning --sort-by=.metadata.creationTimestamp
    ```


---

## 6. Interactive Practice Matrix

Practice concepts from this chapter directly in the interactive WebAssembly sandbox:

| Exercise ID | Challenge Description | Direct Link | Action |
| :--- | :--- | :--- | :--- |
| **`troubleshoot01`** | Debugging CrashLoopBackOff & Exit Codes | [`../playground/index.html?exercise=troubleshoot01`](../playground/index.html?exercise=troubleshoot01) | [**⚡ Solve `troubleshoot01` in Playground →**](../playground/index.html?exercise=troubleshoot01){ .md-button .md-button--primary } |
| **`troubleshoot02`** | Debugging ImagePullBackOff | [`../playground/index.html?exercise=troubleshoot02`](../playground/index.html?exercise=troubleshoot02) | [**⚡ Solve `troubleshoot02` in Playground →**](../playground/index.html?exercise=troubleshoot02){ .md-button .md-button--primary } |
| **`troubleshoot03`** | Debugging Pending Pods & Scheduling Failures | [`../playground/index.html?exercise=troubleshoot03`](../playground/index.html?exercise=troubleshoot03) | [**⚡ Solve `troubleshoot03` in Playground →**](../playground/index.html?exercise=troubleshoot03){ .md-button .md-button--primary } |
| **`troubleshoot04`** | ResourceQuotas & LimitRanges | [`../playground/index.html?exercise=troubleshoot04`](../playground/index.html?exercise=troubleshoot04) | [**⚡ Solve `troubleshoot04` in Playground →**](../playground/index.html?exercise=troubleshoot04){ .md-button .md-button--primary } |
| **`troubleshoot05`** | Ephemeral Debug Containers & Event Triage | [`../playground/index.html?exercise=troubleshoot05`](../playground/index.html?exercise=troubleshoot05) | [**⚡ Solve `troubleshoot05` in Playground →**](../playground/index.html?exercise=troubleshoot05){ .md-button .md-button--primary } |

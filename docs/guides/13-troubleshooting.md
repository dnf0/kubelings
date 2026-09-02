# Chapter 13: Observability, Debugging & Production Troubleshooting

<div class="grid cards" markdown>

-   :material-school: **Topic Focus** &bull; CrashLoopBackOff, ImagePullBackOff, Pending Pods, Quotas, and kubectl debug
-   :material-api: **Primary APIs** &bull; `v1` &bull; `Pod`, `Event`, `Node`
-   :material-rocket-launch: [**Launch Playground in Wasm →**](../playground/index.html?chapter=13){ .md-button .md-button--primary }

</div>

---

## 1. Architectural Overview & Control Plane Mechanics

In Kubernetes, **Observability, Debugging & Production Troubleshooting** is reconciled through declarative state loops managed by the control plane:

```text
Troubleshooting Decision Flowchart
┌───────────────────────────┐
│     Pod Not Working?      │
└─────────────┬─────────────┘
              │
  ┌───────────┴───────────┐
  ▼                       ▼
[ Status: Pending ]     [ Status: CrashLoopBackOff ]
  │                       │
  ├─► Insufficient CPU    ├─► Check logs: `kubectl logs --previous`
  ├─► Missing PV / Secret ├─► Inspect Exit Code (137 = OOMKilled)
  └─► Node Taint Mismatch └─► Check ConfigMap / Env Vars
```

When resources in this chapter are submitted, the `kube-apiserver` validates the OpenAPI v3 schema, stores state in `etcd`, and triggers the responsible controllers or node daemons to reconcile actual cluster state.

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
| **`troubleshoot01`** | Debugging CrashLoopBackOff & Exit Codes | [`../playground/index.html?exercise=troubleshoot01`](../playground/index.html?exercise=troubleshoot01) | [**⚡ Solve in Playground →**](../playground/index.html?exercise=troubleshoot01){ .md-button .md-button--primary } |
| **`troubleshoot02`** | Debugging ImagePullBackOff | [`../playground/index.html?exercise=troubleshoot02`](../playground/index.html?exercise=troubleshoot02) | [**⚡ Solve in Playground →**](../playground/index.html?exercise=troubleshoot02){ .md-button .md-button--primary } |
| **`troubleshoot03`** | Debugging Pending Pods & Scheduling Failures | [`../playground/index.html?exercise=troubleshoot03`](../playground/index.html?exercise=troubleshoot03) | [**⚡ Solve in Playground →**](../playground/index.html?exercise=troubleshoot03){ .md-button .md-button--primary } |
| **`troubleshoot04`** | ResourceQuotas & LimitRanges | [`../playground/index.html?exercise=troubleshoot04`](../playground/index.html?exercise=troubleshoot04) | [**⚡ Solve in Playground →**](../playground/index.html?exercise=troubleshoot04){ .md-button .md-button--primary } |
| **`troubleshoot05`** | Ephemeral Debug Containers & Event Triage | [`../playground/index.html?exercise=troubleshoot05`](../playground/index.html?exercise=troubleshoot05) | [**⚡ Solve in Playground →**](../playground/index.html?exercise=troubleshoot05){ .md-button .md-button--primary } |

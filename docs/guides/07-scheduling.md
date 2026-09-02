# Chapter 07: Scheduling, Affinity & Advanced Placement

<div class="grid cards" markdown>

-   :material-school: **Topic Focus** &bull; Node Placement, Affinity, Taints, Tolerations, and Topology Spread
-   :material-play-circle: **Interactive Challenges** &bull; 5 Hands-on Exercises
-   :material-rocket-launch: [**Launch Playground in Wasm →**](../playground/index.html?chapter=7){ .md-button .md-button--primary }

</div>

---

## 1. Architectural Overview & Control Plane Mechanics

In Kubernetes, **Scheduling, Affinity & Advanced Placement** represents fundamental declarative resources managed through continuous control loops. 

```text
    ┌──────────────────────┐          Declarative Manifest (YAML)
    │   kube-apiserver     │ ◄─────────────────────────────────────────────
    └──────────┬───────────┘
               │ (Watches & Stores in etcd)
               ▼
    ┌──────────────────────┐          Reconciles Desired State vs Actual State
    │  Controller / Daemon │ ─────────────────────────────────────────────► [ Cluster State ]
    └──────────────────────┘
```

When you declare resources for this domain, the Kubernetes API Server validates the OpenAPI v3 schema, persists the specification to etcd, and signals the responsible controller or node daemon to reconcile actual state with your desired specification.

---

## 2. Annotated YAML Anatomy & Schema Reference

Below is a production-ready declarative manifest illustrating key fields, structure, and configuration semantics for this chapter:

```yaml

```

### Key Field Reference

- **`apiVersion`**: The target API group and version for the resource schema.
- **`kind`**: The resource type identifier.
- **`metadata.name`**: Unique DNS-1123 compliant identifier for this resource within its namespace.
- **`metadata.labels`**: Key-value pairs used by selectors, services, and queries.
- **`spec`**: The desired state specification managed by Kubernetes controllers.

---

## 3. Production Best Practices & Hardening Guidelines

1. **Explicit Resource Declarations**: Always specify resource constraints (`requests` and `limits`) to ensure predictable scheduling and prevent node resource starvation.
2. **Immutable Identifiers & Clear Labeling**: Use standard Kubernetes recommended labels (`app.kubernetes.io/name`, `app.kubernetes.io/instance`, `app.kubernetes.io/version`, `app.kubernetes.io/component`).
3. **Defense in Depth**: Follow least-privilege security principles (e.g. `runAsNonRoot: true`, `readOnlyRootFilesystem: true`, dropping all unnecessary Linux capabilities).
4. **Health Check Probes**: Configure comprehensive startup, liveness, and readiness probes with appropriate failure thresholds and timing delays.
5. **Declarative GitOps Management**: Maintain all manifests in version control and deploy through automated reconciliation pipelines.

---

## 4. Troubleshooting & Diagnostic Workflows

When inspecting or debugging resources in this category, use the following triage sequence:

```bash
# 1. Check resource status and conditions
kubectl get scheduling -o wide

# 2. Inspect detailed control plane events and controller messages
kubectl describe scheduling <resource-name>

# 3. Stream real-time logs (if applicable)
kubectl logs -l app=<label> --tail=100 -f
```

---

## 5. Interactive Practice Exercises

Practice the concepts from this chapter directly in your browser using our client-side WebAssembly environment:

- [**`sched01`**: Node Placement (nodeName & nodeSelector)](../playground/index.html?exercise=sched01)
- [**`sched02`**: Node Affinity & Constraints](../playground/index.html?exercise=sched02)
- [**`sched03`**: Pod Affinity & Pod Anti-Affinity](../playground/index.html?exercise=sched03)
- [**`sched04`**: Taints and Tolerations](../playground/index.html?exercise=sched04)
- [**`sched05`**: Topology Spread Constraints](../playground/index.html?exercise=sched05)

<div style="margin-top: 1.5rem;">
  <a href="../playground/index.html?chapter=7" class="md-button md-button--primary">
    ⚡ Practice Chapter 07 in WebAssembly Playground →
  </a>
</div>

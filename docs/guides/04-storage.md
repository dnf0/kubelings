# Chapter 04: Storage & Persistent Volumes

<div class="grid cards" markdown>

-   :material-school: **Topic Focus** &bull; PVs, PVCs, Access Modes, StorageClasses, and Snapshots
-   :material-play-circle: **Interactive Challenges** &bull; 5 Hands-on Exercises
-   :material-rocket-launch: [**Launch Playground in Wasm →**](../playground/index.html?chapter=4){ .md-button .md-button--primary }

</div>

---

## 1. Architectural Overview & Control Plane Mechanics

In Kubernetes, **Storage & Persistent Volumes** represents fundamental declarative resources managed through continuous control loops. 

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
kubectl get storage -o wide

# 2. Inspect detailed control plane events and controller messages
kubectl describe storage <resource-name>

# 3. Stream real-time logs (if applicable)
kubectl logs -l app=<label> --tail=100 -f
```

---

## 5. Interactive Practice Exercises

Practice the concepts from this chapter directly in your browser using our client-side WebAssembly environment:

- [**`storage01`**: Volume Types (emptyDir & hostPath)](../playground/index.html?exercise=storage01)
- [**`storage02`**: PersistentVolumes & PersistentVolumeClaims](../playground/index.html?exercise=storage02)
- [**`storage03`**: Access Modes & Reclaim Policies](../playground/index.html?exercise=storage03)
- [**`storage04`**: StorageClasses & Dynamic Provisioning](../playground/index.html?exercise=storage04)
- [**`storage05`**: Volume Snapshots & Volume Expansion](../playground/index.html?exercise=storage05)

<div style="margin-top: 1.5rem;">
  <a href="../playground/index.html?chapter=4" class="md-button md-button--primary">
    ⚡ Practice Chapter 04 in WebAssembly Playground →
  </a>
</div>

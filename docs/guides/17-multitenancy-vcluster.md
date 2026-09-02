# Chapter 17: Multi-Tenancy & Virtual Clusters

<div class="grid cards" markdown>

-   :material-school: **Topic Focus** &bull; Hierarchical Namespace Controller (HNC), Quotas, vcluster, and Tenant Isolation
-   :material-api: **Primary APIs** &bull; `v1`, `hnc.x-k8s.io/v1alpha2` &bull; `ResourceQuota`, `LimitRange`, `HierarchyConfiguration`
-   :material-rocket-launch: [**Launch Playground in Wasm →**](../playground/index.html?chapter=17){ .md-button .md-button--primary }

</div>

---

## 1. Architectural Overview & Control Plane Mechanics

In Kubernetes, **Multi-Tenancy & Virtual Clusters** is reconciled through declarative state loops managed by the control plane:

```text
┌─────────────────────────────────────────────────────────────┐
    │                      Host K8s Cluster                       │
    │  ┌───────────────────────────────────────────────────────┐  │
    │  │               Tenant Namespace: `team-alpha`          │  │
    │  │  ┌─────────────────────────────────────────────────┐  │  │
    │  │  │              vcluster Control Plane             │  │  │
    │  │  │   (Virtual API Server + SQLite/k3s / Syncer)    │  │  │
    │  │  └────────────────────────┬────────────────────────┘  │  │
    │  │                           │ Synced Workload Pods      │  │
    │  │                           ▼                           │  │
    │  │  [ Pod A (synced) ] [ Pod B (synced) ] [ Secret ]     │  │
    │  └───────────────────────────────────────────────────────┘  │
    └─────────────────────────────────────────────────────────────┘
```

When resources in this chapter are submitted, the `kube-apiserver` validates the OpenAPI v3 schema, stores state in `etcd`, and triggers the responsible controllers or node daemons to reconcile actual cluster state.

---

## 2. Annotated Production YAML Anatomy & Field Reference

Below is a production-grade declarative manifest demonstrating field definitions and operational patterns:

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: tenant-quota
  namespace: team-alpha
spec:
  hard:
    requests.cpu: "4"
    requests.memory: 8Gi
    limits.cpu: "8"
    limits.memory: 16Gi
    pods: "20"
    services.loadbalancers: "1"
---
apiVersion: v1
kind: LimitRange
metadata:
  name: tenant-limit-range
  namespace: team-alpha
spec:
  limits:
  - default:
      cpu: "500m"
      memory: "512Mi"
    defaultRequest:
      cpu: "100m"
      memory: "128Mi"
    type: Container
```

### Key Field Schema Reference

| Field | Type | Description |
| :--- | :--- | :--- |
| `ResourceQuota` | `Hard ceiling` | Bounds aggregate compute resources, storage allocations, and object counts across a namespace. |
| `LimitRange` | `Defaults & Bounds` | Injects default resource requests/limits for bare pods and enforces min/max container size constraints. |
| `vcluster` | `Virtual Cluster` | Runs a lightweight, dedicated control plane inside a namespace for full multi-tenant CRD and cluster-admin isolation. |

---

## 3. Real-World Architectural Patterns

### Hierarchical Namespaces (HNC) Tree

```yaml
apiVersion: hnc.x-k8s.io/v1alpha2
kind: HierarchyConfiguration
metadata:
  name: hierarchy
  namespace: team-alpha-staging
spec:
  parent: team-alpha-root
```

### vcluster Helm Values Configuration

```yaml
# vcluster helm configuration for lightweight k3s tenant
syncer:
  extraArgs:
  - --sync-nodes=false
  - --sync-all-secrets=false
isolation:
  enabled: true
  podSecurityStandard: restricted
  resourceQuota:
    enabled: true
    quota:
      requests.cpu: "2"
      requests.memory: 4Gi
```


---

## 4. Production Hardening & Operational Governance

- Combine `ResourceQuota` with `LimitRange` in every tenant namespace to prevent unconstrained pod scheduling from saturating quotas.
- Use `vcluster` when tenants require custom CRDs, independent API versions, or cluster-scoped role simulations.
- Enforce NetworkPolicies between tenant namespaces to eliminate cross-tenant lateral movement.

---

## 5. Failure Modes & Diagnostic Triage Tree

??? failure "`exceeded quota: ... requested: ..., used: ..., limited: ...`"
    **Root Cause:** Tenant namespace has exhausted its ResourceQuota ceiling.

    **Diagnostic Triage Sequence:**
    1. Inspect quota usage: `kubectl describe resourcequota -n <tenant-namespace>`
2. Delete orphaned pods or scale down unused deployments.


---

## 6. Interactive Practice Matrix

Practice concepts from this chapter directly in the interactive WebAssembly sandbox:

| Exercise ID | Challenge Description | Direct Link | Action |
| :--- | :--- | :--- | :--- |
| **`tenant01`** | HNC Hierarchical Subnamespace Anchor | [`../playground/index.html?exercise=tenant01`](../playground/index.html?exercise=tenant01) | [**⚡ Solve in Playground →**](../playground/index.html?exercise=tenant01){ .md-button .md-button--primary } |
| **`tenant02`** | Tenant ResourceQuotas and LimitRanges | [`../playground/index.html?exercise=tenant02`](../playground/index.html?exercise=tenant02) | [**⚡ Solve in Playground →**](../playground/index.html?exercise=tenant02){ .md-button .md-button--primary } |
| **`tenant03`** | Virtual Cluster (vcluster) Control Plane | [`../playground/index.html?exercise=tenant03`](../playground/index.html?exercise=tenant03) | [**⚡ Solve in Playground →**](../playground/index.html?exercise=tenant03){ .md-button .md-button--primary } |
| **`tenant04`** | Multi-Tenant Network Isolation & Egress Filtering | [`../playground/index.html?exercise=tenant04`](../playground/index.html?exercise=tenant04) | [**⚡ Solve in Playground →**](../playground/index.html?exercise=tenant04){ .md-button .md-button--primary } |

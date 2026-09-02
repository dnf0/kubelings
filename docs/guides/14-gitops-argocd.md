# Chapter 14: GitOps Continuous Delivery with ArgoCD

<div class="grid cards" markdown>

-   :material-school: **Topic Focus** &bull; Application CRDs, ApplicationSets, Sync Policies, and Progressive Delivery Rollouts
-   :material-api: **Primary APIs** &bull; `argoproj.io/v1alpha1` &bull; `Application`, `ApplicationSet`, `Rollout`
-   :material-rocket-launch: [**Launch Playground in Wasm →**](../playground/index.html?chapter=14){ .md-button .md-button--primary }

</div>

---

## 1. Architectural Overview & Control Plane Mechanics

In Kubernetes, **GitOps Continuous Delivery with ArgoCD** is reconciled through declarative state loops managed by the control plane:

```text
┌───────────────────────────┐
│     Git Repository        │ ◄── Single Source of Truth (Git Commit / PR)
└─────────────┬─────────────┘
              │ ArgoCD Repo Server Polls / Webhook
              ▼
┌───────────────────────────┐
│  ArgoCD Application Ctrl  │ ◄── Compares Git Desired State vs Cluster Live State
└─────────────┬─────────────┘
              │ Auto-Sync & Self-Healing Reconciliation
              ▼
┌───────────────────────────┐
│    Kubernetes Cluster     │ ──► [ Deployments, Services, ConfigMaps ]
└───────────────────────────┘
```

When resources in this chapter are submitted, the `kube-apiserver` validates the OpenAPI v3 schema, stores state in `etcd`, and triggers the responsible controllers or node daemons to reconcile actual cluster state.

---

## 2. Annotated Production YAML Anatomy & Field Reference

Below is a production-grade declarative manifest demonstrating field definitions and operational patterns:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: production-microservices
  namespace: argocd
  finalizers:
  - resources-finalizer.argocd.argoproj.io
spec:
  project: default
  source:
    repoURL: https://github.com/example-org/k8s-manifests.git
    targetRevision: main
    path: environments/production
  destination:
    server: https://kubernetes.default.svc
    namespace: production
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
    - CreateNamespace=true
    - ApplyOutOfSyncOnly=true
```

### Key Field Schema Reference

| Field | Type | Description |
| :--- | :--- | :--- |
| `spec.source` | `Object` | Git repository URL, branch/tag (`targetRevision`), and directory path containing manifests/Helm/Kustomize. |
| `spec.syncPolicy.automated.prune` | `Boolean` | Deletes cluster resources when their YAML manifests are removed from Git. |
| `spec.syncPolicy.automated.selfHeal` | `Boolean` | Reverts manual out-of-band `kubectl` mutations back to Git state within seconds. |

---

## 3. Real-World Architectural Patterns

### Argo Rollouts Canary with AnalysisTemplate

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: web-rollout
spec:
  replicas: 5
  strategy:
    canary:
      steps:
      - setWeight: 20
      - pause: {duration: 5m}
      - setWeight: 50
      - pause: {duration: 10m}
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
      - name: web
        image: nginx:1.27-alpine
```

### ApplicationSet Matrix Generator

```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: cluster-addons
  namespace: argocd
spec:
  generators:
  - list:
      elements:
      - cluster: dev-cluster
        url: https://dev-k8s.example.com
      - cluster: prod-cluster
        url: https://prod-k8s.example.com
  template:
    metadata:
      name: "{{cluster}}-addons"
    spec:
      project: default
      source:
        repoURL: https://github.com/example/addons.git
        targetRevision: HEAD
        path: "clusters/{{cluster}}"
      destination:
        server: "{{url}}"
        namespace: kube-addons
```


---

## 4. Production Hardening & Operational Governance

- Always enable `prune: true` and `selfHeal: true` in production GitOps pipelines to enforce true declarative reconciliation.
- Use `resources-finalizer.argocd.argoproj.io` to ensure all child resources are cleaned up if an Application is deleted.
- Protect production clusters using ArgoCD AppProjects with restricted destination namespaces and allowed source repositories.

---

## 5. Failure Modes & Diagnostic Triage Tree

??? failure "Application `OutOfSync` / Degraded"
    **Root Cause:** Manifest syntax error or immutable field modification.

    **Diagnostic Triage Sequence:**
    1. Inspect sync status in ArgoCD CLI: `argocd app get <app-name>`
    2. Trigger manual sync with diff: `argocd app sync <app-name> --dry-run`
    3. Check controller logs: `kubectl logs -n argocd -l app.kubernetes.io/name=argocd-application-controller`


---

## 6. Interactive Practice Matrix

Practice concepts from this chapter directly in the interactive WebAssembly sandbox:

| Exercise ID | Challenge Description | Direct Link | Action |
| :--- | :--- | :--- | :--- |
| **`gitops01`** | ArgoCD Application CRD & Sync Policies | [`../playground/index.html?exercise=gitops01`](../playground/index.html?exercise=gitops01) | [**⚡ Solve in Playground →**](../playground/index.html?exercise=gitops01){ .md-button .md-button--primary } |
| **`gitops02`** | ArgoCD ApplicationSet Matrix Generator | [`../playground/index.html?exercise=gitops02`](../playground/index.html?exercise=gitops02) | [**⚡ Solve in Playground →**](../playground/index.html?exercise=gitops02){ .md-button .md-button--primary } |
| **`gitops03`** | Sync Windows, ServerSideApply & Retry Backoff | [`../playground/index.html?exercise=gitops03`](../playground/index.html?exercise=gitops03) | [**⚡ Solve in Playground →**](../playground/index.html?exercise=gitops03){ .md-button .md-button--primary } |
| **`gitops04`** | Progressive Delivery with Argo Rollouts | [`../playground/index.html?exercise=gitops04`](../playground/index.html?exercise=gitops04) | [**⚡ Solve in Playground →**](../playground/index.html?exercise=gitops04){ .md-button .md-button--primary } |

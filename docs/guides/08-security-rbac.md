# Chapter 08: Security, RBAC & Service Accounts

<div class="grid cards" markdown>

-   :material-school: **Topic Focus** &bull; ServiceAccounts, Roles, ClusterRoles, SecurityContext, and PSS
-   :material-api: **Primary APIs** &bull; `rbac.authorization.k8s.io/v1`, `v1` &bull; `Role`, `ClusterRole`, `RoleBinding`, `ServiceAccount`
-   :material-rocket-launch: [**Launch Playground in Wasm →**](../playground/index.html?chapter=8){ .md-button .md-button--primary }

</div>

---

## 1. Architectural Overview & Control Plane Mechanics

In Kubernetes, **Security, RBAC & Service Accounts** is reconciled through declarative state loops managed by the control plane:

```text
┌───────────────────────────┐
│      ServiceAccount       │ ◄── Injected into Pod JWT Token
└─────────────┬─────────────┘
              │ Bound via RoleBinding
              ▼
┌───────────────────────────┐
│     Role / ClusterRole    │ ◄── Rules: apiGroups, resources, verbs
└─────────────┬─────────────┘
              │ Authorizes
              ▼
┌───────────────────────────┐
│       kube-apiserver      │ ──► [ GET /api/v1/namespaces/default/pods ] ✓
└───────────────────────────┘
```

When resources in this chapter are submitted, the `kube-apiserver` validates the OpenAPI v3 schema, stores state in `etcd`, and triggers the responsible controllers or node daemons to reconcile actual cluster state.

---

## 2. Annotated Production YAML Anatomy & Field Reference

Below is a production-grade declarative manifest demonstrating field definitions and operational patterns:

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: deployment-manager
  namespace: production
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: deployment-operator
  namespace: production
rules:
- apiGroups: ["apps"]
  resources: ["deployments", "replicasets"]
  verbs: ["get", "list", "watch", "create", "update", "patch"]
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: bind-deployment-operator
  namespace: production
subjects:
- kind: ServiceAccount
  name: deployment-manager
  namespace: production
roleRef:
  kind: Role
  name: deployment-operator
  apiGroup: rbac.authorization.k8s.io
```

### Key Field Schema Reference

| Field | Type | Description |
| :--- | :--- | :--- |
| `rules[*].apiGroups` | `Array` | Target API group (`""` for core v1, `"apps"`, `"networking.k8s.io"`). |
| `rules[*].resources` | `Array` | Kubernetes resource nouns (`pods`, `deployments`, `configmaps`). |
| `rules[*].verbs` | `Array` | Permitted operations (`get`, `list`, `watch`, `create`, `update`, `patch`, `delete`). |

---

## 3. Real-World Architectural Patterns

### ClusterRole for Cross-Namespace Read-Only Audit

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: cluster-viewer
rules:
- apiGroups: ["", "apps", "batch", "networking.k8s.io"]
  resources: ["*"]
  verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: bind-cluster-viewer
subjects:
- kind: ServiceAccount
  name: auditor
  namespace: security-tools
roleRef:
  kind: ClusterRole
  name: cluster-viewer
  apiGroup: rbac.authorization.k8s.io
```

### Pod Security Standard Restricted SecurityContext

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: hardened-secure-pod
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 10001
    runAsGroup: 10001
    fsGroup: 10001
    seccompProfile:
      type: RuntimeDefault
  containers:
  - name: secure-app
    image: alpine:3.20
    command: ["sleep", "3600"]
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop:
        - ALL
```


---

## 4. Production Hardening & Operational Governance

- Follow the Principle of Least Privilege: never grant wildcard `*` permissions in production RoleBindings.
- Disable automatic ServiceAccount token mounting with `automountServiceAccountToken: false` on pods that do not interact with the API Server.
- Enforce Pod Security Standards (`pod-security.kubernetes.io/enforce: restricted`) at the Namespace level.

---

## 5. Failure Modes & Diagnostic Triage Tree

??? failure "API Request `403 Forbidden`"
    **Root Cause:** ServiceAccount lacks RBAC verb or resource permission.

    **Diagnostic Triage Sequence:**
    1. Test authorization: `kubectl auth can-i create deployments --as=system:serviceaccount:production:deployment-manager -n production`
    2. Inspect RoleBinding subjects and roleRef matching.


---

## 6. Interactive Practice Matrix

Practice concepts from this chapter directly in the interactive WebAssembly sandbox:

| Exercise ID | Challenge Description | Direct Link | Action |
| :--- | :--- | :--- | :--- |
| **`rbac01`** | ServiceAccounts & Token Management | [`../playground/index.html?exercise=rbac01`](../playground/index.html?exercise=rbac01) | [**⚡ Solve in Playground →**](../playground/index.html?exercise=rbac01){ .md-button .md-button--primary } |
| **`rbac02`** | Roles & RoleBindings | [`../playground/index.html?exercise=rbac02`](../playground/index.html?exercise=rbac02) | [**⚡ Solve in Playground →**](../playground/index.html?exercise=rbac02){ .md-button .md-button--primary } |
| **`rbac03`** | ClusterRoles & ClusterRoleBindings | [`../playground/index.html?exercise=rbac03`](../playground/index.html?exercise=rbac03) | [**⚡ Solve in Playground →**](../playground/index.html?exercise=rbac03){ .md-button .md-button--primary } |
| **`rbac04`** | Pod & Container SecurityContext | [`../playground/index.html?exercise=rbac04`](../playground/index.html?exercise=rbac04) | [**⚡ Solve in Playground →**](../playground/index.html?exercise=rbac04){ .md-button .md-button--primary } |
| **`rbac05`** | Pod Security Standards (PSS/PSA) | [`../playground/index.html?exercise=rbac05`](../playground/index.html?exercise=rbac05) | [**⚡ Solve in Playground →**](../playground/index.html?exercise=rbac05){ .md-button .md-button--primary } |

# Chapter 03: Configuration & Secret Management

<div class="grid cards" markdown>

-   :material-school: **Topic Focus** &bull; ConfigMaps, Secrets, In-Memory Mounts, and Immutability
-   :material-api: **Primary APIs** &bull; `v1` &bull; `ConfigMap`, `Secret`
-   :material-rocket-launch: [**Launch Playground in Wasm →**](../playground/index.html?chapter=3){ .md-button .md-button--primary }

</div>

!!! tip "⚡ Interactive Problems in this Chapter (Click to solve in Playground)"
    - [**`config01`**: ConfigMaps as Environment Variables →](../playground/index.html?exercise=config01)
    - [**`config02`**: ConfigMaps Mounted as Volumes →](../playground/index.html?exercise=config02)
    - [**`config03`**: Secrets & Base64 Encoding →](../playground/index.html?exercise=config03)
    - [**`config04`**: Secret Volume Mounts & Permissions →](../playground/index.html?exercise=config04)
    - [**`config05`**: Immutable ConfigMaps and Secrets →](../playground/index.html?exercise=config05)

---

## 1. Architectural Overview & Control Plane Mechanics

In Kubernetes, **Configuration & Secret Management** is reconciled through declarative state loops managed by the control plane:

```text
┌─────────────────────────────────────────────────────────────┐
│                      Kubernetes API                         │
│   ┌────────────────────┐          ┌─────────────────────┐   │
│   │  ConfigMap (Plain) │          │ Secret (Base64/KMS) │   │
│   └─────────┬──────────┘          └──────────┬──────────┘   │
└─────────────┼────────────────────────────────┼──────────────┘
              │                                │
              ▼ Mounted as Files / Env Vars    ▼
┌─────────────────────────────────────────────────────────────┐
│                         Pod Spec                            │
│  • envFrom: configMapRef / secretRef                        │
│  • volumes.configMap -> /etc/config                         │
│  • volumes.secret    -> /etc/secrets (tmpfs memory)         │
└─────────────────────────────────────────────────────────────┘
```

When resources in this chapter are submitted, the `kube-apiserver` validates the OpenAPI v3 schema, stores state in `etcd`, and triggers the responsible controllers or node daemons to reconcile actual cluster state.

---

## 2. Annotated Production YAML Anatomy & Field Reference

Below is a production-grade declarative manifest demonstrating field definitions and operational patterns:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: default
data:
  APP_ENV: "production"
  LOG_LEVEL: "info"
  nginx.conf: |
    events { worker_connections 1024; }
    http {
      server {
        listen 80;
        location / { return 200 "OK"; }
      }
    }
---
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
  namespace: default
type: Opaque
stringData:
  DB_PASSWORD: "super-secure-production-password"
  API_KEY: "secret-token-xyz-123"
```

### Key Field Schema Reference

| Field | Type | Description |
| :--- | :--- | :--- |
| `data` vs `stringData` | `Map` | `data` expects base64 encoded strings; `stringData` accepts raw text and is auto-encoded on write. |
| `immutable: true` | `Boolean` | Protects against accidental config modification and reduces kube-apiserver watch load. |
| `envFrom.configMapRef` | `Object` | Exposes all key-value pairs in a ConfigMap as individual container environment variables. |

---

## 3. Real-World Architectural Patterns

### Projected Volume Config Injection

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: projected-config-pod
spec:
  containers:
  - name: app
    image: alpine:3.20
    command: ["sh", "-c", "ls -la /etc/config && sleep 3600"]
    volumeMounts:
    - name: config-bundle
      mountPath: /etc/config
      readOnly: true
  volumes:
  - name: config-bundle
    projected:
      sources:
      - configMap:
          name: app-config
      - secret:
          name: app-secrets
```

### Immutable Configuration Pattern

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: static-routing-table-v1
immutable: true
data:
  routes.json: |
    {"/api/v1": "http://api-v1", "/api/v2": "http://api-v2"}
```


---

## 4. Production Hardening & Operational Governance

- Store sensitive data exclusively in `Secret` resources backed by KMS envelope encryption or external vault integrations (External Secrets Operator).
- Set `immutable: true` on ConfigMaps and Secrets used with immutable deployment pipelines to eliminate drift.
- Always mount Secret volumes with `readOnly: true` to prevent unauthorized in-pod file manipulation.

---

## 5. Failure Modes & Diagnostic Triage Tree

??? failure "`CreateContainerConfigError`"
    **Root Cause:** Referenced ConfigMap or Secret does not exist or key name is misspelled.

    **Diagnostic Triage Sequence:**
    1. Run `kubectl describe pod <name>` and inspect the exact missing key.
    2. Check namespace: `kubectl get configmap,secret -n <namespace>`.

??? failure "Live ConfigMap Update Not Reflected in Pod"
    **Root Cause:** ConfigMaps injected as environment variables are static and require pod restart; volume mounts take up to kubelet sync period (default ~60s).

    **Diagnostic Triage Sequence:**
    1. Trigger rolling restart: `kubectl rollout restart deployment/<name>`.


---

## 6. Interactive Practice Matrix

Practice concepts from this chapter directly in the interactive WebAssembly sandbox:

| Exercise ID | Challenge Description | Direct Link | Action |
| :--- | :--- | :--- | :--- |
| **`config01`** | ConfigMaps as Environment Variables | [`../playground/index.html?exercise=config01`](../playground/index.html?exercise=config01) | [**⚡ Solve `config01` in Playground →**](../playground/index.html?exercise=config01){ .md-button .md-button--primary } |
| **`config02`** | ConfigMaps Mounted as Volumes | [`../playground/index.html?exercise=config02`](../playground/index.html?exercise=config02) | [**⚡ Solve `config02` in Playground →**](../playground/index.html?exercise=config02){ .md-button .md-button--primary } |
| **`config03`** | Secrets & Base64 Encoding | [`../playground/index.html?exercise=config03`](../playground/index.html?exercise=config03) | [**⚡ Solve `config03` in Playground →**](../playground/index.html?exercise=config03){ .md-button .md-button--primary } |
| **`config04`** | Secret Volume Mounts & Permissions | [`../playground/index.html?exercise=config04`](../playground/index.html?exercise=config04) | [**⚡ Solve `config04` in Playground →**](../playground/index.html?exercise=config04){ .md-button .md-button--primary } |
| **`config05`** | Immutable ConfigMaps and Secrets | [`../playground/index.html?exercise=config05`](../playground/index.html?exercise=config05) | [**⚡ Solve `config05` in Playground →**](../playground/index.html?exercise=config05){ .md-button .md-button--primary } |

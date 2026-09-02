# Chapter 18: Advanced Admission Webhooks

<div class="grid cards" markdown>

-   :material-school: **Topic Focus** &bull; Mutating & Validating Webhooks, Sidecar Injection, and CRD Conversion
-   :material-api: **Primary APIs** &bull; `admissionregistration.k8s.io/v1` &bull; `MutatingWebhookConfiguration`, `ValidatingWebhookConfiguration`
-   :material-rocket-launch: [**Launch Playground in Wasm →**](../playground/index.html?chapter=18){ .md-button .md-button--primary }

</div>

!!! tip "⚡ Interactive Problems in this Chapter (Click to solve in Playground)"
    - [**`webhook01`**: MutatingWebhookConfiguration Manifest →](../playground/index.html?exercise=webhook01)
    - [**`webhook02`**: ValidatingWebhookConfiguration Manifest →](../playground/index.html?exercise=webhook02)
    - [**`webhook03`**: Dynamic Sidecar Injection AdmissionReview Response →](../playground/index.html?exercise=webhook03)
    - [**`webhook04`**: CRD Webhook Conversion Strategy →](../playground/index.html?exercise=webhook04)

---

## 1. Architectural Overview & Control Plane Mechanics

In Kubernetes, **Advanced Admission Webhooks** is reconciled through declarative state loops managed by the control plane:

```mermaid
flowchart TD
    subgraph APIServerPipeline["kube-apiserver Admission Processing"]
        REQ["kubectl / API Request"]
        MUTATING["1. Mutating Admission Webhook Phase<br/><i>(Sequential Invocations)</i>"]
        SCHEMA["2. Object Schema Validation & Immutability"]
        VALIDATING["3. Validating Admission Webhook Phase<br/><i>(Parallel Invocations)</i>"]
        PERSIST[("etcd Storage")]

        REQ --> MUTATING
        MUTATING --> SCHEMA
        SCHEMA --> VALIDATING
        VALIDATING --> PERSIST
    end

    subgraph WebhookServices["Webhook Servers (mTLS Secured)"]
        MUT_HOOK["Mutating Webhook Pod<br/><i>(Patches JSON: Add Vault Sidecar)</i>"]
        VAL_HOOK["Validating Webhook Pod<br/><i>(Rejects Missing Resource Limits)</i>"]

        MUTATING -->|POST AdmissionReview| MUT_HOOK
        MUT_HOOK -->|Returns JSONPatch| MUTATING

        VALIDATING -->|POST AdmissionReview| VAL_HOOK
        VAL_HOOK -->|Allowed: true/false| VALIDATING
    end
```

When resources in this chapter are submitted, the `kube-apiserver` validates the OpenAPI v3 schema, stores state in `etcd`, and triggers the responsible controllers or node daemons to reconcile actual cluster state.

---

## 2. Annotated Production YAML Anatomy & Field Reference

Below is a production-grade declarative manifest demonstrating field definitions and operational patterns:

```yaml
apiVersion: admissionregistration.k8s.io/v1
kind: ValidatingWebhookConfiguration
metadata:
  name: strict-image-validator
webhooks:
- name: image-validator.security.example.com
  rules:
  - apiGroups: [""]
    apiVersions: ["v1"]
    operations: ["CREATE", "UPDATE"]
    resources: ["pods"]
    scope: "Namespaced"
  clientConfig:
    service:
      name: webhook-service
      namespace: security-system
      path: "/validate-images"
      port: 443
    caBundle: "LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCg=="
  admissionReviewVersions: ["v1"]
  sideEffects: None
  timeoutSeconds: 3
  failurePolicy: Fail
```

### Key Field Schema Reference

| Field | Type | Description |
| :--- | :--- | :--- |
| `failurePolicy` | `Enum` | `Fail` (rejects API request if webhook times out or crashes) or `Ignore` (allows request through upon failure). |
| `clientConfig.caBundle` | `Base64` | PEM-encoded CA certificate used by API Server to verify the webhook server TLS certificate. |
| `sideEffects: None` | `Enum` | Guarantees the webhook has no out-of-band side effects on dry-run requests. |

---

## 3. Real-World Architectural Patterns

### Mutating Webhook for Sidecar Injection

```yaml
apiVersion: admissionregistration.k8s.io/v1
kind: MutatingWebhookConfiguration
metadata:
  name: sidecar-injector
webhooks:
- name: sidecar.inject.example.com
  rules:
  - apiGroups: [""]
    apiVersions: ["v1"]
    operations: ["CREATE"]
    resources: ["pods"]
  clientConfig:
    service:
      name: injector-service
      namespace: default
      path: "/mutate"
  admissionReviewVersions: ["v1"]
  sideEffects: None
  failurePolicy: Ignore
```

### Namespace Exclusion Selector

```yaml
# Webhook configuration with namespaceSelector to exclude system components
apiVersion: admissionregistration.k8s.io/v1
kind: ValidatingWebhookConfiguration
metadata:
  name: app-validator
webhooks:
- name: validator.example.com
  rules:
  - apiGroups: ["apps"]
    apiVersions: ["v1"]
    operations: ["CREATE"]
    resources: ["deployments"]
  namespaceSelector:
    matchExpressions:
    - key: kubernetes.io/metadata.name
      operator: NotIn
      values: ["kube-system", "kube-public"]
  clientConfig:
    service:
      name: validator-svc
      namespace: default
      path: "/validate"
  admissionReviewVersions: ["v1"]
  sideEffects: None
```


---

## 4. Production Hardening & Operational Governance

- Always set `namespaceSelector` to exclude `kube-system` from webhooks to prevent circular bricking of control plane restarts.
- Use `timeoutSeconds: 3` (or less) to prevent slow webhooks from stalling kube-apiserver admission pipelines.
- Use `cert-manager` CA injector to automatically maintain `caBundle` synchronization.

---

## 5. Failure Modes & Diagnostic Triage Tree

??? failure "`Internal error occurred: failed calling webhook ... connection refused`"
    **Root Cause:** Webhook server pod is dead or unreachable over TLS.

    **Diagnostic Triage Sequence:**
    1. Inspect webhook server logs: `kubectl logs -n <namespace> -l app=<webhook-name>`
    2. Temporarily switch `failurePolicy: Ignore` to restore cluster operations during emergencies.


---

## 6. Interactive Practice Matrix

Practice concepts from this chapter directly in the interactive WebAssembly sandbox:

| Exercise ID | Challenge Description | Direct Link | Action |
| :--- | :--- | :--- | :--- |
| **`webhook01`** | MutatingWebhookConfiguration Manifest | [`../playground/index.html?exercise=webhook01`](../playground/index.html?exercise=webhook01) | [**⚡ Solve `webhook01` in Playground →**](../playground/index.html?exercise=webhook01){ .md-button .md-button--primary } |
| **`webhook02`** | ValidatingWebhookConfiguration Manifest | [`../playground/index.html?exercise=webhook02`](../playground/index.html?exercise=webhook02) | [**⚡ Solve `webhook02` in Playground →**](../playground/index.html?exercise=webhook02){ .md-button .md-button--primary } |
| **`webhook03`** | Dynamic Sidecar Injection AdmissionReview Response | [`../playground/index.html?exercise=webhook03`](../playground/index.html?exercise=webhook03) | [**⚡ Solve `webhook03` in Playground →**](../playground/index.html?exercise=webhook03){ .md-button .md-button--primary } |
| **`webhook04`** | CRD Webhook Conversion Strategy | [`../playground/index.html?exercise=webhook04`](../playground/index.html?exercise=webhook04) | [**⚡ Solve `webhook04` in Playground →**](../playground/index.html?exercise=webhook04){ .md-button .md-button--primary } |

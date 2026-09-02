# Chapter 22: Infrastructure as Data with Crossplane

<div class="grid cards" markdown>

-   :material-school: **Topic Focus** &bull; CompositeResourceDefinitions (XRDs), Compositions, Managed Resources, and Developer Claims
-   :material-api: **Primary APIs** &bull; `apiextensions.crossplane.io/v1`, `pkg.crossplane.io/v1` &bull; `CompositeResourceDefinition`, `Composition`
-   :material-rocket-launch: [**Launch Playground in Wasm →**](../playground/index.html?chapter=22){ .md-button .md-button--primary }

</div>

---

## 1. Architectural Overview & Control Plane Mechanics

In Kubernetes, **Infrastructure as Data with Crossplane** is reconciled through declarative state loops managed by the control plane:

```text
┌───────────────────────────┐
│     Application Dev       │ ──► Declares Composite Resource Claim (XRC)
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│        Composition        │ ◄── Platform Team Blueprint
└─────────────┬─────────────┘
              │ Composes Managed Resources (MR)
      ┌───────┴───────┐
      ▼               ▼
┌───────────┐   ┌───────────┐
│  AWS RDS  │   │  AWS S3   │ ◄── External Cloud Providers
│  Instance │   │  Bucket   │
└───────────┘   └───────────┘
```

When resources in this chapter are submitted, the `kube-apiserver` validates the OpenAPI v3 schema, stores state in `etcd`, and triggers the responsible controllers or node daemons to reconcile actual cluster state.

---

## 2. Annotated Production YAML Anatomy & Field Reference

Below is a production-grade declarative manifest demonstrating field definitions and operational patterns:

```yaml
apiVersion: apiextensions.crossplane.io/v1
kind: CompositeResourceDefinition
metadata:
  name: xpostgresqlinstances.database.example.org
spec:
  group: database.example.org
  names:
    kind: XPostgreSQLInstance
    plural: xpostgresqlinstances
  claimNames:
    kind: PostgreSQLInstance
    plural: postgresqlinstances
  versions:
  - name: v1alpha1
    served: true
    referenceable: true
    schema:
      openAPIV3Schema:
        type: object
        properties:
          spec:
            type: object
            required: ["storageGB"]
            properties:
              storageGB:
                type: integer
```

### Key Field Schema Reference

| Field | Type | Description |
| :--- | :--- | :--- |
| `CompositeResourceDefinition` (XRD) | `API Contract` | Defines the custom schema exposed to application developers. |
| `Composition` | `Infrastructure Template` | Binds the XRD to specific Managed Resources (e.g. AWS RDS, GCP CloudSQL). |
| `Managed Resource` (MR) | `Cloud Primitive` | Direct representation of cloud resources with continuous state reconciliation. |

---

## 3. Real-World Architectural Patterns

### Application Developer Claim (XRC)

```yaml
apiVersion: database.example.org/v1alpha1
kind: PostgreSQLInstance
metadata:
  name: app-database
  namespace: default
spec:
  storageGB: 20
```

### ProviderConfig IAM Configuration

```yaml
apiVersion: aws.upbound.io/v1beta1
kind: ProviderConfig
metadata:
  name: default
spec:
  credentials:
    source: IRSA
```


---

## 4. Production Hardening & Operational Governance

- Use IAM Roles for Service Accounts (IRSA / Workload Identity) rather than static long-lived cloud API keys.
- Lock Composition schemas with strict validation and automated drift detection.
- Protect critical databases from accidental deletion with `deletionPolicy: Orphan`.

---

## 5. Failure Modes & Diagnostic Triage Tree

??? failure "Managed Resource `Ready=False` / `Synced=False`"
    **Root Cause:** Cloud provider authentication failure or parameter validation error.

    **Diagnostic Triage Sequence:**
    1. Run `kubectl describe <managed-resource> <name>`
2. Verify ProviderConfig status: `kubectl get providerconfigs`.


---

## 6. Interactive Practice Matrix

Practice concepts from this chapter directly in the interactive WebAssembly sandbox:

| Exercise ID | Challenge Description | Direct Link | Action |
| :--- | :--- | :--- | :--- |
| **`crossplane01`** | CompositeResourceDefinition (XRD) Schema | [`../playground/index.html?exercise=crossplane01`](../playground/index.html?exercise=crossplane01) | [**⚡ Solve in Playground →**](../playground/index.html?exercise=crossplane01){ .md-button .md-button--primary } |
| **`crossplane02`** | Composition and Field Path Transforms | [`../playground/index.html?exercise=crossplane02`](../playground/index.html?exercise=crossplane02) | [**⚡ Solve in Playground →**](../playground/index.html?exercise=crossplane02){ .md-button .md-button--primary } |
| **`crossplane03`** | ProviderConfig and Resource Deletion Policies | [`../playground/index.html?exercise=crossplane03`](../playground/index.html?exercise=crossplane03) | [**⚡ Solve in Playground →**](../playground/index.html?exercise=crossplane03){ .md-button .md-button--primary } |
| **`crossplane04`** | Developer Self-Service Claims & Connection Secrets | [`../playground/index.html?exercise=crossplane04`](../playground/index.html?exercise=crossplane04) | [**⚡ Solve in Playground →**](../playground/index.html?exercise=crossplane04){ .md-button .md-button--primary } |

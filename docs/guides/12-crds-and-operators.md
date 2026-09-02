# Chapter 12: Custom Resources, CRDs & Operators

<div class="grid cards" markdown>

-   :material-school: **Topic Focus** &bull; CRD Schemas, Subresources, Python Operator Loops, and Webhooks
-   :material-api: **Primary APIs** &bull; `apiextensions.k8s.io/v1` &bull; `CustomResourceDefinition`
-   :material-rocket-launch: [**Launch Playground in Wasm →**](../playground/index.html?chapter=12){ .md-button .md-button--primary }

</div>

!!! tip "⚡ Interactive Problems in this Chapter (Click to solve in Playground)"
    - [**`crd01`**: CustomResourceDefinition (CRD) Schema →](../playground/index.html?exercise=crd01)
    - [**`crd02`**: CRD Subresources & Printer Columns →](../playground/index.html?exercise=crd02)
    - [**`crd03`**: Python Kubernetes Operator Loop →](../playground/index.html?exercise=crd03)
    - [**`crd04`**: Dynamic Admission Webhooks →](../playground/index.html?exercise=crd04)

---

## 1. Architectural Overview & Control Plane Mechanics

In Kubernetes, **Custom Resources, CRDs & Operators** is reconciled through declarative state loops managed by the control plane and node daemons:

```mermaid
flowchart TD
    subgraph OpenAPIValidation["1. Schema Registration"]
        CRD["CustomResourceDefinition (CRD)<br/><code>group: database.example.com</code><br/><code>kind: PostgreSQLCluster</code>"]
        APISERVER["kube-apiserver<br/><i>OpenAPI v3 Validation & Storage</i>"]
        CRD --> APISERVER
    end

    subgraph OperatorEngine["2. Operator Controller Loop (Kopf / Kube-rs)"]
        INFORMER["SharedInformer & Reflector<br/><i>List-Watch Local Cache</i>"]
        QUEUE["WorkQueue (RateLimitingQueue)"]
        RECONCILER["Reconciliation Function (Python / Go)<br/><code>def reconcile(spec, status):</code>"]

        APISERVER -->|Watch Events (ADD, UPDATE, DEL)| INFORMER
        INFORMER --> QUEUE
        QUEUE --> RECONCILER
    end

    subgraph ManagedResources["3. Actuation & Status"]
        STATEFULSET["Managed StatefulSets & PVCs"]
        SERVICE["Managed ClusterIP & Secrets"]
        STATUS["Update <code>.status.conditions</code>"]

        RECONCILER -->|Creates/Updates| STATEFULSET
        RECONCILER -->|Creates/Updates| SERVICE
        RECONCILER -->|Reports State| STATUS
        STATUS --> APISERVER
    end
```

### 1.1 Architectural Flow & Lifecycle Walkthrough

1. **CRD Registration & OpenAPI Schema Ingestion**: An administrator submits a `CustomResourceDefinition` (CRD) object (e.g. `postgresqlclusters.database.example.com`). `kube-apiserver` registers the new REST endpoints (`/apis/database.example.com/v1/...`), validates the embedded OpenAPI v3 structural schema, and establishes storage mappings in `etcd`.
2. **Custom Resource (CR) Ingestion**: A developer submits a Custom Resource instance (e.g., `kind: PostgreSQLCluster`, `spec: { replicas: 3, storageGB: 50 }`). The API server validates the CR against the CRD's OpenAPI schema, rejects any malformed types, and stores the object.
3. **Operator Informer Watch & Queueing**: The Operator process (written in Go with `controller-runtime`, Python with `Kopf`, or Rust with `kube-rs`) runs inside the cluster. Its `SharedIndexInformer` receives an `ADDED` or `MODIFIED` watch event from `kube-apiserver` and enqueues the resource key into a `RateLimitingWorkQueue`.
4. **Reconciliation Loop Execution**: The operator reconciles desired vs actual state:
   - Queries the cluster for child resources owned by the CR (StatefulSets, Services, ConfigMaps, Secrets).
   - If child resources are missing or drift from the CR spec, the operator issues API calls to create or update them.
   - Executes out-of-band operational tasks (e.g., running `pg_basebackup` or initializing database replication).
5. **Status & Condition Reporting**: The operator issues an HTTP `PATCH` to the CR's `/status` subresource, updating `.status.conditions` (e.g., `Type: Ready, Status: True, Message: "Primary and 2 standbys active"`) and increments `.status.observedGeneration`.

### 1.2 Serialization, Protocols & Communication Pathways

- **OpenAPI v3 JSON Schema Validation**: The API server enforces schema contracts defined in the CRD spec (`openAPIV3Schema`) before persisting custom resources.
- **Server-Side Apply (SSA) YAML/JSON Protocol**: Modern operators use Server-Side Apply (`PATCH` with `Content-Type: application/apply-patch+yaml`), specifying `fieldManager: postgres-operator` to declare explicit field ownership and detect conflicting mutations.
- **Dynamic Watch JSON Streams**: Custom resources are streamed over HTTP/2 chunked streams to client-go informers using JSON or Protobuf (for CRDs supporting Protobuf serialization).

### 1.3 Deep-Dive Component Breakdown

- **CustomResourceDefinition (CRD)**: Kubernetes extension mechanism defining new resource types, versions, validation schemas, and subresources (`/status`, `/scale`).
- **Operator / Custom Controller**: Domain-specific software agent packaging operational knowledge (backup, failover, upgrades, scaling) for complex stateful applications.
- **OwnerReferences & Garbage Collection**: Child resources are stamped with `metadata.ownerReferences` pointing to the parent CR. When the parent CR is deleted, the Kubernetes Garbage Collector automatically deletes all child resources via cascading deletion.
- **Finalizers (`metadata.finalizers`)**: Asynchronous pre-deletion hooks (e.g., `database.example.com/clean-cloud-disks`) that prevent immediate object deletion in `etcd` until the operator completes external teardown tasks and removes the finalizer string.

### 1.4 Under-The-Hood Mechanics & Failure Modes

- **Deadlock on Stuck Finalizers**: If an operator crashes or is uninstalled while custom resources remain with active `metadata.finalizers`, attempts to delete the custom resources hang indefinitely in `Terminating` state until finalizers are manually patched out.
- **Infinite Reconciliation Loops**: If an operator modifies a field in `.spec` during reconciliation (instead of `.status`), the modification triggers a new `MODIFIED` watch event, causing the operator to endlessly re-reconcile itself and saturate API server resources.
- **CRD Version Conversion Webhook Timeouts**: When supporting multiple CRD API versions (`v1alpha1`, `v1`), version conversion webhooks must deserialize and translate schemas. If the conversion webhook service is unreachable, all API operations across older versions fail with `ConversionWebhookFailed`.

---

## 2. Annotated Production YAML Anatomy & Field Reference

Below is a production-grade declarative manifest demonstrating field definitions and operational patterns:

```yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: databaseclusters.storage.example.com
spec:
  group: storage.example.com
  names:
    plural: databaseclusters
    singular: databasecluster
    kind: DatabaseCluster
    shortNames:
    - dbc
  scope: Namespaced
  versions:
  - name: v1alpha1
    served: true
    storage: true
    subresources:
      status: {}
      scale:
        specReplicasPath: .spec.replicas
        statusReplicasPath: .status.replicas
    schema:
      openAPIV3Schema:
        type: object
        required: ["spec"]
        properties:
          spec:
            type: object
            required: ["engine", "replicas"]
            properties:
              engine:
                type: string
                enum: ["postgres", "mysql", "redis"]
              replicas:
                type: integer
                minimum: 1
                maximum: 10
              storageSize:
                type: string
                pattern: "^[0-9]+(Gi|Mi)$"
          status:
            type: object
            properties:
              phase:
                type: string
              replicas:
                type: integer
```

### Key Field Schema Reference

| Field | Type | Description |
| :--- | :--- | :--- |
| `spec.scope` | `Enum` | `Namespaced` (resources live in namespaces) or `Cluster` (cluster-wide). |
| `spec.versions[*].subresources.status` | `Object` | Enables `/status` subresource; separates spec updates from status updates. |
| `spec.versions[*].schema.openAPIV3Schema` | `Object` | Strict structural schema validation enforced by the API Server on write. |

---

## 3. Real-World Architectural Patterns

### Custom Resource Instance (CR)

```yaml
apiVersion: storage.example.com/v1alpha1
kind: DatabaseCluster
metadata:
  name: primary-postgres
  namespace: default
spec:
  engine: postgres
  replicas: 3
  storageSize: 50Gi
```

### CRD with Additional Printer Columns

```yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: backups.storage.example.com
spec:
  group: storage.example.com
  names:
    kind: Backup
    plural: backups
  scope: Namespaced
  versions:
  - name: v1
    served: true
    storage: true
    additionalPrinterColumns:
    - name: Status
      type: string
      jsonPath: .status.phase
    - name: Age
      type: date
      jsonPath: .metadata.creationTimestamp
    schema:
      openAPIV3Schema:
        type: object
        properties:
          spec:
            type: object
```


---

## 4. Production Hardening & Operational Governance

- Always include complete OpenAPI v3 validation schemas with `type`, `required`, and `enum` bounds to prevent invalid state persistence.
- Use `/status` subresources so operator reconciliation updates do not conflict with user spec mutations.
- Follow Kubernetes API versioning conventions (`v1alpha1` &rarr; `v1beta1` &rarr; `v1`) and use conversion webhooks when altering stored schemas.

---

## 5. Failure Modes & Diagnostic Triage Tree

??? failure "`error: unable to recognize "cr.yaml": no matches for kind`"
    **Root Cause:** CRD is not registered, or apiVersion group/version is mismatched.

    **Diagnostic Triage Sequence:**
    1. Check registered CRDs: `kubectl get crds`
    2. Verify served API versions: `kubectl get crd <name> -o yaml`.


---

## 6. Interactive Practice Matrix

Practice concepts from this chapter directly in the interactive WebAssembly sandbox:

| Exercise ID | Challenge Description | Direct Link | Action |
| :--- | :--- | :--- | :--- |
| **`crd01`** | CustomResourceDefinition (CRD) Schema | [`../playground/index.html?exercise=crd01`](../playground/index.html?exercise=crd01) | [**⚡ Solve `crd01` in Playground →**](../playground/index.html?exercise=crd01){ .md-button .md-button--primary } |
| **`crd02`** | CRD Subresources & Printer Columns | [`../playground/index.html?exercise=crd02`](../playground/index.html?exercise=crd02) | [**⚡ Solve `crd02` in Playground →**](../playground/index.html?exercise=crd02){ .md-button .md-button--primary } |
| **`crd03`** | Python Kubernetes Operator Loop | [`../playground/index.html?exercise=crd03`](../playground/index.html?exercise=crd03) | [**⚡ Solve `crd03` in Playground →**](../playground/index.html?exercise=crd03){ .md-button .md-button--primary } |
| **`crd04`** | Dynamic Admission Webhooks | [`../playground/index.html?exercise=crd04`](../playground/index.html?exercise=crd04) | [**⚡ Solve `crd04` in Playground →**](../playground/index.html?exercise=crd04){ .md-button .md-button--primary } |

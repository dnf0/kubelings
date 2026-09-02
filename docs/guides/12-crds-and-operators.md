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

In Kubernetes, **Custom Resources, CRDs & Operators** is reconciled through declarative state loops managed by the control plane:

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

When resources in this chapter are submitted, the `kube-apiserver` validates the OpenAPI v3 schema, stores state in `etcd`, and triggers the responsible controllers or node daemons to reconcile actual cluster state.

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

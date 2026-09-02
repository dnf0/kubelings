# Chapter 16: Policy as Code (Kyverno & Gatekeeper)

<div class="grid cards" markdown>

-   :material-school: **Topic Focus** &bull; Kyverno ClusterPolicies, Mutating & Generate rules, and OPA Gatekeeper Constraints
-   :material-api: **Primary APIs** &bull; `kyverno.io/v1`, `templates.gatekeeper.sh/v1` &bull; `ClusterPolicy`, `ConstraintTemplate`
-   :material-rocket-launch: [**Launch Playground in Wasm →**](../playground/index.html?chapter=16){ .md-button .md-button--primary }

</div>

!!! tip "⚡ Interactive Problems in this Chapter (Click to solve in Playground)"
    - [**`policy01`**: Kyverno ClusterPolicy for Required Labels →](../playground/index.html?exercise=policy01)
    - [**`policy02`**: Kyverno Mutating Policy for Security Defaults →](../playground/index.html?exercise=policy02)
    - [**`policy03`**: Kyverno Generate Policy for Default Deny NetworkPolicy →](../playground/index.html?exercise=policy03)
    - [**`policy04`**: OPA Gatekeeper ConstraintTemplate & Constraint →](../playground/index.html?exercise=policy04)

---

## 1. Architectural Overview & Control Plane Mechanics

In Kubernetes, **Policy as Code (Kyverno & Gatekeeper)** is reconciled through declarative state loops managed by the control plane and node daemons:

```mermaid
flowchart TD
    subgraph APIPipeline["API Admission Request Pipeline"]
        REQ["Admission Request (e.g. Create Pod)"]
        APISERVER["kube-apiserver Admission Pipeline"]
        REQ --> APISERVER
    end

    subgraph PolicyEngine["Kyverno / OPA Gatekeeper Engine"]
        MUTATE["1. Mutate Phase<br/><i>(Inject securityContext, labels, sidecars)</i>"]
        GENERATE["2. Generate Phase<br/><i>(Create default NetworkPolicies, Quotas)</i>"]
        VALIDATE["3. Validate Phase<br/><i>(Enforce readOnlyRootFilesystem, nonRoot)</i>"]
        VERIFY["4. Verify Images<br/><i>(Cosign Sigstore crypto verification)</i>"]

        APISERVER -->|AdmissionReview Webhook| MUTATE
        MUTATE --> GENERATE
        GENERATE --> VALIDATE
        VALIDATE --> VERIFY
    end

    subgraph DecisionOutcome["Admission Verdict"]
        ALLOW["✅ 200 OK: Object Persisted to etcd"]
        DENY["❌ 403 Forbidden: Policy Violation Message Returned"]

        VERIFY -->|Passes All Checks| ALLOW
        VALIDATE -->|Rule Violation (Enforce Mode)| DENY
    end
```

### 1.1 Architectural Flow & Lifecycle Walkthrough

1. **API Admission Interception**: A user submits a workload creation request (`kubectl create -f pod.yaml`). `kube-apiserver` authenticates and authorizes the request, then directs the JSON representation of the resource to the Admission Control pipeline.
2. **Phase 1: Mutate Phase (Kyverno / OPA Gatekeeper)**:
   - The API server sends an `AdmissionReview` POST request over HTTPS to the policy engine webhook service.
   - The policy engine evaluates mutation rules (e.g., automatically injecting `securityContext.runAsNonRoot = true` or adding cost-center labels).
   - The engine returns a `JSONPatch` (RFC 6902) array back to the API server, which applies the mutations to the in-memory object.
3. **Phase 2: Generate Phase**: The policy engine generates dependent resources (e.g., creating default `NetworkPolicy` and `ResourceQuota` objects whenever a new `Namespace` is created).
4. **Phase 3: Validate Phase**:
   - The API server submits the mutated object to the Validating Admission Webhook.
   - The policy engine evaluates declarative validation rules (written in Kyverno YAML, OPA Rego, or Kubernetes CEL).
   - If the object violates a policy set to `validationFailureAction: Enforce` (e.g., requesting `privileged: true`), the policy engine returns `allowed: false` with a descriptive error message. The API server terminates the request with `403 Forbidden`.
5. **Phase 4: Cryptographic Image Verification**: Kyverno/Gatekeeper verifies that container image digests are cryptographically signed using Sigstore Cosign keys or keyless Rekor transparency logs before permitting execution.

### 1.2 Serialization, Protocols & Communication Pathways

- **AdmissionReview JSON Wire Protocol (v1)**: `kube-apiserver` exchanges structured JSON payloads containing `request` metadata (UserInfo, Kind, Operation, Object, OldObject) and evaluates returned `response` objects (`allowed`, `status`, `patch`).
- **JSONPatch RFC 6902 Serialization**: Mutation patches are serialized as base64-encoded JSON arrays containing discrete patch operations (`{"op": "add", "path": "/spec/securityContext/runAsNonRoot", "value": true}`).
- **Common Expression Language (CEL)**: High-speed, non-Turing complete expression evaluation executed in-process inside `kube-apiserver` with sub-millisecond evaluation latency.

### 1.3 Deep-Dive Component Breakdown

- **ValidatingAdmissionPolicy**: Built-in Kubernetes native CEL-based admission engine executing in-process inside `kube-apiserver` without external webhook network hops.
- **Kyverno / OPA Gatekeeper Webhook Servers**: High-availability pods running mTLS webhook servers that evaluate complex cluster-wide policies.
- **Sigstore Cosign & Rekor**: Cryptographic signing framework and public transparency log verifying software supply chain provenance for container artifacts.
- **Policy Mutation Engine**: JSON transformation pipeline applying sequential RFC 6902 patch sets to object representations before persistence.

### 1.4 Under-The-Hood Mechanics & Failure Modes

- **Webhook Deadlock on API Server Startup**: If policy engine webhook pods are down and `failurePolicy: Fail` is configured on a webhook targeting core resources, `kube-apiserver` rejects all Pod creations—including the policy engine's own pods—causing a fatal cluster deadlock. Webhooks must use `namespaceSelector` to exempt `kube-system` and the policy engine's namespace.
- **CEL Evaluation Resource Exhaustion**: Highly recursive or deeply nested CEL expressions evaluated across high-frequency API calls can exceed the API server's per-request CEL budget (100,000 cost units), causing admission to fail with `CostLimitExceeded`.
- **Drift between Audit and Enforce Modes**: Running policies in `Audit` mode flags violations in logs but allows non-compliant resources to be deployed. Transitioning directly to `Enforce` mode without remediation will block operational updates to existing non-compliant workloads.

---

## 2. Annotated Production YAML Anatomy & Field Reference

Below is a production-grade declarative manifest demonstrating field definitions and operational patterns:

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: disallow-privileged-and-root
spec:
  validationFailureAction: Enforce
  background: true
  rules:
  - name: require-run-as-non-root
    match:
      any:
      - resources:
          kinds:
          - Pod
    validate:
      message: "Running as root is forbidden. Set securityContext.runAsNonRoot: true."
      pattern:
        spec:
          securityContext:
            runAsNonRoot: true
          containers:
          - securityContext:
              allowPrivilegeEscalation: false
```

### Key Field Schema Reference

| Field | Type | Description |
| :--- | :--- | :--- |
| `validationFailureAction` | `Enum` | `Audit` (logs violations without blocking) or `Enforce` (rejects non-compliant API requests). |
| `background` | `Boolean` | Scans existing cluster resources periodically to report non-compliant workloads. |
| `rules[*].mutate` / `rules[*].generate` | `Object` | Automates manifest transformation and default resource creation. |

---

## 3. Real-World Architectural Patterns

### Auto-Inject Default NetworkPolicy on Namespace Creation

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: default-network-policy
spec:
  rules:
  - name: generate-default-deny
    match:
      any:
      - resources:
          kinds:
          - Namespace
    generate:
      apiVersion: networking.k8s.io/v1
      kind: NetworkPolicy
      name: default-deny-all
      namespace: "{{request.object.metadata.name}}"
      synchronize: true
      data:
        spec:
          podSelector: {}
          policyTypes:
          - Ingress
          - Egress
```

### Gatekeeper ConstraintTemplate (Rego)

```yaml
apiVersion: templates.gatekeeper.sh/v1
kind: ConstraintTemplate
metadata:
  name: k8srequiredlabels
spec:
  crd:
    spec:
      names:
        kind: K8sRequiredLabels
      validation:
        openAPIV3Schema:
          type: object
          properties:
            labels:
              type: array
              items: {type: string}
  targets:
  - target: admission.k8s.gatekeeper.sh
    rego: |
      package k8srequiredlabels
      violation[{"msg": msg}] {
        provided := {label | input.review.object.metadata.labels[label]}
        required := {label | label := input.parameters.labels[_]}
        missing := required - provided
        count(missing) > 0
        msg := sprintf("Missing required labels: %v", [missing])
      }
```


---

## 4. Production Hardening & Operational Governance

- Start policies in `validationFailureAction: Audit` for 2 weeks to assess existing workloads before switching to `Enforce`.
- Exclude critical system namespaces (`kube-system`, `kyverno`, `gatekeeper-system`) from mutating policies.
- Run policy validation tests in CI (e.g. `kyverno test .` or `gator test .`) before manifests reach cluster environments.

---

## 5. Failure Modes & Diagnostic Triage Tree

??? failure "Manifest Rejected by Policy (`Error from server: admission webhook denied`)"
    **Root Cause:** Resource violated an enforced policy rule.

    **Diagnostic Triage Sequence:**
    1. Review the exact error message returned by `kubectl`.
    2. Check Kyverno PolicyReports: `kubectl get policyreports -A`
    3. Check Gatekeeper constraints: `kubectl get constraints`


---

## 6. Interactive Practice Matrix

Practice concepts from this chapter directly in the interactive WebAssembly sandbox:

| Exercise ID | Challenge Description | Direct Link | Action |
| :--- | :--- | :--- | :--- |
| **`policy01`** | Kyverno ClusterPolicy for Required Labels | [`../playground/index.html?exercise=policy01`](../playground/index.html?exercise=policy01) | [**⚡ Solve `policy01` in Playground →**](../playground/index.html?exercise=policy01){ .md-button .md-button--primary } |
| **`policy02`** | Kyverno Mutating Policy for Security Defaults | [`../playground/index.html?exercise=policy02`](../playground/index.html?exercise=policy02) | [**⚡ Solve `policy02` in Playground →**](../playground/index.html?exercise=policy02){ .md-button .md-button--primary } |
| **`policy03`** | Kyverno Generate Policy for Default Deny NetworkPolicy | [`../playground/index.html?exercise=policy03`](../playground/index.html?exercise=policy03) | [**⚡ Solve `policy03` in Playground →**](../playground/index.html?exercise=policy03){ .md-button .md-button--primary } |
| **`policy04`** | OPA Gatekeeper ConstraintTemplate & Constraint | [`../playground/index.html?exercise=policy04`](../playground/index.html?exercise=policy04) | [**⚡ Solve `policy04` in Playground →**](../playground/index.html?exercise=policy04){ .md-button .md-button--primary } |

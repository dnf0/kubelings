# Chapter 16: Policy as Code (Kyverno & Gatekeeper)

<div class="grid cards" markdown>

-   :material-school: **Topic Focus** &bull; Kyverno ClusterPolicies, Mutating & Generate rules, and OPA Gatekeeper Constraints
-   :material-api: **Primary APIs** &bull; `kyverno.io/v1`, `templates.gatekeeper.sh/v1` &bull; `ClusterPolicy`, `ConstraintTemplate`
-   :material-rocket-launch: [**Launch Playground in Wasm →**](../playground/index.html?chapter=16){ .md-button .md-button--primary }

</div>

---

## 1. Architectural Overview & Control Plane Mechanics

In Kubernetes, **Policy as Code (Kyverno & Gatekeeper)** is reconciled through declarative state loops managed by the control plane:

```text
┌───────────────────────────┐
│     User / CI Pipeline    │ ──(kubectl apply)──► kube-apiserver
└───────────────────────────┘                            │
                                                         ▼ Admission Phase
┌─────────────────────────────────────────────────────────────┐
│            Policy Engine (Kyverno / Gatekeeper)             │
│  • Validate: Block privileged containers, enforce non-root  │
│  • Mutate: Auto-inject default securityContext & labels     │
│  • Generate: Auto-create NetworkPolicies on new Namespaces  │
└─────────────────────────────────────────────────────────────┘
```

When resources in this chapter are submitted, the `kube-apiserver` validates the OpenAPI v3 schema, stores state in `etcd`, and triggers the responsible controllers or node daemons to reconcile actual cluster state.

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
| **`policy01`** | Kyverno ClusterPolicy for Required Labels | [`../playground/index.html?exercise=policy01`](../playground/index.html?exercise=policy01) | [**⚡ Solve in Playground →**](../playground/index.html?exercise=policy01){ .md-button .md-button--primary } |
| **`policy02`** | Kyverno Mutating Policy for Security Defaults | [`../playground/index.html?exercise=policy02`](../playground/index.html?exercise=policy02) | [**⚡ Solve in Playground →**](../playground/index.html?exercise=policy02){ .md-button .md-button--primary } |
| **`policy03`** | Kyverno Generate Policy for Default Deny NetworkPolicy | [`../playground/index.html?exercise=policy03`](../playground/index.html?exercise=policy03) | [**⚡ Solve in Playground →**](../playground/index.html?exercise=policy03){ .md-button .md-button--primary } |
| **`policy04`** | OPA Gatekeeper ConstraintTemplate & Constraint | [`../playground/index.html?exercise=policy04`](../playground/index.html?exercise=policy04) | [**⚡ Solve in Playground →**](../playground/index.html?exercise=policy04){ .md-button .md-button--primary } |

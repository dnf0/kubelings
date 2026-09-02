# Design Specification: Bidirectional 26-Chapter Kubernetes Reference Manual & Playground Integration

## 1. Executive Overview

This specification defines the complete rewrite and bidirectional integration of the 26-chapter Kubernetes Reference Manual for Kubelings. 

Kubelings will deliver:
1. **26 In-Depth Architectural Reference Manual Guides** located in `docs/guides/01-pods.md` through `docs/guides/26-hardware-acceleration-dra.md`. Each guide contains deep architectural control plane diagrams, annotated production-ready YAML manifests, field-level schema definitions, production hardening checklists, and real-world failure mode troubleshooting trees.
2. **Bidirectional Linking Architecture**:
   - **From Guides &rarr; Exercises**: Every exercise in the reference guide provides an interactive button that launches the exact exercise in the WebAssembly Monaco playground (`../playground/index.html?exercise=<id>`).
   - **From Exercises &rarr; Guides**: The WebAssembly playground features a dynamic `📖 Open Reference Guide` header button, contextual links in the progressive hint drawer, and terminal failure tips directing learners to the relevant guide.

---

## 2. Guide Schema & Structural Standard

Every reference guide in `docs/guides/` MUST implement the following 7 standard sections without placeholders or generic stubs:

```markdown
# Chapter XX: <Chapter Title>

<!-- Section 1: Hero & Metadata Banner -->
<div class="grid cards" markdown>
- :material-school: **Topic Focus** &bull; <Detailed Topic Summary>
- :material-cube-outline: **Key APIs** &bull; `<apiVersion>` &bull; `<kind>`
- :material-rocket-launch: [**Launch Chapter in Web IDE →**](../playground/index.html?chapter=<num>){ .md-button .md-button--primary }
</div>

## 1. Architectural Overview & Control Plane Mechanics
- Domain-specific ASCII architecture / data-flow diagram illustrating Kubernetes API Server, etcd, controller reconciliation loops, kubelet runtime, kernel eBPF hooks, or custom CRD controllers.
- Core invariants, state transition lifecycles, and controller mechanics.

## 2. Annotated Production YAML Anatomy & Field Reference
- Complete, validated, realistic production-grade YAML manifest.
- Comprehensive field reference table detailing `spec` parameters, data types, defaults, and operational semantics.

## 3. Real-World Architectural Patterns
- 2–3 fully articulated YAML patterns (e.g. Sidecar logging pattern, initContainer database migration, Downward API metadata injection, blue-green traffic splits, or distributed RayCluster worker topologies).

## 4. Production Hardening & Operational Governance
- Pod Security Standards (PSS/PSA), seccomp profiles, capability dropping, read-only root filesystems.
- Resource constraints (QoS Guaranteed/Burstable), Pod Disruption Budgets (PDB), Topology Spread Constraints, and anti-affinity.

## 5. Failure Modes & Diagnostic Triage Tree
- Common error conditions (e.g. `CrashLoopBackOff`, `OOMKilled`, `FailedScheduling`, `Pending`, `CreateContainerConfigError`, `ErrImagePull`, `EndpointNotReady`).
- Exact `kubectl` triage command sequences (`kubectl get -o wide`, `kubectl describe`, `kubectl logs`, `kubectl debug`).

## 6. Interactive Practice Matrix (Bidirectional Guide-to-Exercise Links)
- Interactive table mapping each chapter exercise with direct deep links:
  - Exercise ID & Title
  - Target Competency
  - [**⚡ Solve Exercise in Playground →**](../playground/index.html?exercise=<id>)
```

---

## 3. Playground UI Bidirectional Integration (Exercise-to-Guide Links)

### A. Dynamic Reference Guide Header Button
In `docs/assets/playground/playground.js`:
- Map each of the 26 chapter numbers / names to its corresponding MkDocs reference guide URL:
  ```javascript
  const CHAPTER_GUIDES = {
    1: "../guides/01-pods/",
    2: "../guides/02-controllers/",
    3: "../guides/03-config-secrets/",
    4: "../guides/04-storage/",
    5: "../guides/05-services-networking/",
    6: "../guides/06-ingress-gateway/",
    7: "../guides/07-scheduling/",
    8: "../guides/08-security-rbac/",
    9: "../guides/09-network-policies/",
    10: "../guides/10-lifecycle-probes/",
    11: "../guides/11-autoscaling/",
    12: "../guides/12-crds-and-operators/",
    13: "../guides/13-troubleshooting/",
    14: "../guides/14-gitops-argocd/",
    15: "../guides/15-service-mesh-cilium/",
    16: "../guides/16-policy-as-code/",
    17: "../guides/17-multitenancy-vcluster/",
    18: "../guides/18-admission-webhooks/",
    19: "../guides/19-helm-packaging/",
    20: "../guides/20-kustomize-overlays/",
    21: "../guides/21-gateway-api/",
    22: "../guides/22-crossplane-iac/",
    23: "../guides/23-ebpf-tetragon/",
    24: "../guides/24-kuberay-ml/",
    25: "../guides/25-batch-kueue-volcano/",
    26: "../guides/26-hardware-acceleration-dra/",
  };
  ```
- When `selectExercise(exerciseId)` runs, update a dedicated `📖 Reference Guide` link button in the playground header pointing to `CHAPTER_GUIDES[ex.chapter_number]`.

### B. Hint Drawer Contextual Reference Links
- In the Hint Drawer (`renderHints()`), append a footer:
  `📖 Stuck? Check the Chapter Reference Guide for architectural diagrams and schema references.`

### C. Terminal Failure Action Tip
- When validation fails in the Pyodide WebAssembly runner, output a contextual suggestion link in the interactive terminal:
  `💡 Architectural Reference: Review Chapter XX Guide at <guide_url>`

---

## 4. Chapter Coverage Map (26 Guides & 114 Exercises)

| # | Guide File | Target Domain & Topics | Exercise IDs |
|---|------------|------------------------|--------------|
| 01 | `01-pods.md` | Pod specs, multi-container sidecars, initContainers, QoS, Downward API, PDB | `pods01`–`pods06` |
| 02 | `02-controllers.md` | ReplicaSets, Deployments, StatefulSets, DaemonSets, Jobs, CronJobs | `ctrl01`–`ctrl06` |
| 03 | `03-config-secrets.md` | ConfigMaps, Secrets, projected volumes, envFrom, immutable configs | `config01`–`config05` |
| 04 | `04-storage.md` | PVs, PVCs, StorageClasses, dynamic provisioning, access modes | `storage01`–`storage05` |
| 05 | `05-services-networking.md` | ClusterIP, NodePort, LoadBalancer, Headless, EndpointSlices | `net01`–`net05` |
| 06 | `06-ingress-gateway.md` | Ingress controllers, path/host routing, TLS certificates | `ingress01`–`ingress04` |
| 07 | `07-scheduling.md` | nodeSelector, node/pod affinity, taints/tolerations, topology spread | `sched01`–`sched05` |
| 08 | `08-security-rbac.md` | ServiceAccounts, Roles, ClusterRoles, RoleBindings, SecurityContext, PSS | `rbac01`–`rbac05` |
| 09 | `09-network-policies.md` | Default deny, pod/namespace selectors, ingress/egress CIDR blocks | `netpol01`–`netpol04` |
| 10 | `10-lifecycle-probes.md` | Liveness, readiness, startup probes, grace periods, preStop hooks | `health01`–`health04` |
| 11 | `11-autoscaling.md` | HPA v2 metrics, VPA recommendation modes, KEDA event scalers | `autoscale01`–`autoscale04` |
| 12 | `12-crds-and-operators.md` | OpenAPI v3 schemas, CRD subresources, reconciliation loops | `crd01`–`crd04` |
| 13 | `13-troubleshooting.md` | CrashLoopBackOff, OOMKilled, Pending, ImagePullBackOff, kubectl debug | `troubleshoot01`–`troubleshoot05` |
| 14 | `14-gitops-argocd.md` | ArgoCD Application, ApplicationSet, automated sync, Argo Rollouts | `gitops01`–`gitops04` |
| 15 | `15-service-mesh-cilium.md` | eBPF CNI, CiliumNetworkPolicy L7 rules, mTLS, Hubble | `mesh01`–`mesh04` |
| 16 | `16-policy-as-code.md` | Kyverno ClusterPolicies, mutating/generating rules, Gatekeeper Rego | `policy01`–`policy04` |
| 17 | `17-multitenancy-vcluster.md` | Hierarchical Namespaces (HNC), ResourceQuotas, vcluster control planes | `tenant01`–`tenant04` |
| 18 | `18-admission-webhooks.md` | Mutating/validating webhooks, admission phases, TLS certificates | `webhook01`–`webhook04` |
| 19 | `19-helm-packaging.md` | Chart.yaml, Go templates, _helpers.tpl, values schemas, subcharts | `helm01`–`helm04` |
| 20 | `20-kustomize-overlays.md` | Bases, overlays, generators, strategic merge & JSON 6902 patches | `kustomize01`–`kustomize04` |
| 21 | `21-gateway-api.md` | GatewayClass, Gateway, HTTPRoute, traffic splits, ReferenceGrant | `gateway01`–`gateway04` |
| 22 | `22-crossplane-iac.md` | XRDs, Compositions, Managed Resources, Composite Resource Claims | `crossplane01`–`crossplane04` |
| 23 | `23-ebpf-tetragon.md` | Tetragon TracingPolicy, sys_execve tracing, namespace escape security | `tetragon01`–`tetragon04` |
| 24 | `24-kuberay-ml.md` | RayCluster (head/worker specs), RayJob batch tuning, RayService serving | `ray01`–`ray04` |
| 25 | `25-batch-kueue-volcano.md` | Kueue ClusterQueue/LocalQueue cohorts, Volcano gang scheduling | `kueue01`–`volcano02` |
| 26 | `26-hardware-acceleration-dra.md` | NVIDIA MIG, Apple Silicon GPU, Dynamic Resource Allocation (DRA) | `accel01`–`accel04` |

---

## 5. Verification & Acceptance Criteria

1. **Guide Content Quality**: All 26 guides contain zero empty YAML blocks or generic stubs; all manifests are valid Kubernetes schemas.
2. **Bidirectional Navigation**:
   - Clicking any exercise link in any guide opens the WebAssembly playground directly on that exercise.
   - Clicking `📖 Reference Guide` in the playground opens the matching chapter reference guide.
3. **Docs Strict Build**: `mkdocs build --strict` completes with 0 errors and 0 missing link warnings.
4. **Test Suite**: `pytest` passes all 915 tests.
5. **Lint & Formatting**: `ruff check .`, `ruff format --check .`, and `pyright` pass with 0 errors.

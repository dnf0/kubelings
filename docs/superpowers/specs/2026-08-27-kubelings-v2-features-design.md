# Kubelings v2 Advanced Features & Curriculum Expansion Design

## 1. Overview & Objectives

This design outlines the architecture, data models, UI components, and curriculum expansion for **Kubelings v2**, introducing:
1. **Interactive Full-Screen TUI Dashboard (`kubelings tui` / `kubelings dashboard`)**: A visual split-pane terminal interface for navigating chapters, previewing code, running exercises, and viewing live validation diagnostics.
2. **Kubernetes Resource Topology Visualizer (`kubelings tree`)**: An architectural tree inspector that renders Kubernetes resource relationships (Workloads ➔ Pods ➔ PVCs ➔ Services ➔ Ingress ➔ Policies).
3. **Universal YAML Manifest Linter (`kubelings lint <manifest.yaml>`)**: A standalone schema and best-practices linter for arbitrary Kubernetes manifests with line-accurate diagnostics.
4. **Curriculum Expansion (Chapters 16, 17, 18 — 82 Total Exercises)**:
   - **Chapter 16: Policy as Code with Kyverno & OPA Gatekeeper** (`16_policy_as_code`)
   - **Chapter 17: Multi-Tenancy, Virtual Clusters & HNC** (`17_multitenancy_vcluster`)
   - **Chapter 18: Advanced Admission Webhooks & Dynamic Interception** (`18_admission_webhooks`)

---

## 2. Architecture & Components

### 2.1 Interactive TUI Dashboard (`src/kubelings/tui.py`)
- **Layout Structure**:
  - `Header`: Kubelings title, version, active cluster status badge, and global keyboard hints.
  - `Sidebar` (Left): Collapsible chapter and exercise tree with status badges (✅ Passed, ⏳ In Progress, ❌ Failing, ⭕ Untouched).
  - `Main Pane` (Right Top): Exercise title, objective, problem description, and syntax-highlighted exercise code viewer with line numbers.
  - `Output / Diagnostics Pane` (Right Bottom): Schema validation results, stdout/stderr, progressive hint tiers, and execution timing.
  - `Footer`: Context-sensitive hotkeys (`[Enter]` Run, `[h]` Hint, `[r]` Reset, `[t]` Tree View, `[q]` Exit).
- **Navigation Controls**:
  - `↑` / `k`: Move up exercise list
  - `↓` / `j`: Move down exercise list
  - `Enter`: Execute highlighted exercise
  - `h`: Reveal next progressive hint tier
  - `r`: Reset exercise to clean starter state
  - `t`: Switch to Topology Tree view for active exercise
  - `q` / `Esc`: Exit TUI

### 2.2 Kubernetes Resource Topology Visualizer (`src/kubelings/topology.py`)
- **Core Functionality**:
  - Parses Kubernetes manifest dictionaries (or loads from file / exercise output).
  - Identifies relationship graphs:
    - Ingress ➔ Service ➔ Endpoints ➔ Pods
    - Deployment / StatefulSet / DaemonSet / Job ➔ ReplicaSet / Pods
    - Workload Pods ➔ PVC ➔ PV ➔ StorageClass
    - NetworkPolicy / CiliumNetworkPolicy ➔ Target Workload Pods & Egress Endpoints
  - Formats relations into a Rich `Tree` object with colorized badges and resource metadata.
- **CLI Commands**:
  - `kubelings tree [EXERCISE_NAME]` (renders topology for an exercise)
  - `kubelings tree --file <manifest.yaml>` (renders topology for external file)

### 2.3 Universal Manifest Linter (`src/kubelings/linter.py`)
- **Core Functionality**:
  - Validates YAML/JSON files against:
    - Root schema integrity (`apiVersion`, `kind`, `metadata.name`)
    - Workload best practices (resource `limits`/`requests` specified, `readinessProbe`/`livenessProbe` defined)
    - Security best practices (`runAsNonRoot: true`, `readOnlyRootFilesystem: true`, `allowPrivilegeEscalation: false`)
    - Service selector matching valid pod label patterns
  - Emits colorized Rich table with file path, line number, severity (`ERROR`, `WARNING`, `INFO`), rule ID, and actionable fix suggestions.
- **CLI Command**:
  - `kubelings lint <path_or_glob>` (e.g. `kubelings lint exercises/01_pods/*.py` or `kubelings lint deploy.yaml`)

### 2.4 Curriculum Expansion (Chapters 16, 17, 18)

#### Chapter 16: Policy as Code with Kyverno & Gatekeeper (`16_policy_as_code`)
- `policy01`: Kyverno `ClusterPolicy` validating mandatory organizational labels (`app.kubernetes.io/name`, `team`).
- `policy02`: Kyverno Mutating Policy injecting container `securityContext` defaults (`runAsNonRoot: true`, `drop: ["ALL"]`).
- `policy03`: Kyverno Generate Policy creating default-deny NetworkPolicy upon Namespace provisioning.
- `policy04`: OPA Gatekeeper `ConstraintTemplate` with Rego specification and `K8sRequiredLabels` constraint.

#### Chapter 17: Multi-Tenancy, Virtual Clusters & HNC (`17_multitenancy_vcluster`)
- `tenant01`: Hierarchical Namespace Controller (`HNC`) parent-child subnamespace hierarchy and role propagation.
- `tenant02`: Namespace ResourceQuotas, LimitRanges, and tenant isolation policies.
- `tenant03`: Virtual Cluster (`vcluster`) CustomResource spec with isolated control plane.
- `tenant04`: Multi-tenant NetworkPolicy isolation & egress gateway routing.

#### Chapter 18: Advanced Admission Webhooks & Dynamic Interception (`18_admission_webhooks`)
- `webhook01`: MutatingAdmissionWebhook configuration with CABundle, rules, and failurePolicy.
- `webhook02`: ValidatingAdmissionWebhook intercepting privileged pod creation and hostPath mounts.
- `webhook03`: Sidecar container injection via mutating admission webhook review response.
- `webhook04`: CRD conversion webhooks for multi-version CustomResourceDefinitions.

---

## 3. Data Flow & Interfaces

```
+-------------------------------------------------------------+
|                      Kubelings CLI                          |
|  +--------------+  +--------------+  +-------------------+  |
|  |  watch / run |  |  tui / dash  |  |  tree / lint      |  |
|  +-------+------+  +-------+------+  +---------+---------+  |
+----------|-----------------|-------------------|------------+
           |                 |                   |
           v                 v                   v
+--------------------+ +---------------+ +--------------------+
|  Curriculum Engine | |  TUI Renderer | | Topology & Linter  |
|  (18 Chapters /    | |  (Split Pane  | | (Resource Graph &  |
|   82 Exercises)    | |   Dashboard)  | |  Rule Evaluator)   |
+----------+---------+ +-------+-------+ +---------+----------+
           |                   |                   |
           +-------------------+-------------------+
                               |
                               v
                     +-------------------+
                     | Schema Validator  |
                     | & Cluster Adapter |
                     +-------------------+
```

---

## 4. Verification & Testing Strategy

1. **Unit Tests**:
   - `tests/test_tui.py`: Verify TUI state machine, keypress routing, and screen layout rendering.
   - `tests/test_topology.py`: Verify topology graph construction for Pods, Services, Storage, Ingress, and Policies.
   - `tests/test_linter.py`: Verify linter rule detection for security, resources, and probes.
   - `tests/test_chapters_16_18.py`: Verify all starter templates fail with NOT_DONE and all reference solutions pass.
2. **Integration Tests**:
   - `kubelings test`: Verify 82/82 reference solutions pass.
   - Full test suite: `pytest` across Python 3.10, 3.11, and 3.12.
   - Quality checks: `ruff check .`, `ruff format --check .`, `pyright`.
   - MkDocs build & validation: `mkdocs build --strict`.

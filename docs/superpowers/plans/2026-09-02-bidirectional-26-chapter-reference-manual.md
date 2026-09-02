# Bidirectional 26-Chapter Kubernetes Reference Manual & Playground Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Choose an execution mode:
> 1. `superpowers:subagent-driven-development` (recommended for multi-agent reviews, backed by `SKILL.state` / `.agent-state/state.json`)
> 2. `agent-rules:stateful-execution` (SKILL.state) (recommended for deterministic single-agent linear execution)
> 3. `superpowers:executing-plans` (batch execution with manual checkpoints)
> Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild the complete 26-chapter Kubernetes reference manual with deep architectural diagrams, validated production YAML manifests, field references, and troubleshooting triage trees, bidirectionally linked with the 114-exercise WebAssembly Monaco playground.

**Architecture:** 
1. The WebAssembly playground (`playground.js` & `index.html`) dynamically links every exercise to its chapter's reference guide via a dedicated header button, hint drawer link, and terminal error tip.
2. An automated reference guide generator (`generate_reference_guides.py`) builds 26 production-grade reference guides (`docs/guides/01-pods.md` to `26-hardware-acceleration-dra.md`) with valid YAML manifests, ASCII control plane diagrams, schema tables, hardening checklists, and deep-linked exercise matrices.
3. Automated test suite (`test_reference_guides.py`) validates that all 26 guides exist, contain valid YAML, have all required sections, and properly link all 114 exercises.

**Tech Stack:** Python 3.12, PyYAML, MkDocs Material, Vanilla JS (Playground Controller), Monaco Editor, Pyodide Wasm, pytest, Ruff, Pyright.

## Global Constraints

- Python 3.12 syntax with strict typing.
- All YAML manifests in guides must be valid and parseable with `yaml.safe_load`.
- Every exercise link must point to `../playground/index.html?exercise=<id>`.
- Every playground exercise must resolve to its corresponding `../guides/<slug>/` guide.
- `mkdocs build --strict` must pass with 0 errors and 0 missing link warnings.
- All 915+ pytest tests, `ruff check .`, `ruff format --check .`, and `pyright` must pass.

---

### Task 1: WebAssembly Playground Bidirectional Navigation & Header UI

**Files:**
- Modify: `docs/assets/playground/playground.js:614-680,1050-1120`
- Modify: `docs/assets/playground/playground.css:20-60`
- Modify: `docs/playground/index.html:25-85`

**Interfaces:**
- Produces: `CHAPTER_GUIDES` map in `playground.js`, `#btn-open-guide` in `standalone-header`, dynamic URL update on `selectExercise(exerciseId)`.

- [ ] **Step 1: Add `#btn-open-guide` element to `docs/playground/index.html`**
  Add a `📖 Reference Guide` link button in the standalone header navigation actions:
  ```html
  <a id="btn-open-guide" href="../guides/01-pods/" target="_blank" rel="noopener noreferrer" class="nav-btn" title="Open Chapter Reference Guide">
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path></svg>
    <span>Reference Guide</span>
  </a>
  ```

- [ ] **Step 2: Update `docs/assets/playground/playground.js` with `CHAPTER_GUIDES` and dynamic guide link handler**
  Define the 26-chapter slug mapping table and wire `selectExercise()` to update the `#btn-open-guide` link to the active exercise's chapter guide.

- [ ] **Step 3: Update Hint Drawer and Terminal failure tips to suggest the chapter guide**
  In `renderHints()` and test evaluation failure handlers, include the dynamic reference guide link.

- [ ] **Step 4: Verify playground bidirectional UI links**
  Verify DOM elements and URL generation for chapters 1 through 26.

- [ ] **Step 5: Commit changes**
  `git commit -m "feat(playground): add bidirectional reference guide header navigation and contextual links"`

---

### Task 2: Comprehensive 26-Chapter Reference Guide Authoring Engine & Verification Suite

**Files:**
- Create: `tests/test_reference_guides.py`
- Modify: `scripts/generate_reference_guides.py`
- Modify: `docs/guides/01-pods.md` through `docs/guides/26-hardware-acceleration-dra.md`

**Interfaces:**
- Consumes: `src/kubelings/manifest.py:build_manifest()`
- Produces: 26 fully formed Markdown reference guides in `docs/guides/*.md`

- [ ] **Step 1: Write the automated test suite `tests/test_reference_guides.py`**
  Write tests that verify:
  1. All 26 guide files exist in `docs/guides/`.
  2. Each file contains all 7 standard sections (Hero, Architecture Diagram, Annotated YAML, Patterns, Hardening, Troubleshooting, Exercise Matrix).
  3. Every YAML code block in the guide is valid YAML (`yaml.safe_load`).
  4. Every exercise registered in `src/kubelings/manifest.py` is present with a valid playground link.

- [ ] **Step 2: Run `pytest tests/test_reference_guides.py` to confirm failure on existing stubs**
  Verify that the tests catch empty YAML blocks in existing guides.

- [ ] **Step 3: Implement comprehensive chapter data dictionary in `scripts/generate_reference_guides.py`**
  Define rich, production-grade manifest content, domain-specific ASCII diagrams, field annotations, real-world patterns, hardening checklists, and troubleshooting commands for all 26 chapters:
  - `01-pods`: Multi-container sidecars, initContainers, QoS Guaranteed/Burstable, Downward API, PDBs.
  - `02-controllers`: RollingUpdate vs Recreate, StatefulSet ordinals, DaemonSet tolerations, Jobs/CronJobs.
  - `03-config-secrets`: ConfigMaps, Secret types, projected volumes, envFrom, immutable configs.
  - `04-storage`: StorageClasses, PVC binding modes, access modes, CSI attributes.
  - `05-services-networking`: ClusterIP, NodePort, LoadBalancer, Headless, EndpointSlices.
  - `06-ingress-gateway`: Ingress annotations, path/host routing, TLS secrets.
  - `07-scheduling`: nodeSelector, node/pod affinity, taints/tolerations, topology spread.
  - `08-security-rbac`: ServiceAccounts, Roles, ClusterRoles, RoleBindings, SecurityContext, PSS.
  - `09-network-policies`: Default deny ingress/egress, CIDR blocks, pod/namespace selectors.
  - `10-lifecycle-probes`: Liveness/Readiness/Startup probes, grace periods, preStop hooks.
  - `11-autoscaling`: HPA v2 metrics, VPA recommendation modes, KEDA triggers.
  - `12-crds-and-operators`: OpenAPI v3 schemas, CRD subresources, reconciliation loops.
  - `13-troubleshooting`: CrashLoopBackOff, OOMKilled, Pending, kubectl debug.
  - `14-gitops-argocd`: ArgoCD Applications, sync policies, Argo Rollouts canaries.
  - `15-service-mesh-cilium`: Cilium eBPF CNI, L7 policies, mTLS, Hubble.
  - `16-policy-as-code`: Kyverno ClusterPolicy validate/mutate/generate, Gatekeeper Rego.
  - `17-multitenancy-vcluster`: HNC, ResourceQuotas, vcluster control planes.
  - `18-admission-webhooks`: Mutating/validating webhooks, admission phases, TLS certs.
  - `19-helm-packaging`: Chart.yaml, Go templates, _helpers.tpl, values schemas.
  - `20-kustomize-overlays`: Bases, overlays, generators, strategic merge & JSON 6902 patches.
  - `21-gateway-api`: GatewayClass, Gateway, HTTPRoute, weighted traffic splits, ReferenceGrant.
  - `22-crossplane-iac`: XRDs, Compositions, Managed Resources, Claims.
  - `23-ebpf-tetragon`: Tetragon TracingPolicy, sys_execve tracing, namespace escape security.
  - `24-kuberay-ml`: RayCluster head/worker specs, RayJob batch tuning, RayService serving.
  - `25-batch-kueue-volcano`: Kueue ClusterQueue cohorts, Volcano gang scheduling.
  - `26-hardware-acceleration-dra`: NVIDIA MIG, Apple Silicon GPU, Dynamic Resource Allocation.

- [ ] **Step 4: Execute generator and verify with `tests/test_reference_guides.py`**
  Run `python scripts/generate_reference_guides.py` and run `pytest tests/test_reference_guides.py` to confirm all 26 guides pass validation.

- [ ] **Step 5: Commit changes**
  `git commit -m "docs: generate comprehensive 26-chapter reference guides with full YAML manifests and diagrams"`

---

### Task 3: Full Documentation Site Verification, Syllabus, and Index Refresh

**Files:**
- Modify: `docs/index.md`
- Modify: `docs/syllabus.md`
- Modify: `mkdocs.yml`

- [ ] **Step 1: Refresh `docs/index.md` and `docs/syllabus.md` with complete 26-chapter roadmap**
  Ensure all guides, chapters, and exercises are indexed with clean badges and bidirectional links.

- [ ] **Step 2: Run `mkdocs build --strict`**
  Verify clean documentation compilation with 0 warnings/errors.

- [ ] **Step 3: Run complete verification suite**
  - `pytest` (all tests passing)
  - `ruff check .` and `ruff format --check .`
  - `pyright`

- [ ] **Step 4: Commit changes**
  `git commit -m "docs: refresh landing page, syllabus, and finalize bidirectional documentation suite"`

# AWS EKS, GCP GKE & Enterprise Governance Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Choose an execution mode:
> 1. `superpowers:subagent-driven-development` (recommended for multi-agent reviews, backed by `SKILL.state` / `.agent-state/state.json`)
> 2. `agent-rules:stateful-execution` (SKILL.state) (recommended for deterministic single-agent linear execution)
> 3. `superpowers:executing-plans` (batch execution with manual checkpoints)
> Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expand the Kubelings learning curriculum to 29 chapters and 126 exercises by adding dedicated chapters for AWS EKS, GCP GKE, and Enterprise Multi-Account Governance (Control Tower, ESO, Vault, ArgoCD).

**Architecture:** Extend `kubelings/manifest.py` with 12 new exercise declarations across chapters 27-29. Scaffold all 12 exercise directories in `exercises/` with problem manifests, solutions, and hints. Author production-grade Mermaid.js architectural diagrams, YAML manifests, field tables, and troubleshooting trees in `scripts/generate_reference_guides.py`. Verify with pytest and deploy to GitHub Pages.

**Tech Stack:** Python 3.12, Pytest, Material for MkDocs, Mermaid.js, PyYAML, WebAssembly/Pyodide.

## Global Constraints

- Total chapter count expands from 26 to 29.
- Total exercise count expands from 114 to 126.
- All 12 new exercises must have valid, complete `README.md`, `problem.yaml`, and `solution.yaml` files.
- All new reference guides must contain rich Mermaid.js diagrams in Section 1 and zero raw text boxes.
- Full pytest suite and strict MkDocs build must pass with 0 errors.

---

### Task 1: Update Curriculum Manifest for Chapters 27, 28, and 29

**Files:**
- Modify: `kubelings/manifest.py`
- Test: `tests/test_manifest.py`

**Interfaces:**
- Consumes: Chapter and Exercise dataclasses from `kubelings.models`
- Produces: `build_manifest()` returning 29 chapters and 126 exercises.

- [ ] **Step 1: Add Chapter 27, 28, and 29 definitions to `manifest.py`**
Define Chapter 27 (AWS EKS: `eks01`, `eks02`, `eks03`, `eks04`), Chapter 28 (GCP GKE: `gke01`, `gke02`, `gke03`, `gke04`), Chapter 29 (Enterprise Governance: `eso01`, `vault01`, `gov01`, `gov02`).

- [ ] **Step 2: Run manifest tests to verify definitions**
Run `uv run pytest tests/test_manifest.py -v`.

- [ ] **Step 3: Commit**
```bash
git add kubelings/manifest.py
git commit -m "feat(manifest): register chapters 27, 28, and 29 with 12 new exercises"
```

---

### Task 2: Scaffold Chapter 27 Exercises (AWS EKS)

**Files:**
- Create: `exercises/27-aws-eks/eks01/{README.md, problem.yaml, solution.yaml}`
- Create: `exercises/27-aws-eks/eks02/{README.md, problem.yaml, solution.yaml}`
- Create: `exercises/27-aws-eks/eks03/{README.md, problem.yaml, solution.yaml}`
- Create: `exercises/27-aws-eks/eks04/{README.md, problem.yaml, solution.yaml}`
- Test: `tests/test_exercises.py`

- [ ] **Step 1: Create `eks01` (EKS Pod Identity & IRSA)**
Author ServiceAccount with AWS IAM role annotation (`eks.amazonaws.com/role-arn`) and projected token volume.

- [ ] **Step 2: Create `eks02` (AWS Load Balancer Controller Ingress)**
Author Ingress with `alb.ingress.kubernetes.io/scheme: internet-facing` and `alb.ingress.kubernetes.io/target-type: ip`.

- [ ] **Step 3: Create `eks03` (VPC CNI Security Groups for Pods)**
Author `SecurityGroupPolicy` CRD binding AWS security groups to matching pod selectors.

- [ ] **Step 4: Create `eks04` (Karpenter AWS NodePool)**
Author Karpenter `NodePool` and `EC2NodeClass` for AWS spot and on-demand EC2 capacity.

- [ ] **Step 5: Run tests and commit**
```bash
git add exercises/27-aws-eks/
git commit -m "feat(exercises): add chapter 27 AWS EKS exercises"
```

---

### Task 3: Scaffold Chapter 28 Exercises (GCP GKE)

**Files:**
- Create: `exercises/28-gcp-gke/gke01/{README.md, problem.yaml, solution.yaml}`
- Create: `exercises/28-gcp-gke/gke02/{README.md, problem.yaml, solution.yaml}`
- Create: `exercises/28-gcp-gke/gke03/{README.md, problem.yaml, solution.yaml}`
- Create: `exercises/28-gcp-gke/gke04/{README.md, problem.yaml, solution.yaml}`
- Test: `tests/test_exercises.py`

- [ ] **Step 1: Create `gke01` (GKE Workload Identity Federation)**
Author ServiceAccount with `iam.gke.io/gcp-service-account` annotation and pod identity binding.

- [ ] **Step 2: Create `gke02` (GKE Autopilot Workload Sizing)**
Author Deployment configured for Autopilot resource management with `autopilot.gke.io/compute-class: Performance`.

- [ ] **Step 3: Create `gke03` (GKE Gateway API & Cloud Armor Policy)**
Author `GCPBackendPolicy` attaching a Cloud Armor security policy to a Gateway HTTPRoute backend.

- [ ] **Step 4: Create `gke04` (Config Connector StorageBucket)**
Author Google Cloud `StorageBucket` CRD (`storage.cnrm.cloud.google.com/v1beta1`) with uniform bucket-level access.

- [ ] **Step 5: Run tests and commit**
```bash
git add exercises/28-gcp-gke/
git commit -m "feat(exercises): add chapter 28 GCP GKE exercises"
```

---

### Task 4: Scaffold Chapter 29 Exercises (Enterprise Governance & Secrets)

**Files:**
- Create: `exercises/29-enterprise-governance/eso01/{README.md, problem.yaml, solution.yaml}`
- Create: `exercises/29-enterprise-governance/vault01/{README.md, problem.yaml, solution.yaml}`
- Create: `exercises/29-enterprise-governance/gov01/{README.md, problem.yaml, solution.yaml}`
- Create: `exercises/29-enterprise-governance/gov02/{README.md, problem.yaml, solution.yaml}`
- Test: `tests/test_exercises.py`

- [ ] **Step 1: Create `eso01` (External Secrets Operator `SecretStore` & `ExternalSecret`)**
Author `SecretStore` referencing AWS Secrets Manager / GCP Secret Manager and an `ExternalSecret` resource.

- [ ] **Step 2: Create `vault01` (HashiCorp Vault Agent Injector)**
Author Pod template with `vault.hashicorp.com/agent-inject: "true"` and credential templates.

- [ ] **Step 3: Create `gov01` (ArgoCD ApplicationSet Cluster Matrix)**
Author `ApplicationSet` with a `matrix` generator deploying cluster baselines across production environments.

- [ ] **Step 4: Create `gov02` (Multi-Account Security & Resource Quotas)**
Author multi-tenant `ResourceQuota` and security constraints preventing privilege escalation.

- [ ] **Step 5: Run tests and commit**
```bash
git add exercises/29-enterprise-governance/
git commit -m "feat(exercises): add chapter 29 Enterprise Governance exercises"
```

---

### Task 5: Implement Reference Manual Content & Mermaid Diagrams (Chapters 27, 28 & 29)

**Files:**
- Modify: `scripts/generate_reference_guides.py`
- Modify: `mkdocs.yml`
- Test: `uv run python scripts/generate_reference_guides.py`

- [ ] **Step 1: Add Chapters 27, 28, and 29 data in `generate_reference_guides.py`**
Include complete Mermaid diagrams, primary production YAML manifests, field schema tables, patterns, hardening checklists, and failure triage trees.

- [ ] **Step 2: Update `mkdocs.yml` navigation**
Add Chapter 27, 28, and 29 reference guides to the documentation navigation tree.

- [ ] **Step 3: Generate reference guides**
Run `uv run python scripts/generate_reference_guides.py` to generate `27-aws-eks.md`, `28-gcp-gke.md`, `29-enterprise-governance.md`, and update `syllabus.md`.

- [ ] **Step 4: Commit**
```bash
git add scripts/generate_reference_guides.py mkdocs.yml docs/guides/ docs/syllabus.md
git commit -m "feat(docs): add comprehensive reference guides for chapters 27, 28, and 29"
```

---

### Task 6: Update Automated Verification Tests

**Files:**
- Modify: `tests/test_reference_guides.py`
- Modify: `tests/test_manifest.py`
- Test: `uv run pytest -q`

- [ ] **Step 1: Update chapter slugs and exercise count assertions in test files**
Include `27-aws-eks`, `28-gcp-gke`, `29-enterprise-governance` in `CHAPTER_SLUGS` and update total exercise count to 126.

- [ ] **Step 2: Run full test suite**
Run `uv run pytest -q` and verify all tests pass.

- [ ] **Step 3: Commit**
```bash
git add tests/
git commit -m "test: update test assertions for 29 chapters and 126 exercises"
```

---

### Task 7: Build Verification, Merge, and Deployment

**Files:**
- Test: `uv run mkdocs build --strict`
- Test: `uv run ruff check .`
- Test: `uv run pyright`
- Run: `git push origin main`

- [ ] **Step 1: Run linting, typing, and strict docs build**
Ensure `uv run ruff check .`, `uv run pyright`, and `uv run mkdocs build --strict` pass with 0 errors.

- [ ] **Step 2: Push to `main`**
Push to trigger the GitHub Actions `Deploy Documentation` workflow.

- [ ] **Step 3: Verify live deployment**
Track workflow with `gh run watch` to confirm live deployment on GitHub Pages.

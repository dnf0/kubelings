# 26-Chapter Mermaid.js Architectural Diagrams Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Choose an execution mode:
> 1. `superpowers:subagent-driven-development` (recommended for multi-agent reviews, backed by `SKILL.state` / `.agent-state/state.json`)
> 2. `agent-rules:stateful-execution` (SKILL.state) (recommended for deterministic single-agent linear execution)
> 3. `superpowers:executing-plans` (batch execution with manual checkpoints)
> Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade all 26 reference guide architectural diagrams from plain ASCII text boxes to high-fidelity, responsive, theme-aware Mermaid.js flowcharts and sequence diagrams in Material for MkDocs.

**Architecture:** Configure `pymdownx.superfences` custom fences in `mkdocs.yml` to support client-side Mermaid rendering. Update `scripts/generate_reference_guides.py` with 26 detailed Mermaid definitions utilizing subgraphs, custom styling, labeled packet/control flows, and state machines. Validate via automated pytest assertions and strict MkDocs builds.

**Tech Stack:** Python 3.12, Material for MkDocs, `pymdownx.superfences`, Mermaid.js, Pytest.

## Global Constraints

- Must work flawlessly in Material for MkDocs dark (`slate`) and light (`default`) themes.
- No external unverified dependencies; uses built-in Material for MkDocs Mermaid integration.
- Strict MkDocs build (`uv run mkdocs build --strict`) must pass with 0 errors and 0 warnings.
- Full pytest suite (969+ tests) must pass.

---

### Task 1: Enable Native Mermaid Support in MkDocs Configuration

**Files:**
- Modify: `mkdocs.yml:34-48`
- Test: `uv run mkdocs build --strict`

- [ ] **Step 1: Update `mkdocs.yml` markdown extensions**
Configure `pymdownx.superfences` with `fence_code_format` for `mermaid`.

- [ ] **Step 2: Verify `mkdocs build --strict` passes**
Run `uv run mkdocs build --strict` and verify exit code 0.

- [ ] **Step 3: Commit**
```bash
git add mkdocs.yml
git commit -m "chore(docs): configure native Mermaid custom fences in mkdocs.yml"
```

---

### Task 2: Implement Mermaid Diagrams for Chapters 01 to 07 (Core Architecture)

**Files:**
- Modify: `scripts/generate_reference_guides.py` (Chapters 1 to 7)
- Test: `tests/test_reference_guides.py`

**Interfaces:**
- Consumes: Chapter metadata in `CHAPTER_GUIDE_METADATA`
- Produces: `flowchart TD` / `flowchart LR` Mermaid blocks in Section 1 of Guides 01 to 07.

- [ ] **Step 1: Define Mermaid diagrams for Chapters 01 to 07 in `generate_reference_guides.py`**
  - Ch 01: Pod Sandboxes, Kubelet Sync Loop, CRI containerd, Init Container barrier, Sidecars, Shared `emptyDir`/PVC.
  - Ch 02: `kube-controller-manager`, Deployment Controller, ReplicaSet revisions, desired replicas sync loop.
  - Ch 03: ConfigMaps & Secrets (Envelope Encryption), atomic symlink volume projection (`..data`), env var injection.
  - Ch 04: StorageClass, CSI Provisioner, CSI Attacher, Node CSI Driver mount, PV/PVC binding lifecycle.
  - Ch 05: CoreDNS lookup, Service ClusterIP/NodePort/LoadBalancer VIP, `kube-proxy` (iptables/IPVS), EndpointSlice.
  - Ch 06: Ingress Controller (Envoy/NGINX), Ingress rules (Host/Path), TLS termination, upstream Service backends.
  - Ch 07: `kube-scheduler` pipeline (Filter → Score → Reserve → Permit → PreBind → Bind), Node Affinity, Taints/Tolerations, Topology Spread.

- [ ] **Step 2: Generate guides and verify**
Run `uv run python scripts/generate_reference_guides.py` and inspect generated markdown files.

- [ ] **Step 3: Commit**
```bash
git add scripts/generate_reference_guides.py docs/guides/0[1-7]-*.md
git commit -m "feat(docs): add rich Mermaid architectural diagrams for chapters 01 to 07"
```

---

### Task 3: Implement Mermaid Diagrams for Chapters 08 to 14 (Security, Operations & GitOps)

**Files:**
- Modify: `scripts/generate_reference_guides.py` (Chapters 8 to 14)
- Test: `tests/test_reference_guides.py`

- [ ] **Step 1: Define Mermaid diagrams for Chapters 08 to 14 in `generate_reference_guides.py`**
  - Ch 08: Authentication (X.509/OIDC), RBAC evaluation (`ClusterRoleBinding` → `Role` → Rule Verbs), Pod Security Admission & SecurityContext.
  - Ch 09: CNI dataplane firewalling (eBPF / iptables), Ingress/Egress CIDR, PodSelector, Default-Deny isolation.
  - Ch 10: Kubelet probe engine (Startup → Liveness → Readiness), Pod conditions, EndpointSlice traffic gating.
  - Ch 11: Metrics Server & Prometheus, HPA PID controller loop, VPA recommendation, Karpenter/Cluster Autoscaler node provisioning.
  - Ch 12: CRD OpenAPI schema validation, Controller Informer cache, Event Queue, Reconciler loop, Status subresource update.
  - Ch 13: Systematic troubleshooting triage flowchart (Pending → CrashLoopBackOff → OOMKilled → Evicted → Service 503).
  - Ch 14: GitOps Repo Source of Truth, ArgoCD Repo Server, Application Controller reconciliation (Diff live vs desired), Self-Heal & Auto-Prune.

- [ ] **Step 2: Generate guides and verify**
Run `uv run python scripts/generate_reference_guides.py`.

- [ ] **Step 3: Commit**
```bash
git add scripts/generate_reference_guides.py docs/guides/0[8-9]-*.md docs/guides/1[0-4]-*.md
git commit -m "feat(docs): add rich Mermaid architectural diagrams for chapters 08 to 14"
```

---

### Task 4: Implement Mermaid Diagrams for Chapters 15 to 21 (eBPF, Extensions & Modern Networking)

**Files:**
- Modify: `scripts/generate_reference_guides.py` (Chapters 15 to 21)
- Test: `tests/test_reference_guides.py`

- [ ] **Step 1: Define Mermaid diagrams for Chapters 15 to 21 in `generate_reference_guides.py`**
  - Ch 15: Cilium eBPF socket layer (`sockops` / `tc-bpf`), Sidecarless Envoy proxy, SPIFFE mTLS, Hubble L7 observability.
  - Ch 16: Policy-as-Code admission review (Kyverno / OPA Gatekeeper), Mutate/Validate/Generate rules, ConstraintTemplates.
  - Ch 17: vcluster Virtual Control Plane, syncer daemon, super-cluster physical worker nodes, resource quota isolation.
  - Ch 18: Admission Webhook pipeline (Mutating Webhook → Schema Validation → Validating Webhook → etcd persistence).
  - Ch 19: Helm packaging & templating engine (`values.yaml` + `Chart.yaml`), release Secret versioning (`sh.helm.release.v1`).
  - Ch 20: Kustomize overlay pipeline (Base manifests + patchesStrategicMerge, json6902, namePrefix, configMapGenerator).
  - Ch 21: Gateway API hierarchy (`GatewayClass` → `Gateway` → `HTTPRoute`/`GRPCRoute` → backend Service Endpoints).

- [ ] **Step 2: Generate guides and verify**
Run `uv run python scripts/generate_reference_guides.py`.

- [ ] **Step 3: Commit**
```bash
git add scripts/generate_reference_guides.py docs/guides/1[5-9]-*.md docs/guides/2[0-1]-*.md
git commit -m "feat(docs): add rich Mermaid architectural diagrams for chapters 15 to 21"
```

---

### Task 5: Implement Mermaid Diagrams for Chapters 22 to 26 (Cloud-Native Ecosystem & AI/ML)

**Files:**
- Modify: `scripts/generate_reference_guides.py` (Chapters 22 to 26)
- Test: `tests/test_reference_guides.py`

- [ ] **Step 1: Define Mermaid diagrams for Chapters 22 to 26 in `generate_reference_guides.py`**
  - Ch 22: Crossplane XRD Composite Resource Definitions, `Composition` pipeline, Managed Resource external cloud provider APIs.
  - Ch 23: Tetragon kernel eBPF tracepoints & kprobes, BPF sensor enforcement, real-time security event stream.
  - Ch 24: KubeRay Operator, `RayCluster` CR, Ray Head node, Ray Worker nodes with Plasma shared memory, distributed ML training.
  - Ch 25: Batch scheduling (Volcano Gang Scheduling & PodGroups + Kueue ResourceFlavor & Cohort Workload Queue).
  - Ch 26: Dynamic Resource Allocation (DRA) Controller, `ResourceClaim`, CDI Device Plugin, GPU/TPU/FPGA hardware injection.

- [ ] **Step 2: Generate guides and verify**
Run `uv run python scripts/generate_reference_guides.py`.

- [ ] **Step 3: Commit**
```bash
git add scripts/generate_reference_guides.py docs/guides/2[2-6]-*.md
git commit -m "feat(docs): add rich Mermaid architectural diagrams for chapters 22 to 26"
```

---

### Task 6: Test Suite Verification & Automated Checks

**Files:**
- Modify: `tests/test_reference_guides.py`
- Run: `uv run pytest -q`

- [ ] **Step 1: Add automated tests verifying Mermaid syntax and diagram presence across all 26 guides**
Verify that every `01-*.md` to `26-*.md` file contains a valid ```` ```mermaid ```` block in Section 1 and zero legacy raw ASCII boxes.

- [ ] **Step 2: Run test suite**
Run `uv run pytest -q` and verify all tests pass.

- [ ] **Step 3: Commit**
```bash
git add tests/test_reference_guides.py
git commit -m "test: add automated assertions for Mermaid diagram presence across all 26 guides"
```

---

### Task 7: Build Verification, Merge, and Deployment

**Files:**
- Run: `uv run mkdocs build --strict`
- Run: `git push origin main`

- [ ] **Step 1: Run strict MkDocs build**
Ensure `uv run mkdocs build --strict` runs with 0 errors.

- [ ] **Step 2: Push to `main`**
Push to trigger the GitHub Actions `Deploy Documentation` workflow.

- [ ] **Step 3: Verify live deployment status**
Track workflow run with `gh run watch` to confirm live deployment.

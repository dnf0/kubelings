# Cloud-Native Platform Engineering Curriculum Expansion (Chapters 21, 22, 23)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expand Kubelings to 23 chapters and 102 exercises with advanced CNCF platform engineering tracks: Kubernetes Gateway API (Chapter 21), Crossplane Infrastructure as Data (Chapter 22), and eBPF Kernel Observability with Tetragon (Chapter 23).

**Architecture:** 
- In-memory schema and behavioral evaluators validate resource definitions offline with sub-millisecond execution times.
- Chapter 21 introduces Gateway API standard (GatewayClass, Gateway, HTTPRoute, ReferenceGrant).
- Chapter 22 covers Crossplane platform engineering (XRDs, Compositions, Managed Resources, Developer Claims).
- Chapter 23 covers eBPF runtime security & observability (Tetragon TracingPolicy, execve tracing, file monitoring, kernel Sigkill actions, TCP socket tracing).
- Manifest and curriculum expand to 23 chapters with 102 starter exercises and 102 passing reference solutions.

**Tech Stack:** Python 3.10+, Typer, Rich, Pytest, Ruff, Pyright, Hatchling.

---

### Task 1: Chapter 21 - Kubernetes Gateway API (`21_gateway_api`)

**Files:**
- Create: `exercises/21_gateway_api/gateway01.py` to `gateway04.py`
- Create: `solutions/21_gateway_api/gateway01.py` to `gateway04.py`
- Modify: `src/kubelings/manifest.py`
- Create: `tests/test_chapters_21_23.py`

- [ ] **Step 1: Write starter exercises for Chapter 21**
  - `gateway01.py`: GatewayClass and Gateway resources with listeners.
  - `gateway02.py`: HTTPRoute with path matching and backend service references.
  - `gateway03.py`: Traffic splitting (weighted canary) and URL rewrites.
  - `gateway04.py`: ReferenceGrant for secure cross-namespace routing.

- [ ] **Step 2: Write reference solutions for Chapter 21**
  - Implement complete solutions in `solutions/21_gateway_api/`.

- [ ] **Step 3: Run tests to verify solutions work**

---

### Task 2: Chapter 22 - Crossplane Infrastructure as Code (`22_crossplane_iac`)

**Files:**
- Create: `exercises/22_crossplane_iac/crossplane01.py` to `crossplane04.py`
- Create: `solutions/22_crossplane_iac/crossplane01.py` to `crossplane04.py`
- Modify: `src/kubelings/manifest.py`

- [ ] **Step 1: Write starter exercises for Chapter 22**
  - `crossplane01.py`: CompositeResourceDefinition (XRD) schema.
  - `crossplane02.py`: Composition with field path transforms.
  - `crossplane03.py`: Managed resources and ProviderConfig credentials.
  - `crossplane04.py`: Self-service Developer Claims and connection secrets.

- [ ] **Step 2: Write reference solutions for Chapter 22**
  - Implement complete solutions in `solutions/22_crossplane_iac/`.

- [ ] **Step 3: Run tests to verify solutions work**

---

### Task 3: Chapter 23 - eBPF & Kernel Observability with Tetragon (`23_ebpf_tetragon`)

**Files:**
- Create: `exercises/23_ebpf_tetragon/tetragon01.py` to `tetragon04.py`
- Create: `solutions/23_ebpf_tetragon/tetragon01.py` to `tetragon04.py`
- Modify: `src/kubelings/manifest.py`

- [ ] **Step 1: Write starter exercises for Chapter 23**
  - `tetragon01.py`: TracingPolicy for process execution (sys_execve).
  - `tetragon02.py`: File monitoring for sensitive paths (sys_openat on /etc/shadow).
  - `tetragon03.py`: Kernel-level Sigkill enforcement for unauthorized execution.
  - `tetragon04.py`: eBPF network socket tracing (tcp_connect probes).

- [ ] **Step 2: Write reference solutions for Chapter 23**
  - Implement complete solutions in `solutions/23_ebpf_tetragon/`.

- [ ] **Step 3: Run tests to verify solutions work**

---

### Task 4: Manifest Registration, Test Suite Expansion & Docs

**Files:**
- Modify: `src/kubelings/manifest.py`
- Modify: `tests/test_manifest.py`
- Modify: `tests/test_solutions_and_exercises.py`
- Modify: `README.md`
- Modify: `docs/syllabus.md`
- Modify: `docs/index.md`

- [ ] **Step 1: Update manifest with chapters 21, 22, 23 (102 total exercises)**
- [ ] **Step 2: Run full test suite and verify 102/102 solutions pass**
- [ ] **Step 3: Update documentation and syllabus tables**
- [ ] **Step 4: Commit and verify CI**

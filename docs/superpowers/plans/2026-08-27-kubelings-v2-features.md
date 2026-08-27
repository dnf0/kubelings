# Kubelings v2 Features & Curriculum Expansion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement Kubelings v2 features: a full-screen interactive TUI dashboard, Kubernetes resource topology visualizer (`kubelings tree`), universal manifest linter (`kubelings lint`), and curriculum expansion with Chapters 16, 17, and 18 (82 total exercises).

**Architecture:** 
- Topology visualizer analyzes Kubernetes resource relationships (Workloads ➔ Pods ➔ PVCs ➔ Services ➔ Ingress ➔ Policies) into a Rich hierarchical tree.
- Universal manifest linter inspects YAML/JSON definitions for security, resource limits, probe configurations, and schema rules with line-accurate diagnostics.
- TUI module renders a split-pane curses/Rich layout allowing visual chapter navigation, code preview, live execution, and hint reveals.
- Manifest and curriculum expand to 18 chapters with 82 exercises, complete starter templates, and passing reference solutions.

**Tech Stack:** Python 3.10+, Typer, Rich, Pytest, Ruff, Pyright, Hatchling, MkDocs Material.

---

### Task 1: Kubernetes Resource Topology Visualizer (`kubelings tree`)

**Files:**
- Create: `src/kubelings/topology.py`
- Create: `tests/test_topology.py`
- Modify: `src/kubelings/cli.py`

- [ ] **Step 1: Write tests for topology visualizer**

```python
# tests/test_topology.py
from kubelings.topology import build_resource_topology, render_topology_tree

def test_pod_service_topology():
    manifests = [
        {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {"name": "web-svc", "namespace": "default"},
            "spec": {
                "selector": {"app": "web"},
                "ports": [{"port": 80, "targetPort": 8080}],
            },
        },
        {
            "apiVersion": "v1",
            "kind": "Pod",
            "metadata": {"name": "web-pod-1", "namespace": "default", "labels": {"app": "web"}},
            "spec": {"containers": [{"name": "app", "image": "nginx"}]},
        },
    ]
    tree = build_resource_topology(manifests)
    assert tree is not None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_topology.py -v`
Expected: FAIL (`ModuleNotFoundError: No module named 'kubelings.topology'`)

- [ ] **Step 3: Implement `src/kubelings/topology.py`**

Implement resource relationship mapper (Ingress ➔ Service ➔ Endpoints ➔ Pods, Workloads ➔ PVC ➔ PV, Policies ➔ Workloads) and Rich Tree renderer.

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_topology.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/kubelings/topology.py tests/test_topology.py
git commit --no-gpg-sign -m "feat(topology): add Kubernetes resource relationship visualizer"
```

---

### Task 2: Universal Manifest Linter (`kubelings lint`)

**Files:**
- Create: `src/kubelings/linter.py`
- Create: `tests/test_linter.py`
- Modify: `src/kubelings/cli.py`

- [ ] **Step 1: Write tests for manifest linter**

```python
# tests/test_linter.py
from kubelings.linter import ManifestLinter, LintSeverity

def test_linter_detects_missing_probes_and_security():
    bad_manifest = {
        "apiVersion": "v1",
        "kind": "Pod",
        "metadata": {"name": "insecure-pod"},
        "spec": {
            "containers": [{"name": "web", "image": "nginx"}]
        }
    }
    linter = ManifestLinter()
    diagnostics = linter.lint_manifest(bad_manifest)
    rule_ids = {d.rule_id for d in diagnostics}
    assert "SEC001_RUN_AS_NON_ROOT" in rule_ids
    assert "REL001_MISSING_PROBES" in rule_ids
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_linter.py -v`
Expected: FAIL (`ModuleNotFoundError: No module named 'kubelings.linter'`)

- [ ] **Step 3: Implement `src/kubelings/linter.py`**

Implement `ManifestLinter` with rules for Security (`SEC*`), Reliability & Probes (`REL*`), Resources (`RES*`), and Schema Integrity (`SCH*`), plus colorized Rich diagnostic table renderer.

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_linter.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/kubelings/linter.py tests/test_linter.py
git commit --no-gpg-sign -m "feat(linter): implement manifest linter and best-practices checker"
```

---

### Task 3: Interactive Terminal TUI Dashboard (`kubelings tui`)

**Files:**
- Create: `src/kubelings/tui.py`
- Create: `tests/test_tui.py`
- Modify: `src/kubelings/cli.py`

- [ ] **Step 1: Write tests for TUI state machine & renderer**

```python
# tests/test_tui.py
from kubelings.tui import TuiState, TuiApp
from kubelings.manifest import get_manifest

def test_tui_navigation():
    state = TuiState(manifest=get_manifest())
    assert state.selected_exercise_index == 0
    state.move_down()
    assert state.selected_exercise_index == 1
    state.move_up()
    assert state.selected_exercise_index == 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_tui.py -v`
Expected: FAIL (`ModuleNotFoundError: No module named 'kubelings.tui'`)

- [ ] **Step 3: Implement `src/kubelings/tui.py`**

Implement `TuiState` and `TuiApp` using Rich split layout (Sidebar with exercise status badges, Code Viewer with syntax highlighting, Diagnostics & Output pane, Footer hotkeys).

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_tui.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/kubelings/tui.py tests/test_tui.py
git commit --no-gpg-sign -m "feat(tui): add interactive full-screen terminal dashboard"
```

---

### Task 4: Curriculum Expansion (Chapters 16-18 — 82 Total Exercises)

**Files:**
- Create: `exercises/16_policy_as_code/` (policy01.py to policy04.py)
- Create: `solutions/16_policy_as_code/` (policy01.py to policy04.py)
- Create: `exercises/17_multitenancy_vcluster/` (tenant01.py to tenant04.py)
- Create: `solutions/17_multitenancy_vcluster/` (tenant01.py to tenant04.py)
- Create: `exercises/18_admission_webhooks/` (webhook01.py to webhook04.py)
- Create: `solutions/18_admission_webhooks/` (webhook01.py to webhook04.py)
- Modify: `src/kubelings/manifest.py`
- Create: `tests/test_chapters_16_18.py`
- Modify: `tests/test_manifest.py`
- Modify: `tests/test_solutions_and_exercises.py`

- [ ] **Step 1: Create exercises, solutions, and tests for Chapters 16, 17, 18**
- [ ] **Step 2: Update `src/kubelings/manifest.py` to register Chapters 16, 17, 18 (82 total exercises)**
- [ ] **Step 3: Update `tests/test_manifest.py` and `tests/test_solutions_and_exercises.py`**
- [ ] **Step 4: Run test suite to verify 82/82 exercises fail when broken and pass when solved**

Run: `pytest tests/test_chapters_16_18.py tests/test_solutions_and_exercises.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add exercises/ solutions/ src/kubelings/manifest.py tests/
git commit --no-gpg-sign -m "feat(curriculum): add Chapters 16-18 (Policy as Code, Multi-Tenancy, Webhooks)"
```

---

### Task 5: CLI Integration (`tree`, `lint`, `tui`, `dashboard`)

**Files:**
- Modify: `src/kubelings/cli.py`
- Modify: `tests/test_cli.py`

- [ ] **Step 1: Write CLI command tests for tree, lint, tui, and dashboard**
- [ ] **Step 2: Add CLI commands in `src/kubelings/cli.py`**
- [ ] **Step 3: Run CLI test suite**

Run: `pytest tests/test_cli.py -v`
Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add src/kubelings/cli.py tests/test_cli.py
git commit --no-gpg-sign -m "feat(cli): expose tree, lint, and tui/dashboard commands"
```

---

### Task 6: Documentation & MkDocs Update

**Files:**
- Modify: `README.md`
- Modify: `docs/index.md`
- Modify: `docs/syllabus.md`
- Modify: `docs/cli-reference.md`
- Modify: `scripts/generate_demo_svg.py`

- [ ] **Step 1: Update documentation and syllabus tables for 18 chapters and 82 exercises**
- [ ] **Step 2: Test MkDocs build**

Run: `uvx --with mkdocs-material mkdocs build --strict`
Expected: PASS

- [ ] **Step 3: Commit**

```bash
git add docs/ README.md scripts/generate_demo_svg.py assets/
git commit --no-gpg-sign -m "docs: update documentation for Kubelings v2 features and syllabus"
```

---

### Task 7: Full Verification, Knowledge Graph Update & Remote Push

- [ ] **Step 1: Run comprehensive verification (`ruff check`, `ruff format`, `pyright`, `pytest`, `kubelings test`)**
- [ ] **Step 2: Update knowledge graph (`uvx --from graphifyy graphify update .`)**
- [ ] **Step 3: Push to `main` and monitor GitHub Actions**

# Kubelings Enhancements & Expansion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expand Kubelings with interactive watcher hotkeys, a curriculum self-testing CLI, Chapters 14 & 15 (GitOps & Cilium Service Mesh), hero terminal assets, and a hosted MkDocs documentation site.

**Architecture:** 
- Watcher gains asynchronous keyboard input handling without blocking the filesystem event loop.
- CLI adds `kubelings test` command evaluating reference solutions against schema validators.
- Curriculum manifest expands from 13 to 15 chapters (70 total exercises) with verify tests and starter templates.
- SVG demo generation script captures rich terminal output into an animated SVG for `README.md`.
- MkDocs Material site configured with GitHub Pages workflow for automatic documentation publishing.

**Tech Stack:** Python 3.10+, Typer, Rich, Watchfiles, Pytest, MkDocs Material, GitHub Actions.

---

### Task 1: Interactive Keyboard Controls in Watcher Loop

**Files:**
- Modify: `src/kubelings/watcher.py`
- Modify: `src/kubelings/ui.py`
- Create: `tests/test_watcher_interactive.py`

- [ ] **Step 1: Write the failing test for watcher interactive input handling**

```python
# tests/test_watcher_interactive.py
import pytest
from unittest.mock import MagicMock, patch
from kubelings.manifest import get_manifest
from kubelings.watcher import WatcherState, handle_keypress

def test_handle_keypress_hint():
    state = MagicMock(spec=WatcherState)
    state.current_hint_index = 0
    state.exercise = get_manifest().chapters[0].exercises[0]
    
    new_hint = handle_keypress("h", state)
    assert new_hint == 1
    assert state.current_hint_index == 1

def test_handle_keypress_quit():
    state = MagicMock(spec=WatcherState)
    with pytest.raises(KeyboardInterrupt):
        handle_keypress("q", state)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_watcher_interactive.py -v`
Expected: FAIL with `ImportError: cannot import name 'WatcherState'`

- [ ] **Step 3: Implement WatcherState and handle_keypress in `src/kubelings/watcher.py`**

```python
# Add to src/kubelings/watcher.py:
from dataclasses import dataclass
from typing import Optional
from kubelings.models import Exercise

@dataclass
class WatcherState:
    exercise: Exercise
    current_hint_index: int = 0
    force_rerun: bool = False

def handle_keypress(key: str, state: WatcherState) -> int:
    key = key.lower().strip()
    if key == "q":
        raise KeyboardInterrupt
    elif key == "h":
        max_hints = len(state.exercise.hints)
        if max_hints > 0:
            state.current_hint_index = min(state.current_hint_index + 1, max_hints)
        return state.current_hint_index
    elif key == "r":
        state.force_rerun = True
        return state.current_hint_index
    return state.current_hint_index
```

- [ ] **Step 4: Update `src/kubelings/ui.py` to show interactive hotkeys prompt**

Update watcher footer prompt in `ui.py` to display:
`[dim]Press [bold cyan]h[/bold cyan] hint | [bold cyan]r[/bold cyan] rerun | [bold cyan]l[/bold cyan] list | [bold cyan]q[/bold cyan] quit | [bold cyan]Ctrl+C[/bold cyan] exit[/dim]`

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/test_watcher_interactive.py tests/test_cli.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add src/kubelings/watcher.py src/kubelings/ui.py tests/test_watcher_interactive.py
git commit --no-gpg-sign -m "feat(watcher): add interactive keyboard shortcuts and hint progression"
```

---

### Task 2: Solutions Test Runner CLI (`kubelings test`)

**Files:**
- Modify: `src/kubelings/cli.py`
- Modify: `src/kubelings/runner.py`
- Create: `tests/test_cli_test_solutions.py`

- [ ] **Step 1: Write failing test for `kubelings test` CLI command**

```python
# tests/test_cli_test_solutions.py
from typer.testing import CliRunner
from kubelings.cli import app

runner = CliRunner()

def test_cli_test_solutions():
    result = runner.invoke(app, ["test", "--max-exercises", "2"])
    assert result.exit_code == 0
    assert "Testing Reference Solutions" in result.stdout
    assert "Passed" in result.stdout
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_cli_test_solutions.py -v`
Expected: FAIL (No such command 'test')

- [ ] **Step 3: Implement `test` command in `src/kubelings/cli.py`**

Add `test` CLI command to `src/kubelings/cli.py`:
- Accepts optional `--chapter`, `--exercise`, `--max-exercises`.
- Runs reference solutions in `solutions/` or extracts clean solutions and verifies they execute with exit code 0.
- Prints rich status summary table.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_cli_test_solutions.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/kubelings/cli.py tests/test_cli_test_solutions.py
git commit --no-gpg-sign -m "feat(cli): add 'kubelings test' reference solutions verification command"
```

---

### Task 3: Advanced Curriculum Expansion (Chapters 14 & 15: GitOps & Service Mesh)

**Files:**
- Create: `exercises/14_gitops_argocd/gitops01.py` to `gitops04.py`
- Create: `solutions/14_gitops_argocd/gitops01.py` to `gitops04.py`
- Create: `exercises/15_service_mesh_cilium/mesh01.py` to `mesh04.py`
- Create: `solutions/15_service_mesh_cilium/mesh01.py` to `mesh04.py`
- Modify: `src/kubelings/manifest.py`
- Modify: `src/kubelings/validator.py`
- Create: `tests/test_chapters_14_15.py`

- [ ] **Step 1: Write failing test for Chapters 14 & 15 in `tests/test_chapters_14_15.py`**

```python
# tests/test_chapters_14_15.py
from kubelings.manifest import get_manifest

def test_expanded_chapters_count():
    manifest = get_manifest()
    assert len(manifest.chapters) == 15
    assert len(manifest.all_exercises) == 70

def test_chapter_14_gitops():
    manifest = get_manifest()
    ch14 = next(c for c in manifest.chapters if c.number == 14)
    assert ch14.name == "14_gitops_argocd"
    assert len(ch14.exercises) == 4

def test_chapter_15_service_mesh():
    manifest = get_manifest()
    ch15 = next(c for c in manifest.chapters if c.number == 15)
    assert ch15.name == "15_service_mesh_cilium"
    assert len(ch15.exercises) == 4
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_chapters_14_15.py -v`
Expected: FAIL (assertion 13 == 15)

- [ ] **Step 3: Implement Chapter 14 (GitOps ArgoCD) & Chapter 15 (Service Mesh & Cilium)**
  - `gitops01`: ArgoCD Application CRD (`argoproj.io/v1alpha1`) with automated sync & self-heal policy.
  - `gitops02`: ApplicationSet generator with git directory matrices.
  - `gitops03`: Sync windows and retry backoff configurations.
  - `gitops04`: Argo Rollouts Canary step weight specifications.
  - `mesh01`: CiliumNetworkPolicy L7 HTTP routing and header filtering (`cilium.io/v2`).
  - `mesh02`: Ingress mTLS and Strict PeerAuthentication.
  - `mesh03`: CiliumClusterwideNetworkPolicy with egress CIDR & DNS rules.
  - `mesh04`: Service mesh observability with Hubble metrics and OpenTelemetry tracing annotations.

- [ ] **Step 4: Update `src/kubelings/manifest.py` and `validator.py`**
  - Register chapters 14 & 15 with hints and metadata in `build_manifest()`.
  - Add schema validator rules for `argoproj.io/v1alpha1` (`Application`, `ApplicationSet`, `Rollout`) and `cilium.io/v2` (`CiliumNetworkPolicy`).

- [ ] **Step 5: Run tests and full verification**

Run: `pytest tests/test_chapters_14_15.py tests/test_solutions_and_exercises.py -v`
Expected: All 70 exercises and solutions PASS.

- [ ] **Step 6: Commit**

```bash
git add exercises/ solutions/ src/kubelings/ tests/
git commit --no-gpg-sign -m "feat(curriculum): add Chapter 14 (GitOps ArgoCD) and Chapter 15 (Cilium Service Mesh)"
```

---

### Task 4: Terminal Hero Asset Generator & README Embed

**Files:**
- Create: `scripts/generate_demo_svg.py`
- Create: `assets/demo.svg`
- Modify: `README.md`

- [ ] **Step 1: Write `scripts/generate_demo_svg.py` using Rich Console SVG export**

```python
# scripts/generate_demo_svg.py
from pathlib import Path
from rich.console import Console
from kubelings.ui import render_banner, render_result
from kubelings.runner import RunResult
from kubelings.manifest import get_exercise_by_name

def generate_svg():
    console = Console(record=True, width=95, force_terminal=True)
    render_banner(console)
    ex = get_exercise_by_name("pods01")
    res = RunResult(
        exercise=ex,
        passed=True,
        has_not_done_marker=False,
        output="✓ Pod 'nginx-web' valid!\n✓ Containers spec verified.",
        duration_ms=18.4,
    )
    render_result(res, console)
    
    Path("assets").mkdir(exist_ok=True)
    console.save_svg("assets/demo.svg", title="Kubelings Terminal")
    print("Generated assets/demo.svg")

if __name__ == "__main__":
    generate_svg()
```

- [ ] **Step 2: Generate SVG and verify file**

Run: `python scripts/generate_demo_svg.py && ls -la assets/demo.svg`
Expected: `assets/demo.svg` created (> 5KB)

- [ ] **Step 3: Embed hero asset in `README.md`**

Add `![Kubelings Terminal Demo](assets/demo.svg)` under the hero banner in `README.md`.

- [ ] **Step 4: Commit**

```bash
git add scripts/generate_demo_svg.py assets/demo.svg README.md
git commit --no-gpg-sign -m "docs: add terminal hero SVG demo to README"
```

---

### Task 5: MkDocs Material Site & GitHub Pages Workflow

**Files:**
- Create: `mkdocs.yml`
- Create: `docs/index.md`, `docs/getting-started.md`, `docs/syllabus.md`, `docs/cli-reference.md`
- Create: `.github/workflows/docs.yml`
- Modify: `pyproject.toml` (add `mkdocs-material` to dev dependencies)

- [ ] **Step 1: Configure `mkdocs.yml`**

```yaml
site_name: Kubelings
site_description: An interactive hands-on CLI learning environment for Kubernetes
site_url: https://dnf0.github.io/kubelings/
repo_url: https://github.com/dnf0/kubelings
theme:
  name: material
  palette:
    scheme: slate
    primary: cyan
    accent: deep purple
  features:
    - navigation.instant
    - navigation.sections
    - content.code.copy
nav:
  - Overview: index.md
  - Getting Started: getting-started.md
  - Curriculum Syllabus: syllabus.md
  - CLI Reference: cli-reference.md
```

- [ ] **Step 2: Create documentation markdown files in `docs/`**
- [ ] **Step 3: Create `.github/workflows/docs.yml` for automated GitHub Pages deployment on push to `main`**
- [ ] **Step 4: Test local doc build with `uvx --with mkdocs-material mkdocs build --strict`**
- [ ] **Step 5: Commit**

```bash
git add mkdocs.yml docs/ .github/workflows/docs.yml pyproject.toml
git commit --no-gpg-sign -m "docs: configure MkDocs Material documentation and GitHub Pages CI"
```

---

### Task 6: Final Verification & Release

- [ ] **Step 1: Run full verification suite**
  - `ruff check .`
  - `ruff format --check .`
  - `pyright`
  - `pytest` (all ~380+ tests passing)
- [ ] **Step 2: Rebuild Graphify knowledge graph**
  - `uvx --from graphifyy graphify update .`
- [ ] **Step 3: Push to `main` and verify CI + Semantic Release trigger**

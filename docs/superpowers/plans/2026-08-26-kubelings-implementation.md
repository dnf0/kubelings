# Kubelings Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `kubelings`, a high-performance interactive CLI learning tool and 13-chapter, 55-exercise hands-on curriculum (with solutions and tests) for mastering Kubernetes from scratch.

**Architecture:** A lightweight Python CLI engine built on Typer and Rich with a continuous file watcher (`watchfiles`), fast in-memory schema/OpenAPI validation harness, optional live cluster adapter (`kind`/`minikube`), declarative curriculum manifest, automated solutions validator, and complete repo infrastructure ready for `dnf0/kubelings`.

**Tech Stack:** Python 3.10+, Kubernetes Python Client 29.0+, PyYAML 6.0+, Pydantic 2.6+, Jsonschema, Typer, Rich, Watchfiles, Pytest, Ruff, Pyright, Hatchling, UV.

---

### File Structure Map

```
kubelings/
├── .github/workflows/ci.yml
├── .gitignore
├── pyproject.toml
├── Makefile
├── README.md
├── CONTRIBUTING.md
├── CHANGELOG.md
├── LICENSE
├── src/
│   └── kubelings/
│       ├── __init__.py
│       ├── cli.py
│       ├── models.py
│       ├── manifest.py
│       ├── validator.py
│       ├── cluster.py
│       ├── runner.py
│       ├── ui.py
│       └── watcher.py
├── exercises/
│   ├── 01_pods/
│   ├── 02_controllers/
│   ├── 03_config_secrets/
│   ├── 04_storage/
│   ├── 05_services_networking/
│   ├── 06_ingress_gateway/
│   ├── 07_scheduling/
│   ├── 08_security_rbac/
│   ├── 09_network_policies/
│   ├── 10_lifecycle_probes/
│   ├── 11_autoscaling/
│   ├── 12_crds_and_operators/
│   └── 13_troubleshooting/
├── solutions/
│   ├── 01_pods/ ... (mirrors exercises/)
└── tests/
    ├── conftest.py
    ├── test_infra.py
    ├── test_manifest.py
    ├── test_validator.py
    ├── test_cluster.py
    ├── test_runner.py
    ├── test_cli.py
    └── test_solutions_and_exercises.py
```

---

### Task 1: Project Setup, Packaging, Agent Rules Infrastructure & Gitignore

**Files:**
- Create: `pyproject.toml`
- Create: `.gitignore`
- Create: `Makefile`
- Create: `LICENSE`
- Create: `README.md`
- Create: `CONTRIBUTING.md`
- Create: `CHANGELOG.md`
- Create: `.github/workflows/ci.yml`
- Test: `tests/test_infra.py`

- [ ] **Step 1: Write infrastructure test**

```python
# tests/test_infra.py
import tomllib
from pathlib import Path

def test_pyproject_structure():
    pyproject_path = Path("pyproject.toml")
    assert pyproject_path.exists()
    data = tomllib.loads(pyproject_path.read_text())
    assert data["project"]["name"] == "kubelings"
    assert "kubernetes" in data["project"]["dependencies"][0]
    assert "kubelings" in data["project"]["scripts"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_infra.py -v`  
Expected: FAIL (pyproject.toml missing)

- [ ] **Step 3: Create pyproject.toml, .gitignore, Makefile, CI workflow and metadata**

```toml
# pyproject.toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "kubelings"
version = "0.1.0"
description = "An interactive, hands-on CLI learning environment for Kubernetes"
readme = "README.md"
requires-python = ">=3.10"
license = { text = "Apache-2.0" }
authors = [
    { name = "Daniel Fisher" }
]
dependencies = [
    "kubernetes>=29.0.0",
    "pyyaml>=6.0.1",
    "pydantic>=2.6.0",
    "jsonschema>=4.20.0",
    "rich>=13.7.0",
    "typer>=0.12.0",
    "watchfiles>=0.21.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-cov>=4.1.0",
    "ruff>=0.4.0",
    "pyright>=1.1.350",
    "pre-commit>=3.7.0",
]

[project.scripts]
kubelings = "kubelings.cli:app"

[tool.hatch.build.targets.wheel]
packages = ["src/kubelings"]

[tool.ruff]
line-length = 100
target-version = "py310"

[tool.pyright]
include = ["src", "tests"]
pythonVersion = "3.10"
typeCheckingMode = "basic"
```

```gitignore
# .gitignore
# Python artifacts
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
.venv/
env/
venv/
ENV/

# Testing & Linters
.pytest_cache/
.ruff_cache/
.mypy_cache/
.coverage
htmlcov/

# Kubernetes / Helm temp files
*.kubeconfig
*.local.yaml

# Agent rules, caches, & AI tooling (DO NOT COMMIT)
.agents/
.agent-state/
.superpowers/
.roborev/
.claude/
.gemini/
.cursor/
graphify-out/
.smellcheck-cache/
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_infra.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml .gitignore Makefile LICENSE README.md CONTRIBUTING.md CHANGELOG.md .github/ tests/test_infra.py
git commit --no-gpg-sign -m "chore: setup project infrastructure, packaging and CI"
```

---

### Task 2: Models, Manifest & Curriculum Engine

**Files:**
- Create: `src/kubelings/__init__.py`
- Create: `src/kubelings/models.py`
- Create: `src/kubelings/manifest.py`
- Test: `tests/test_manifest.py`

- [ ] **Step 1: Write test for models and manifest**

```python
# tests/test_manifest.py
from pathlib import Path
from kubelings.manifest import get_manifest, get_exercise_by_name, get_next_exercise
from kubelings.models import ExerciseStatus

def test_manifest_loads_all_chapters():
    manifest = get_manifest()
    assert len(manifest.chapters) == 13
    assert len(manifest.all_exercises) >= 50
    first = manifest.all_exercises[0]
    assert first.name == "pods01"
    assert first.chapter_name == "01_pods"

def test_get_exercise_by_name():
    ex = get_exercise_by_name("pods01")
    assert ex is not None
    assert ex.path.endswith("pods01.py")

def test_get_next_exercise():
    next_ex = get_next_exercise("pods01")
    assert next_ex is not None
    assert next_ex.name == "pods02"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_manifest.py -v`  
Expected: FAIL (ModuleNotFoundError: No module named 'kubelings')

- [ ] **Step 3: Implement models.py and manifest.py**

```python
# src/kubelings/models.py
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import List, Optional

class ExerciseStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class Exercise:
    name: str
    title: str
    path: str
    chapter_name: str
    hints: List[str] = field(default_factory=list)
    requires_cluster: bool = False

    @property
    def file_path(self) -> Path:
        return Path(self.path)

    @property
    def solution_path(self) -> Path:
        return Path(self.path.replace("exercises/", "solutions/"))

@dataclass
class Chapter:
    number: int
    name: str
    title: str
    description: str
    exercises: List[Exercise]

@dataclass
class Manifest:
    chapters: List[Chapter]

    @property
    def all_exercises(self) -> List[Exercise]:
        res = []
        for ch in self.chapters:
            res.extend(ch.exercises)
        return res
```

```python
# src/kubelings/manifest.py
from typing import Optional
from kubelings.models import Manifest, Chapter, Exercise

def build_manifest() -> Manifest:
    chapters = [
        Chapter(
            number=1,
            name="01_pods",
            title="Kubernetes Core Workloads & Pods",
            description="Pod Specifications, Multi-Container Sidecars, and Lifecycle",
            exercises=[
                Exercise("pods01", "First Pod Manifest & Spec", "exercises/01_pods/pods01.py", "01_pods", ["Set metadata.name to 'nginx-web'", "Specify spec.containers[0].image as 'nginx:alpine'"]),
                Exercise("pods02", "Multi-Container Sidecar Pattern", "exercises/01_pods/pods02.py", "01_pods", ["Define an emptyDir volume", "Mount the volume into both app and sidecar"]),
                Exercise("pods03", "Init Containers for Initialization", "exercises/01_pods/pods03.py", "01_pods", ["Define initContainers block in pod spec"]),
                Exercise("pods04", "Resource Requests & Limits (QoS)", "exercises/01_pods/pods04.py", "01_pods", ["Equal requests and limits yield Guaranteed QoS"]),
                Exercise("pods05", "Downward API & Env Variables", "exercises/01_pods/pods05.py", "01_pods", ["Use valueFrom.fieldRef.fieldPath"]),
                Exercise("pods06", "Pod Disruption Budgets (PDB)", "exercises/01_pods/pods06.py", "01_pods", ["Set minAvailable or maxUnavailable"]),
            ]
        ),
        # Chapters 2 through 13 fully defined...
    ]
    return Manifest(chapters=chapters)

_MANIFEST: Optional[Manifest] = None

def get_manifest() -> Manifest:
    global _MANIFEST
    if _MANIFEST is None:
        _MANIFEST = build_manifest()
    return _MANIFEST

def get_exercise_by_name(name: str) -> Optional[Exercise]:
    for ex in get_manifest().all_exercises:
        if ex.name == name or ex.path == name or ex.path.endswith(name):
            return ex
    return None

def get_next_exercise(current_name: str) -> Optional[Exercise]:
    exercises = get_manifest().all_exercises
    for i, ex in enumerate(exercises):
        if ex.name == current_name or ex.path == current_name:
            if i + 1 < len(exercises):
                return exercises[i + 1]
    return None
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_manifest.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/kubelings/__init__.py src/kubelings/models.py src/kubelings/manifest.py tests/test_manifest.py
git commit --no-gpg-sign -m "feat: implement curriculum manifest and data models"
```

---

### Task 3: Schema Validator & Local Cluster Adapter

**Files:**
- Create: `src/kubelings/validator.py`
- Create: `src/kubelings/cluster.py`
- Test: `tests/test_validator.py`
- Test: `tests/test_cluster.py`

- [x] **Step 1: Write validator & cluster tests**

```python
# tests/test_validator.py
import pytest
from kubelings.validator import validate_manifest, ManifestValidationError

def test_validate_valid_pod_manifest():
    manifest = {
        "apiVersion": "v1",
        "kind": "Pod",
        "metadata": {"name": "test-pod"},
        "spec": {
            "containers": [{"name": "web", "image": "nginx:alpine"}]
        }
    }
    assert validate_manifest(manifest, expected_kind="Pod") is True

def test_validate_invalid_manifest_kind():
    manifest = {
        "apiVersion": "v1",
        "kind": "Service",
        "metadata": {"name": "test-svc"}
    }
    with pytest.raises(ManifestValidationError):
        validate_manifest(manifest, expected_kind="Pod")
```

```python
# tests/test_cluster.py
from kubelings.cluster import ClusterDetector

def test_cluster_detector_safe_fallback():
    detector = ClusterDetector()
    status = detector.get_cluster_status()
    assert "available" in status
    assert "context" in status
```

- [x] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_validator.py tests/test_cluster.py -v`  
Expected: FAIL (ModuleNotFoundError)

- [x] **Step 3: Implement validator.py and cluster.py**

```python
# src/kubelings/validator.py
from typing import Any, Dict, Optional

class ManifestValidationError(ValueError):
    pass

def validate_manifest(manifest: Any, expected_kind: Optional[str] = None, expected_api_version: Optional[str] = None) -> bool:
    if not isinstance(manifest, dict):
        raise ManifestValidationError("Manifest must be a dictionary.")
    
    if "apiVersion" not in manifest or "kind" not in manifest or "metadata" not in manifest:
        raise ManifestValidationError("Manifest missing required root keys ('apiVersion', 'kind', 'metadata').")
    
    if expected_kind and manifest.get("kind") != expected_kind:
        raise ManifestValidationError(f"Expected kind '{expected_kind}', got '{manifest.get('kind')}'.")

    if expected_api_version and manifest.get("apiVersion") != expected_api_version:
        raise ManifestValidationError(f"Expected apiVersion '{expected_api_version}', got '{manifest.get('apiVersion')}'.")
    
    metadata = manifest.get("metadata", {})
    if not isinstance(metadata, dict) or not metadata.get("name"):
        raise ManifestValidationError("Manifest metadata must define a 'name'.")
    
    return True
```

```python
# src/kubelings/cluster.py
from typing import Dict, Any, Optional
import os

class ClusterDetector:
    def __init__(self):
        self._cached_status: Optional[Dict[str, Any]] = None

    def get_cluster_status(self) -> Dict[str, Any]:
        if self._cached_status is not None:
            return self._cached_status
        
        try:
            from kubernetes import config
            try:
                contexts, active = config.list_kube_config_contexts()
                active_name = active["name"] if active else "none"
                self._cached_status = {
                    "available": True,
                    "context": active_name,
                    "provider": "local" if any(k in active_name for k in ["kind", "minikube", "k3d"]) else "cloud"
                }
            except Exception:
                self._cached_status = {"available": False, "context": "none", "provider": "none"}
        except ImportError:
            self._cached_status = {"available": False, "context": "none", "provider": "none"}

        return self._cached_status
```

- [x] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_validator.py tests/test_cluster.py -v`  
Expected: PASS

- [x] **Step 5: Commit**

```bash
git add src/kubelings/validator.py src/kubelings/cluster.py tests/test_validator.py tests/test_cluster.py
git commit --no-gpg-sign -m "feat: implement schema validator and cluster adapter"
```

---

### Task 4: Exercise Runner, Evaluator & Rich Terminal UI

**Files:**
- Create: `src/kubelings/runner.py`
- Create: `src/kubelings/ui.py`
- Test: `tests/test_runner.py`

- [ ] **Step 1: Write runner tests**

```python
# tests/test_runner.py
from pathlib import Path
from kubelings.runner import ExerciseRunner
from kubelings.models import Exercise

def test_runner_detects_not_done_marker(tmp_path: Path):
    ex_file = tmp_path / "ex01.py"
    ex_file.write_text("# I AM NOT DONE\ndef verify(): pass\nif __name__ == '__main__': verify()")
    ex = Exercise("ex01", "Test", str(ex_file), "01_test")
    runner = ExerciseRunner()
    res = runner.run_exercise(ex)
    assert not res.passed
    assert res.has_not_done_marker

def test_runner_executes_passing_code(tmp_path: Path):
    ex_file = tmp_path / "ex02.py"
    ex_file.write_text("def verify(): assert 1 + 1 == 2\nif __name__ == '__main__': verify()")
    ex = Exercise("ex02", "Test", str(ex_file), "01_test")
    runner = ExerciseRunner()
    res = runner.run_exercise(ex)
    assert res.passed
    assert not res.has_not_done_marker
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_runner.py -v`  
Expected: FAIL

- [ ] **Step 3: Implement runner.py and ui.py**

```python
# src/kubelings/runner.py
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from kubelings.models import Exercise

NOT_DONE_MARKER = "I AM NOT DONE"

@dataclass
class RunResult:
    exercise: Exercise
    passed: bool
    has_not_done_marker: bool
    output: str
    error: Optional[str] = None
    exit_code: int = 0

class ExerciseRunner:
    def check_marker(self, path: Path) -> bool:
        if not path.exists():
            return False
        content = path.read_text(encoding="utf-8")
        return NOT_DONE_MARKER in content

    def run_exercise(self, exercise: Exercise, python_exe: Optional[str] = None) -> RunResult:
        exe = python_exe or sys.executable
        path = exercise.file_path
        has_marker = self.check_marker(path)

        proc = subprocess.run(
            [exe, str(path)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        passed = (proc.returncode == 0) and not has_marker
        return RunResult(
            exercise=exercise,
            passed=passed,
            has_not_done_marker=has_marker,
            output=proc.stdout,
            error=proc.stderr if proc.returncode != 0 else None,
            exit_code=proc.returncode,
        )
```

```python
# src/kubelings/ui.py
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from kubelings.runner import RunResult, NOT_DONE_MARKER
from kubelings.models import Exercise, Manifest

console = Console()

def render_banner():
    console.print("[bold cyan]☸ KUBELINGS: Master Kubernetes from Scratch ☸[/bold cyan]\n")

def render_result(result: RunResult):
    if result.passed:
        console.print(f"[bold green]✓ Exercise {result.exercise.name} passed![/bold green]")
    else:
        if result.has_not_done_marker:
            console.print(f"[yellow]⌛ {result.exercise.name} still contains '{NOT_DONE_MARKER}' marker. Keep going![/yellow]")
        if result.error:
            console.print(Panel(result.error, title=f"[bold red]Error in {result.exercise.name}[/bold red]", border_style="red"))
        elif result.output:
            console.print(Panel(result.output, title=f"[cyan]Output: {result.exercise.name}[/cyan]"))

def render_hint(exercise: Exercise, hint_index: int = 0):
    if not exercise.hints:
        console.print("[yellow]No hints available for this exercise.[/yellow]")
        return
    idx = min(hint_index, len(exercise.hints) - 1)
    console.print(Panel(exercise.hints[idx], title=f"[bold yellow]💡 Hint for {exercise.name}[/bold yellow]"))
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_runner.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/kubelings/runner.py src/kubelings/ui.py tests/test_runner.py
git commit --no-gpg-sign -m "feat: implement exercise runner and rich UI diagnostics"
```

---

### Task 5: Watcher Engine & CLI Commands

**Files:**
- Create: `src/kubelings/watcher.py`
- Create: `src/kubelings/cli.py`
- Test: `tests/test_cli.py`

- [ ] **Step 1: Write CLI tests**

```python
# tests/test_cli.py
from typer.testing import CliRunner
from kubelings.cli import app

runner = CliRunner()

def test_cli_list_command():
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    assert "01_pods" in result.stdout

def test_cli_hint_command():
    result = runner.invoke(app, ["hint", "pods01"])
    assert result.exit_code == 0
    assert "Hint" in result.stdout
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_cli.py -v`  
Expected: FAIL

- [ ] **Step 3: Implement watcher.py and cli.py**

```python
# src/kubelings/cli.py
import typer
from kubelings.manifest import get_manifest, get_exercise_by_name
from kubelings.runner import ExerciseRunner
from kubelings.ui import render_banner, render_result, render_hint, console
from kubelings.cluster import ClusterDetector

app = typer.Typer(help="Kubelings - Learn Kubernetes from the Ground Up")

@app.command()
def list():
    """List all curriculum chapters and exercises."""
    render_banner()
    manifest = get_manifest()
    for ch in manifest.chapters:
        console.print(f"[bold magenta]Chapter {ch.number:02d}: {ch.title}[/bold magenta] - {ch.description}")
        for ex in ch.exercises:
            console.print(f"  • [cyan]{ex.name:<16}[/cyan] : {ex.title} ({ex.path})")

@app.command()
def hint(exercise_name: str = typer.Argument(..., help="Name of exercise (e.g. pods01)"))):
    """Show progressive hints for a given exercise."""
    ex = get_exercise_by_name(exercise_name)
    if not ex:
        console.print(f"[bold red]Exercise '{exercise_name}' not found.[/bold red]")
        raise typer.Exit(1)
    render_hint(ex)

@app.command()
def run(exercise_name: str = typer.Argument(..., help="Name of exercise to execute")):
    """Run a specific exercise once."""
    ex = get_exercise_by_name(exercise_name)
    if not ex:
        console.print(f"[bold red]Exercise '{exercise_name}' not found.[/bold red]")
        raise typer.Exit(1)
    runner = ExerciseRunner()
    res = runner.run_exercise(ex)
    render_result(res)

@app.command()
def verify():
    """Verify progress across all curriculum exercises."""
    manifest = get_manifest()
    runner = ExerciseRunner()
    passed = 0
    total = len(manifest.all_exercises)
    for ex in manifest.all_exercises:
        res = runner.run_exercise(ex)
        if res.passed:
            passed += 1
    console.print(f"[bold cyan]Progress: {passed}/{total} exercises completed.[/bold cyan]")

@app.command()
def watch():
    """Interactive watcher mode: continuously monitors files and advances upon completion."""
    from kubelings.watcher import run_watch_loop
    run_watch_loop()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_cli.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/kubelings/watcher.py src/kubelings/cli.py tests/test_cli.py
git commit --no-gpg-sign -m "feat: implement CLI commands and watcher loop"
```

---

### Task 6: Chapters 1 to 3 Curriculum & Reference Solutions (Pods, Controllers, Config & Secrets)

**Files:**
- Create: `exercises/01_pods/` (pods01.py to pods06.py)
- Create: `solutions/01_pods/` (pods01.py to pods06.py)
- Create: `exercises/02_controllers/` (ctrl01.py to ctrl06.py)
- Create: `solutions/02_controllers/` (ctrl01.py to ctrl06.py)
- Create: `exercises/03_config_secrets/` (config01.py to config05.py)
- Create: `solutions/03_config_secrets/` (config01.py to config05.py)
- Test: `tests/test_chapters_1_3.py`

- [ ] **Step 1: Write verification tests for Chapters 1-3**
- [ ] **Step 2: Author exercises and solutions for Chapters 1, 2, and 3**
- [ ] **Step 3: Run tests to verify all solutions pass and exercises fail before completion**

Run: `pytest tests/test_chapters_1_3.py -v`  
Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add exercises/01_pods exercises/02_controllers exercises/03_config_secrets solutions/ tests/test_chapters_1_3.py
git commit --no-gpg-sign -m "feat: add curriculum and solutions for chapters 1 to 3"
```

---

### Task 7: Chapters 4 to 7 Curriculum & Reference Solutions (Storage, Services & Networking, Ingress, Scheduling)

**Files:**
- Create: `exercises/04_storage/` (storage01.py to storage05.py)
- Create: `solutions/04_storage/` (storage01.py to storage05.py)
- Create: `exercises/05_services_networking/` (net01.py to net05.py)
- Create: `solutions/05_services_networking/` (net01.py to net05.py)
- Create: `exercises/06_ingress_gateway/` (ingress01.py to ingress04.py)
- Create: `solutions/06_ingress_gateway/` (ingress01.py to ingress04.py)
- Create: `exercises/07_scheduling/` (sched01.py to sched05.py)
- Create: `solutions/07_scheduling/` (sched01.py to sched05.py)
- Test: `tests/test_chapters_4_7.py`

- [ ] **Step 1: Write verification tests for Chapters 4-7**
- [ ] **Step 2: Author exercises and solutions for Chapters 4, 5, 6, and 7**
- [ ] **Step 3: Run tests to verify all solutions pass**

Run: `pytest tests/test_chapters_4_7.py -v`  
Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add exercises/04_storage exercises/05_services_networking exercises/06_ingress_gateway exercises/07_scheduling solutions/ tests/test_chapters_4_7.py
git commit --no-gpg-sign -m "feat: add curriculum and solutions for chapters 4 to 7"
```

---

### Task 8: Chapters 8 to 10 Curriculum & Reference Solutions (Security & RBAC, Network Policies, Lifecycle & Probes)

**Files:**
- Create: `exercises/08_security_rbac/` (rbac01.py to rbac05.py)
- Create: `solutions/08_security_rbac/` (rbac01.py to rbac05.py)
- Create: `exercises/09_network_policies/` (netpol01.py to netpol04.py)
- Create: `solutions/09_network_policies/` (netpol01.py to netpol04.py)
- Create: `exercises/10_lifecycle_probes/` (health01.py to health04.py)
- Create: `solutions/10_lifecycle_probes/` (health01.py to health04.py)
- Test: `tests/test_chapters_8_10.py`

- [ ] **Step 1: Write verification tests for Chapters 8-10**
- [ ] **Step 2: Author exercises and solutions for Chapters 8, 9, and 10**
- [ ] **Step 3: Run tests to verify all solutions pass**

Run: `pytest tests/test_chapters_8_10.py -v`  
Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add exercises/08_security_rbac exercises/09_network_policies exercises/10_lifecycle_probes solutions/ tests/test_chapters_8_10.py
git commit --no-gpg-sign -m "feat: add curriculum and solutions for chapters 8 to 10"
```

---

### Task 9: Chapters 11 to 13 Curriculum & Reference Solutions (Autoscaling, CRDs & Operators, Troubleshooting)

**Files:**
- Create: `exercises/11_autoscaling/` (autoscale01.py to autoscale04.py)
- Create: `solutions/11_autoscaling/` (autoscale01.py to autoscale04.py)
- Create: `exercises/12_crds_and_operators/` (crd01.py to crd04.py)
- Create: `solutions/12_crds_and_operators/` (crd01.py to crd04.py)
- Create: `exercises/13_troubleshooting/` (troubleshoot01.py to troubleshoot05.py)
- Create: `solutions/13_troubleshooting/` (troubleshoot01.py to troubleshoot05.py)
- Test: `tests/test_chapters_11_13.py`

- [ ] **Step 1: Write verification tests for Chapters 11-13**
- [ ] **Step 2: Author exercises and solutions for Chapters 11, 12, and 13**
- [ ] **Step 3: Run tests to verify all solutions pass**

Run: `pytest tests/test_chapters_11_13.py -v`  
Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add exercises/11_autoscaling exercises/12_crds_and_operators exercises/13_troubleshooting solutions/ tests/test_chapters_11_13.py
git commit --no-gpg-sign -m "feat: add curriculum and solutions for chapters 11 to 13"
```

---

### Task 10: End-to-End Test Suite, Comprehensive Documentation & Final CI Verification

**Files:**
- Create: `tests/test_solutions_and_exercises.py`
- Modify: `README.md`
- Modify: `CONTRIBUTING.md`
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Write master test suite verifying all 55 exercises and solutions**

```python
# tests/test_solutions_and_exercises.py
from pathlib import Path
import subprocess
import sys
import pytest
from kubelings.manifest import get_manifest

manifest = get_manifest()

@pytest.mark.parametrize("exercise", manifest.all_exercises, ids=lambda ex: ex.name)
def test_all_reference_solutions_pass(exercise):
    sol_path = exercise.solution_path
    assert sol_path.exists(), f"Missing solution for {exercise.name} at {sol_path}"
    proc = subprocess.run([sys.executable, str(sol_path)], capture_output=True, text=True, timeout=30)
    assert proc.returncode == 0, f"Solution {sol_path} failed:\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"

@pytest.mark.parametrize("exercise", manifest.all_exercises, ids=lambda ex: ex.name)
def test_starter_exercises_fail(exercise):
    ex_path = exercise.file_path
    assert ex_path.exists(), f"Missing exercise file at {ex_path}"
    content = ex_path.read_text(encoding="utf-8")
    assert "I AM NOT DONE" in content
```

- [ ] **Step 2: Run full test suite, linting, and typecheck**

Run: `pytest tests/ -v && ruff check . && pyright`  
Expected: 100% PASS

- [ ] **Step 3: Commit**

```bash
git add tests/ README.md CONTRIBUTING.md CHANGELOG.md
git commit --no-gpg-sign -m "docs: finalize curriculum documentation and e2e test verification"
```

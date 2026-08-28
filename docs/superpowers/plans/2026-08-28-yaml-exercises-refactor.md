# Decouple YAML Exercises & Core Validator Engine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform Kubelings exercises from Python scripts containing embedded YAML strings into native `.yaml` files with pure Kubernetes syntax highlighting, while moving verification logic into a modular, high-performance external validator engine with human-friendly YAML diagnostics.

**Architecture:** 
- Exercise starter and reference solution files become native `.yaml` files (`exercises/<chapter>/<name>.yaml`, `solutions/<chapter>/<name>.yaml`) with instructional headers formatted as standard YAML comments (`#`).
- Verification logic is extracted from user files into a dedicated validator package (`src/kubelings/validators/`) with a decorator-based registry.
- `ExerciseRunner` parses `.yaml` directly, intercepts syntax errors to render clean diagnostic pointers with line/column markers, and executes the registered validator.
- VS Code extension and WebAssembly Playground bundle generator are updated to natively work with `.yaml` exercises.

**Tech Stack:** Python 3.10+, PyYAML, Rich (for formatting diagnostics), TypeScript/VS Code Extension API, Vitest/Node Test Runner, Pytest.

---

### Task 1: Validator Registry & YAML Diagnostic Formatter in Core Engine

**Files:**
- Create: `src/kubelings/validators/__init__.py`
- Modify: `src/kubelings/validator.py`
- Modify: `src/kubelings/runner.py`
- Test: `tests/test_runner_yaml.py`

- [ ] **Step 1: Write failing test in `tests/test_runner_yaml.py`**

```python
from pathlib import Path
import pytest
from kubelings.models import Exercise
from kubelings.runner import ExerciseRunner, format_yaml_error
from kubelings.validators import register_validator, get_validator


def test_validator_registration():
    @register_validator("test_ex01")
    def sample_val(manifest, raw_text):
        assert manifest.get("kind") == "Pod", "Kind must be Pod"

    fn = get_validator("test_ex01")
    assert fn is not None
    with pytest.raises(AssertionError, match="Kind must be Pod"):
        fn({"kind": "Service"}, "")


def test_runner_executes_yaml_exercise(tmp_path: Path):
    ex_file = tmp_path / "test_pod.yaml"
    ex_file.write_text("apiVersion: v1\nkind: Pod\nmetadata:\n  name: my-pod\n", encoding="utf-8")

    @register_validator("test_pod")
    def validate_test_pod(manifest, raw):
        assert manifest["metadata"]["name"] == "my-pod"

    exercise = Exercise(
        name="test_pod",
        title="Test Pod",
        path=str(ex_file),
        chapter_name="01_pods",
    )

    runner = ExerciseRunner()
    result = runner.run_exercise(exercise)
    assert result.passed is True
    assert "✓ test_pod passed!" in result.output


def test_runner_catches_yaml_syntax_error_cleanly(tmp_path: Path):
    bad_yaml = tmp_path / "bad.yaml"
    bad_yaml.write_text("metadata:\n  app: app: web\n", encoding="utf-8")

    exercise = Exercise(
        name="bad_ex",
        title="Bad YAML",
        path=str(bad_yaml),
        chapter_name="01_pods",
    )

    runner = ExerciseRunner()
    result = runner.run_exercise(exercise)
    assert result.passed is False
    assert "YAML Syntax Error" in result.error
    assert "line 2" in result.error.lower()
```

- [ ] **Step 2: Run test to verify failure**

Run: `uv run pytest tests/test_runner_yaml.py -v`
Expected: FAIL with `ModuleNotFoundError` or missing imports.

- [ ] **Step 3: Implement Validator Registry & YAML Runner in Core**

Create `src/kubelings/validators/__init__.py`:
```python
"""Exercise validator registry and module loader."""

from typing import Any, Callable, Optional

ValidatorFunc = Callable[[Any, str], None]
_VALIDATORS: dict[str, ValidatorFunc] = {}


def register_validator(name: str) -> Callable[[ValidatorFunc], ValidatorFunc]:
    """Register a validation function for a specific exercise name."""
    def decorator(fn: ValidatorFunc) -> ValidatorFunc:
        _VALIDATORS[name] = fn
        return fn
    return decorator


def get_validator(name: str) -> Optional[ValidatorFunc]:
    """Retrieve the registered validation function for an exercise."""
    return _VALIDATORS.get(name)


def load_all_validators() -> None:
    """Import all chapter validator modules to populate registry."""
    import importlib
    import pkgutil
    import kubelings.validators as val_pkg

    for _, module_name, _ in pkgutil.iter_modules(val_pkg.__path__):
        if module_name != "__init__":
            importlib.import_module(f"kubelings.validators.{module_name}")
```

Update `src/kubelings/runner.py` to add `format_yaml_error` and native YAML evaluation in `run_exercise`.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_runner_yaml.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git checkout -b refactor/yaml-exercises-architecture
git add src/kubelings/validators/ src/kubelings/runner.py tests/test_runner_yaml.py
git commit --no-gpg-sign -m "feat(core): implement validator registry and native YAML exercise runner"
```

---

### Task 2: Automated Conversion of All 114 Exercises to `.yaml` & Validator Modules

**Files:**
- Create: `scripts/convert_exercises_to_yaml.py`
- Create: `src/kubelings/validators/ch01_pods.py` ... `ch26_hardware_acceleration_dra.py`
- Modify: `exercises/**/*.yaml` (converted from `.py`)
- Modify: `solutions/**/*.yaml` (converted from `.py`)
- Test: `tests/test_all_converted_exercises.py`

- [ ] **Step 1: Write conversion script `scripts/convert_exercises_to_yaml.py`**

The script:
1. Iterates over all 114 exercises in `exercises/` and `solutions/`.
2. Extracts docstring header comments and converts them to `# ` YAML header blocks.
3. Extracts manifest string literals (`POD_MANIFEST`, `DEPLOYMENT_MANIFEST`, etc.) and formats clean `.yaml` files.
4. Extracts `def verify():` logic into corresponding `src/kubelings/validators/ch<XX>_<name>.py` modules with `@register_validator("<name>")`.
5. Removes old `.py` exercise and solution files.

- [ ] **Step 2: Run conversion script**

Run: `uv run python scripts/convert_exercises_to_yaml.py`
Expected: Generates 114 `.yaml` exercises, 114 `.yaml` solutions, and 26 validator modules in `src/kubelings/validators/`.

- [ ] **Step 3: Write test in `tests/test_all_converted_exercises.py` to assert 100% solution parity**

```python
from kubelings.manifest import build_manifest
from kubelings.models import Exercise
from kubelings.runner import ExerciseRunner
from kubelings.validators import load_all_validators


def test_all_114_solutions_pass():
    load_all_validators()
    manifest = build_manifest()
    runner = ExerciseRunner()

    for ex in manifest.all_exercises:
        sol_path = ex.solution_path
        assert sol_path.exists(), f"Missing solution file {sol_path}"
        sol_ex = Exercise(
            name=ex.name,
            title=ex.title,
            path=str(sol_path),
            chapter_name=ex.chapter_name,
        )
        res = runner.run_exercise(sol_ex)
        assert res.passed is True, f"Solution {ex.name} failed: {res.error}"
```

- [ ] **Step 4: Run full test suite to verify all solutions pass**

Run: `uv run pytest tests/test_all_converted_exercises.py -v`
Expected: 114 passed in < 2.0s!

- [ ] **Step 5: Commit**

```bash
git add exercises/ solutions/ src/kubelings/validators/ tests/test_all_converted_exercises.py
git commit --no-gpg-sign -m "refactor(curriculum): convert 114 exercises to native YAML and modular validators"
```

---

### Task 3: Update Manifest, Init, CLI, and Playground Bundle Generator

**Files:**
- Modify: `src/kubelings/manifest.py` (update paths `.py` -> `.yaml`)
- Modify: `src/kubelings/init.py` (copy `.yaml` files)
- Modify: `scripts/build_playground_bundle.py` (bundle `.yaml` files directly)
- Modify: `tests/test_manifest.py`, `tests/test_cli.py`, `tests/test_playground_bundle.py`

- [ ] **Step 1: Update `src/kubelings/manifest.py`**

Replace all `"exercises/<ch>/<ex>.py"` with `"exercises/<ch>/<ex>.yaml"`.

- [ ] **Step 2: Update `scripts/build_playground_bundle.py` & regenerate bundle**

Update bundle generator to read `.yaml` files directly and include all validator modules in bundle JSON.
Run: `uv run python scripts/build_playground_bundle.py`

- [ ] **Step 3: Run Python test suite**

Run: `uv run pytest -v`
Expected: All tests PASS.

- [ ] **Step 4: Commit**

```bash
git add src/kubelings/manifest.py src/kubelings/init.py scripts/build_playground_bundle.py tests/
git commit --no-gpg-sign -m "feat(manifest): update exercise paths to YAML format and regenerate playground bundle"
```

---

### Task 4: Update VS Code Extension & Diagnostics Bridge

**Files:**
- Modify: `extensions/vscode/src/commands.ts`
- Modify: `extensions/vscode/src/pathUtils.ts`
- Modify: `extensions/vscode/test/pathUtils.test.ts`
- Modify: `extensions/vscode/test/commands.test.ts`
- Modify: `extensions/vscode/package.json`

- [ ] **Step 1: Update extension path utilities to support `.yaml` and `.yml`**

Ensure `path.basename(relPath, '.yaml')` and `.yaml` file opening are default.

- [ ] **Step 2: Run extension test suite**

Run: `cd extensions/vscode && npm test`
Expected: 60/60 tests passing.

- [ ] **Step 3: Package, test locally, and verify bundle**

Run: `npm run package && code --install-extension ../../dist/kubelings-vscode.vsix --force`

- [ ] **Step 4: Commit**

```bash
git add extensions/vscode/
git commit --no-gpg-sign -m "fix(vscode): adapt extension commands and path resolution for native YAML exercises"
```

---

### Task 5: End-to-End Verification, Documentation & Release

**Files:**
- Modify: `docs/syllabus.md`, `README.md`, `docs/getting-started.md`
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Run complete verification suite**
  - `uv run pytest -v`
  - `cd extensions/vscode && npm test`
  - `uv run ruff check .`
  - `uv run ruff format --check .`
  - `uv run pyright`
  - `uv run mkdocs build --strict`
  - `uvx --from graphifyy graphify update .`

- [ ] **Step 2: Commit, merge, and release**

```bash
git add .
git commit --no-gpg-sign -m "docs: update curriculum documentation to reflect native YAML exercise architecture"
git checkout main
git merge --ff-only refactor/yaml-exercises-architecture
git push origin main
```

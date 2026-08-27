# WebAssembly (Pyodide) Browser Playground Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and integrate an interactive, client-side WebAssembly browser playground powered by Pyodide, Monaco Editor, and the Kubelings schema validator into the MkDocs site (`docs/playground.md`).

**Architecture:** 
- A Python build script (`scripts/build_playground_bundle.py`) auto-extracts the pure-Python validator and 11 flagship showcase exercises from repository sources into `docs/assets/playground/playground-bundle.json`.
- A dedicated background Web Worker (`playground-worker.js`) runs Pyodide WebAssembly (Python 3.12), mounts the in-memory bundle, executes AST validations in under 15ms, and posts colorized ANSI diagnostic outputs back to the UI.
- The browser UI (`playground.js`, `playground.css`, Monaco Editor) provides exercise navigation, instant `Ctrl+Enter` evaluation, progressive hint revealing, side-by-side solution diffing, and MkDocs theme synchronization.

**Tech Stack:** Python 3.12, Pyodide v0.26+, Monaco Editor (VS Code Browser ESM), JavaScript (ES6+ Web Workers), HTML5/CSS3 flexbox, MkDocs Material, Pytest.

---

## File Structure Map

| File Path | Role | Responsibility |
| :--- | :--- | :--- |
| `scripts/build_playground_bundle.py` | Build Generator | Serializes `src/kubelings/validator.py`, models, and 11 curated exercises/solutions/hints to JSON. |
| `tests/test_playground_bundle.py` | Pytest Harness | Validates bundle structure, starter failure behavior, and solution pass parity. |
| `docs/assets/playground/playground-worker.js` | Web Worker Engine | Loads Pyodide in WebAssembly, loads PyYAML, mounts `/lib/kubelings/`, evaluates code in sandbox. |
| `docs/assets/playground/playground.css` | Styling | Split-pane layout, terminal styling, dark/light theme variables, mobile responsiveness. |
| `docs/assets/playground/playground.js` | UI Controller | Monaco Editor lifecycle, action button handlers, worker RPC, progressive hints, diff editor. |
| `docs/playground.md` | MkDocs Page | Top-level documentation page hosting the playground container and quickstart instructions. |
| `mkdocs.yml` | Navigation Config | Registers `Playground: playground.md` in top-level site navigation. |

---

## Tasks

### Task 1: Playground Bundle Generator Script & Automated Parity Tests

**Files:**
- Create: `scripts/build_playground_bundle.py`
- Create: `tests/test_playground_bundle.py`

- [ ] **Step 1: Write the failing pytest test for bundle generation**

In `tests/test_playground_bundle.py`:
```python
import json
import subprocess
from pathlib import Path


def test_playground_bundle_generation():
    repo_root = Path(__file__).parent.parent
    bundle_script = repo_root / "scripts" / "build_playground_bundle.py"
    bundle_path = repo_root / "docs" / "assets" / "playground" / "playground-bundle.json"

    # Run the generator script
    result = subprocess.run(
        ["uv", "run", "python", str(bundle_script)],
        capture_output=True,
        text=True,
        cwd=str(repo_root),
    )
    assert result.returncode == 0, f"Script failed with: {result.stderr}"
    assert bundle_path.exists(), "playground-bundle.json was not created"

    data = json.loads(bundle_path.read_text(encoding="utf-8"))
    assert "validator_code" in data
    assert "exercises" in data

    # Verify 11 flagship showcase exercises
    expected_ids = [
        "pods01",
        "ctrl01",
        "config01",
        "storage01",
        "sched01",
        "netpol01",
        "autoscale01",
        "gitops01",
        "gateway01",
        "ray01",
        "accel02",
    ]
    for ex_id in expected_ids:
        assert ex_id in data["exercises"], f"Missing exercise {ex_id}"
        ex = data["exercises"][ex_id]
        assert "title" in ex
        assert "chapter" in ex
        assert "starter_code" in ex
        assert "solution_code" in ex
        assert "hints" in ex
        assert len(ex["hints"]) >= 2
```

- [ ] **Step 2: Run test to verify failure**

Run: `uv run pytest tests/test_playground_bundle.py -v`
Expected: FAIL with file not found or script missing.

- [ ] **Step 3: Implement `scripts/build_playground_bundle.py`**

In `scripts/build_playground_bundle.py`:
```python
#!/usr/bin/env python3
"""Build script to bundle Kubelings validator, models, and curated showcase exercises

into a single JSON asset for the Pyodide WebAssembly browser playground.
"""

from __future__ import annotations

import json
from pathlib import Path

from kubelings.manifest import CHAPTERS, get_exercise_by_name

SHOWCASE_EXERCISE_IDS = [
    "pods01",
    "ctrl01",
    "config01",
    "storage01",
    "sched01",
    "netpol01",
    "autoscale01",
    "gitops01",
    "gateway01",
    "ray01",
    "accel02",
]


def build_bundle() -> dict:
    repo_root = Path(__file__).parent.parent
    validator_path = repo_root / "src" / "kubelings" / "validator.py"
    models_path = repo_root / "src" / "kubelings" / "models.py"

    validator_code = validator_path.read_text(encoding="utf-8")
    models_code = models_path.read_text(encoding="utf-8")

    exercises_data = {}

    for ex_id in SHOWCASE_EXERCISE_IDS:
        manifest_ex = get_exercise_by_name(ex_id)
        if not manifest_ex:
            raise ValueError(f"Exercise {ex_id} not found in manifest!")

        # Find chapter name
        chapter_name = "unknown"
        for ch in CHAPTERS:
            if any(e.name == ex_id for e in ch.exercises):
                chapter_name = ch.name
                break

        starter_path = repo_root / manifest_ex.path
        solution_path = repo_root / f"solutions/{chapter_name}/{manifest_ex.filename}"

        if not starter_path.exists():
            raise FileNotFoundError(f"Starter file {starter_path} does not exist!")
        if not solution_path.exists():
            raise FileNotFoundError(f"Solution file {solution_path} does not exist!")

        starter_code = starter_path.read_text(encoding="utf-8")
        solution_code = solution_path.read_text(encoding="utf-8")

        exercises_data[ex_id] = {
            "id": manifest_ex.name,
            "title": manifest_ex.title,
            "chapter": chapter_name,
            "filename": manifest_ex.filename,
            "topic": manifest_ex.title,
            "hints": manifest_ex.hints,
            "starter_code": starter_code,
            "solution_code": solution_code,
        }

    return {
        "version": "0.7.0",
        "validator_code": validator_code,
        "models_code": models_code,
        "exercises": exercises_data,
    }


def main():
    repo_root = Path(__file__).parent.parent
    out_dir = repo_root / "docs" / "assets" / "playground"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "playground-bundle.json"

    bundle = build_bundle()
    out_file.write_text(json.dumps(bundle, indent=2), encoding="utf-8")
    print(f"✓ Generated playground bundle with {len(bundle['exercises'])} exercises at {out_file}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_playground_bundle.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add scripts/build_playground_bundle.py tests/test_playground_bundle.py docs/assets/playground/playground-bundle.json
git commit --no-gpg-sign -m "feat(playground): add bundle generator script and automated pytest tests"
```

---

### Task 2: Pyodide Web Worker Background Engine

**Files:**
- Create: `docs/assets/playground/playground-worker.js`

- [ ] **Step 1: Implement `playground-worker.js`**

Implement background Web Worker with Pyodide v0.26+ CDN loading, package installation (`pyyaml`), in-memory `/lib/kubelings/` filesystem setup, and sandboxed runner function:

```javascript
// Web Worker for Kubelings Pyodide WebAssembly Runtime
importScripts("https://cdn.jsdelivr.net/pyodide/v0.26.2/full/pyodide.js");

let pyodide = null;
let bundleData = null;

async function initPyodide(bundle) {
  bundleData = bundle;
  self.postMessage({ type: "STATUS", stage: "loading_pyodide", message: "⚡ Initializing Python WebAssembly Runtime..." });
  
  pyodide = await loadPyodide({
    indexURL: "https://cdn.jsdelivr.net/pyodide/v0.26.2/full/"
  });

  self.postMessage({ type: "STATUS", stage: "installing_packages", message: "📦 Loading PyYAML pure-Python engine..." });
  await pyodide.loadPackage(["pyyaml"]);

  self.postMessage({ type: "STATUS", stage: "mounting_bundle", message: "🔧 Mounting Kubelings Schema Validator..." });
  
  // Create /lib/kubelings virtual module in Pyodide FS
  pyodide.FS.mkdirTree("/lib/kubelings");
  pyodide.FS.writeFile("/lib/kubelings/__init__.py", "");
  pyodide.FS.writeFile("/lib/kubelings/models.py", bundle.models_code);
  pyodide.FS.writeFile("/lib/kubelings/validator.py", bundle.validator_code);

  // Setup Python sys.path and in-memory test runner
  await pyodide.runPythonAsync(`
import sys
import io
import time
import importlib
import traceback

if "/lib" not in sys.path:
    sys.path.insert(0, "/lib")

import kubelings.validator as validator

def run_user_code(user_code_str, filename="exercise.py"):
    start_time = time.perf_counter()
    stdout_buf = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = stdout_buf
    
    global_env = {"__name__": "__main__"}
    try:
        exec(user_code_str, global_env)
        
        # Look for manifest or validation logic
        duration = (time.perf_counter() - start_time) * 1000
        output_str = stdout_buf.getvalue()
        return {
            "passed": True,
            "error": None,
            "output": output_str if output_str else "✓ Exercise passed all schema validations and assertions!",
            "durationMs": round(duration, 2)
        }
    except AssertionError as ae:
        duration = (time.perf_counter() - start_time) * 1000
        return {
            "passed": False,
            "error": str(ae) if str(ae) else "AssertionError: validation constraint failed",
            "output": stdout_buf.getvalue(),
            "durationMs": round(duration, 2)
        }
    except Exception as e:
        duration = (time.perf_counter() - start_time) * 1000
        tb = traceback.format_exc()
        return {
            "passed": False,
            "error": f"{type(e).__name__}: {e}",
            "traceback": tb,
            "output": stdout_buf.getvalue(),
            "durationMs": round(duration, 2)
        }
    finally:
        sys.stdout = old_stdout
`);

  self.postMessage({ type: "STATUS", stage: "ready", message: "✅ Ready! Python 3.12 WebAssembly loaded." });
}

self.onmessage = async function(e) {
  const msg = e.data;
  if (msg.type === "INIT") {
    try {
      await initPyodide(msg.bundle);
    } catch (err) {
      self.postMessage({ type: "STATUS", stage: "error", message: "Error initializing Pyodide: " + err.message });
    }
  } else if (msg.type === "RUN_EXERCISE") {
    if (!pyodide) {
      self.postMessage({
        type: "RUN_RESULT",
        exerciseId: msg.exerciseId,
        passed: false,
        error: "Pyodide is still initializing...",
        durationMs: 0
      });
      return;
    }

    try {
      pyodide.globals.set("temp_code_str", msg.code);
      pyodide.globals.set("temp_filename", msg.filename || "exercise.py");
      
      const resProxy = await pyodide.runPythonAsync("run_user_code(temp_code_str, temp_filename)");
      const resultObj = resProxy.toJs({ dict_converter: Object.fromEntries });
      resProxy.destroy();

      self.postMessage({
        type: "RUN_RESULT",
        exerciseId: msg.exerciseId,
        ...resultObj
      });
    } catch (err) {
      self.postMessage({
        type: "RUN_RESULT",
        exerciseId: msg.exerciseId,
        passed: false,
        error: "Execution Error: " + err.message,
        durationMs: 0
      });
    }
  }
};
```

- [ ] **Step 2: Commit**

```bash
git add docs/assets/playground/playground-worker.js
git commit --no-gpg-sign -m "feat(playground): implement Pyodide Web Worker execution engine"
```

---

### Task 3: Monaco Editor, ANSI Output & Interactive UI Controller

**Files:**
- Create: `docs/assets/playground/playground.css`
- Create: `docs/assets/playground/playground.js`

- [ ] **Step 1: Implement `docs/assets/playground/playground.css`**
Responsive split-pane flex layout, action toolbar with modern icons, styled status pill, terminal container with dark background, font family `ui-monospace, monospace`, and mobile breakpoint.

- [ ] **Step 2: Implement `docs/assets/playground/playground.js`**
- Loads Monaco Editor via AMD loader / CDN.
- Loads `playground-bundle.json` and spawns `playground-worker.js`.
- Syncs MkDocs dark/light theme toggle dynamically (`vs-dark` vs. `vs`).
- Handles `▶ Run Solution` button (`Ctrl+Enter` / `Cmd+Enter`), `↺ Reset Code` button, `💡 Reveal Hint` progressive cycle, and `🔍 Compare Solution` diff editor toggle.
- Formats diagnostic error messages, stack traces, and execution timings in the terminal pane.

- [ ] **Step 3: Commit**

```bash
git add docs/assets/playground/playground.css docs/assets/playground/playground.js
git commit --no-gpg-sign -m "feat(playground): add Monaco Editor controller, theme sync, and styling"
```

---

### Task 4: MkDocs Integration & End-to-End Build Verification

**Files:**
- Create: `docs/playground.md`
- Modify: `mkdocs.yml`
- Modify: `README.md`
- Modify: `docs/index.md`
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Create `docs/playground.md`**
Embed the full playground HTML shell, action buttons, Monaco editor container, and output console. Include quick tips for keyboard shortcuts and exercise navigation.

- [ ] **Step 2: Update `mkdocs.yml`**
Add `- Interactive Playground: playground.md` under `nav:`.

- [ ] **Step 3: Run full verification suite**
Run:
- `uv run pytest -v` (assert 100% test pass including bundle tests)
- `uv run ruff check .` and `uv run ruff format --check .`
- `uv run pyright`
- `uv run mkdocs build --strict`
- `make vscode-test`

- [ ] **Step 4: Commit and update knowledge graph**
```bash
git add docs/playground.md mkdocs.yml README.md docs/index.md CHANGELOG.md
git commit --no-gpg-sign -m "feat(docs): integrate WebAssembly playground into documentation navigation"
uvx --from graphifyy graphify update .
```

---

## Verification Plan

### Automated Tests:
- `uv run pytest tests/test_playground_bundle.py -v`: Tests bundle generation, exercise count, metadata schema, and starter/solution parity.
- `uv run pytest -v`: All 570+ existing Python tests pass.
- `make vscode-test`: All 44 VS Code extension tests pass.
- `uv run mkdocs build --strict`: Documentation site builds cleanly with zero broken internal links.

### Manual / Browser Verification:
- Run `uv run mkdocs serve` and visit `http://127.0.0.1:8000/playground/`.
- Test running `pods01` starter (fails with clear diagnostic message).
- Fix `pods01` (passes with green checkmark and `< 15ms` execution time).
- Test Hint button (reveals Hint 1, Hint 2).
- Test Diff button (opens side-by-side Monaco Diff Editor).
- Switch exercises to `ray01` and `accel02` (loads starter code seamlessly).

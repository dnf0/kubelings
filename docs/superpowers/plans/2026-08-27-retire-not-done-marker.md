# Retire '# I AM NOT DONE' & Implement Pure Validation Advancement Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Eliminate the legacy `# I AM NOT DONE` comment requirement from the entire Kubelings platform, replacing it with pure test-driven evaluation, idiomatic Python `# TODO` placeholders, and interactive keystroke navigation (`[n]` for next, `[p]` for previous) in both CLI and VS Code extension.

**Architecture:** 
1. **Core Runner**: Refactor `ExerciseRunner` so that passing relies strictly on execution exit code and assertion/schema validity.
2. **Watcher Engine**: Enhance `WatchEngine` and keyboard handler so that when an exercise passes, the user is presented with celebratory green diagnostics and can press `n`/`Enter` to advance or `p` to revisit.
3. **Curriculum Cleansing**: Strip `# I AM NOT DONE` from all 102 exercises in `exercises/*/*.py` and replace with clear `# TODO:` guidelines while ensuring initial state fails assertions.
4. **VS Code Extension**: Clean `KubelingsDiagnosticsProvider` to only emit real syntax/validation error diagnostics in the Problems panel.
5. **Documentation**: Update all references in README, guides, and syllabus.

**Tech Stack:** Python 3.10+, Typer, Rich, Watchfiles, TypeScript, VS Code Extension API.

---

### Task 1: Refactor Runner & Models for Pure Validation Evaluation

**Files:**
- Modify: `src/kubelings/runner.py`
- Modify: `tests/test_runner.py`
- Modify: `tests/test_cli_json.py`

- [ ] **Step 1: Write failing tests in `tests/test_runner.py` for pure validation execution without marker checks**

```python
def test_runner_passes_purely_on_exit_code_zero(tmp_path: Path):
    script = tmp_path / "valid_ex.py"
    script.write_text("print('All checks pass')\n")
    ex = Exercise(name="valid01", title="Valid", path=str(script), chapter_name="01_pods")
    runner_obj = ExerciseRunner()
    result = runner_obj.run_exercise(ex)
    assert result.passed is True
    assert result.has_not_done_marker is False
    assert result.exit_code == 0
```

- [ ] **Step 2: Run test to verify behavior**

Run: `uv run pytest tests/test_runner.py -v`

- [ ] **Step 3: Modify `src/kubelings/runner.py` to remove marker-blocking logic**

Update `ExerciseRunner.run_exercise()`:
- `has_not_done_marker` becomes an informational flag (defaults to `False`, never blocks `result.passed`).
- `passed = (proc.returncode == 0)`.
- `check_marker()` returns `False` or retains optional backward compatibility without failing passing runs.

- [ ] **Step 4: Run test suite to verify tests pass**

Run: `uv run pytest tests/test_runner.py tests/test_cli_json.py -v`

- [ ] **Step 5: Commit changes**

```bash
git add src/kubelings/runner.py tests/test_runner.py tests/test_cli_json.py
git commit --no-gpg-sign -m "feat(runner): remove NOT_DONE_MARKER requirement and enforce pure validation"
```

---

### Task 2: Enhance Watcher Loop with Interactive Advancement & Navigation

**Files:**
- Modify: `src/kubelings/watcher.py`
- Modify: `src/kubelings/ui.py`
- Modify: `tests/test_watcher_interactive.py`
- Modify: `tests/test_cli.py`

- [ ] **Step 1: Write failing tests for keystroke navigation (`[n]`, `[p]`, `[Enter]`) on passing exercises**

```python
def test_watcher_advances_on_n_or_enter_key():
    engine = WatchEngine(start_exercise="pods01")
    # Verify advancing to next incomplete exercise on 'n' or enter
    next_ex = engine.handle_input_key("n")
    assert next_ex is not None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_watcher_interactive.py -v`

- [ ] **Step 3: Implement interactive navigation in `src/kubelings/watcher.py` and `src/kubelings/ui.py`**

- `ui.render_result()`: render green pass panel with clear footer: `[n/Enter] Advance to next exercise | [p] Previous | [h] Hint | [q] Quit`.
- `WatchEngine.handle_input_key()`: support `n`, `Enter`, `p`, `h`, `r`, `l`, `q`.
- `find_next_incomplete_exercise()`: finds the first exercise that fails validation.

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_watcher_interactive.py tests/test_cli.py -v`

- [ ] **Step 5: Commit changes**

```bash
git add src/kubelings/watcher.py src/kubelings/ui.py tests/test_watcher_interactive.py tests/test_cli.py
git commit --no-gpg-sign -m "feat(watcher): add interactive [n] and [p] navigation on passing exercises"
```

---

### Task 3: Clean All 102 Exercises & Update Parity Tests

**Files:**
- Modify: `exercises/*/*.py` (All 102 files)
- Modify: `tests/test_solutions_and_exercises.py`
- Modify: `src/kubelings/cli.py`

- [ ] **Step 1: Write test in `tests/test_solutions_and_exercises.py` asserting exercises fail on assertion/schema check (not marker)**

```python
def test_exercises_fail_on_schema_or_assertion():
    runner = ExerciseRunner()
    manifest = get_manifest()
    for ex in manifest.all_exercises:
        res = runner.run_exercise(ex)
        assert res.passed is False, f"Starter exercise {ex.name} should fail initial assertions"
```

- [ ] **Step 2: Run test to observe failures on any starter exercises**

Run: `uv run pytest tests/test_solutions_and_exercises.py -v`

- [ ] **Step 3: Remove `# I AM NOT DONE` from all 102 files in `exercises/`**

Run a clean script replacing `# I AM NOT DONE` with `# TODO: Complete the Kubernetes manifest specification...` across all `exercises/*/*.py` files, ensuring each starter exercise fails its initial assertion cleanly.

- [ ] **Step 4: Run full exercise & solution test suite**

Run: `uv run pytest tests/test_solutions_and_exercises.py -v`

- [ ] **Step 5: Commit changes**

```bash
git add exercises/ tests/test_solutions_and_exercises.py src/kubelings/cli.py
git commit --no-gpg-sign -m "chore(curriculum): remove I AM NOT DONE marker from all 102 exercises"
```

---

### Task 4: Update VS Code Extension Diagnostics & Tests

**Files:**
- Modify: `extensions/vscode/src/diagnostics.ts`
- Modify: `extensions/vscode/test/diagnostics.test.ts`
- Modify: `extensions/vscode/test/commands.test.ts`

- [ ] **Step 1: Update TypeScript tests in `extensions/vscode/test/diagnostics.test.ts`**

Remove `# I AM NOT DONE` diagnostic test expectations, replace with tests verifying diagnostics are created only for real errors and cleared on pass.

- [ ] **Step 2: Run extension tests to verify failure**

Run: `make vscode-test`

- [ ] **Step 3: Update `extensions/vscode/src/diagnostics.ts`**

Remove `NOT_DONE_MARKER` scanning and warning diagnostic creation. Only emit errors on actual traceback / execution failures.

- [ ] **Step 4: Run extension tests and re-build**

Run: `make vscode-test && make vscode-build`

- [ ] **Step 5: Commit changes**

```bash
git add extensions/vscode/
git commit --no-gpg-sign -m "feat(vscode): remove NOT_DONE warning diagnostics and streamline editor validation"
```

---

### Task 5: Documentation Updates & End-to-End Verification

**Files:**
- Modify: `README.md`
- Modify: `docs/index.md`
- Modify: `docs/getting-started.md`
- Modify: `extensions/vscode/README.md`

- [ ] **Step 1: Update documentation files to reflect pure validation and `[n]` navigation**
- [ ] **Step 2: Run full verification suite**

Run:
```bash
uv run pytest
make vscode-test
uv run ruff check .
uv run ruff format --check .
uv run pyright
make vscode-package
uvx --from graphifyy graphify update .
```

- [ ] **Step 3: Commit documentation & graph updates**

```bash
git add README.md docs/ extensions/vscode/README.md graphify-out/
git commit --no-gpg-sign -m "docs: update guides and docs for pure test-driven exercise advancement"
```

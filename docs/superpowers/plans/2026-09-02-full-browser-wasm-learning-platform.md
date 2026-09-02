# Full Browser WebAssembly Learning Platform Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the full 114-exercise in-browser Kubernetes learning platform powered by Pyodide WebAssembly with client-side localStorage state persistence and an interactive split-pane syllabus UI.

**Architecture:** A build-time generator packages all 114 exercises and 26 chapters into `playground-bundle.json`. A background Web Worker runs Pyodide WebAssembly with the in-memory Kubelings validation engine. A client-side state engine (`KubelingsStorage`) manages progress and code persistence in `localStorage`. The split-pane UI provides a searchable curriculum sidebar on the left and Monaco Editor + ANSI Terminal Diagnostics on the right.

**Tech Stack:** Python 3.12, Pyodide v0.26+ (WebAssembly), Monaco Editor, Vanilla JS / ES6, CSS Grid/Flexbox, MkDocs Material, Pytest.

## Global Constraints

- **Python Version:** `>=3.10`
- **Exercises:** All 114 exercises across 26 chapters must be bundled and accessible.
- **Evaluation Speed:** Pyodide Web Worker must evaluate submissions in `<25ms`.
- **State Storage:** Persisted locally under `localStorage` key `kubelings_learning_state_v1`. Zero backend requirements.
- **Theme Sync:** Seamless dark/light theme switching with MkDocs Material.
- **Strict Checks:** Must pass `ruff check`, `pyright`, `pytest`, and `mkdocs build --strict`.

---

### Task 1: Expand Playground Bundle Generator & Tests for Full 114 Curriculum

**Files:**
- Modify: `scripts/build_playground_bundle.py`
- Modify: `tests/test_playground_bundle.py`
- Test: `pytest tests/test_playground_bundle.py`

**Interfaces:**
- Consumes: `src/kubelings/manifest.py:get_manifest()`
- Produces: `docs/assets/playground/playground-bundle.json` with keys: `version`, `validator_code`, `models_code`, `chapters`, `exercises`.

- [ ] **Step 1: Write failing tests for full 114 exercise bundle generation**

Update `tests/test_playground_bundle.py` to assert that:
1. `bundle["chapters"]` contains all 26 chapters with `number`, `name`, `title`, `description`, `exercise_ids`.
2. `bundle["exercises"]` contains all 114 exercises with valid `starter_code`, `solution_code`, `hints`, and `requires_cluster`.
3. The total exercise count is 114.

- [ ] **Step 2: Run test to confirm failure**

```bash
pytest tests/test_playground_bundle.py
```

- [ ] **Step 3: Update `scripts/build_playground_bundle.py`**

Refactor `build_bundle()` to:
1. Load the manifest using `get_manifest()`.
2. Iterate through all chapters and all exercises.
3. Include chapter metadata (`number`, `name`, `title`, `description`, `exercise_ids`).
4. Read `starter_code` and `solution_code` for each exercise.
5. Record `requires_cluster` flag for each exercise.
6. Write the full bundle to `docs/assets/playground/playground-bundle.json`.

- [ ] **Step 4: Run tests and verify bundle generation**

```bash
pytest tests/test_playground_bundle.py
```

- [ ] **Step 5: Commit changes**

```bash
git add scripts/build_playground_bundle.py tests/test_playground_bundle.py
git commit --no-gpg-sign -m "feat(playground): expand bundle generator to package all 114 exercises"
```

---

### Task 2: Implement Client-Side State Persistence Engine (`KubelingsStorage`)

**Files:**
- Modify: `docs/assets/playground/playground.js`
- Test: `tests/test_playground_bundle.py`

**Interfaces:**
- Consumes: `localStorage`, `playground-bundle.json`
- Produces: `KubelingsStorage` module in `playground.js` managing `kubelings_learning_state_v1`.

- [ ] **Step 1: Implement `KubelingsStorage` class in `playground.js`**

Implement:
1. `STORAGE_KEY = "kubelings_learning_state_v1"`.
2. `init(bundle)`: Loads state from localStorage or initializes default state from the bundle.
3. `getExerciseState(exerciseId)`: Returns `{ status, userCode, hintsRevealed, lastEvaluatedAt, passedAt }`.
4. `saveExerciseCode(exerciseId, code)`: Debounced update to localStorage.
5. `setExerciseStatus(exerciseId, status, passedAt)`: Updates completion status and recalculates global stats.
6. `revealHint(exerciseId)`: Increments hint tier in storage.
7. `resetExercise(exerciseId, starterCode)`: Reverts user code to starter template.
8. `exportProgressJSON()`: Returns formatted JSON string for backup.
9. `importProgressJSON(jsonString)`: Validates and loads backup JSON.
10. `resetAllProgress()`: Clears storage key and re-initializes.

- [ ] **Step 2: Integrate `KubelingsStorage` with Monaco Editor lifecycle**

1. When switching exercises, load user's saved code (or starter code if first time).
2. Attach `onDidChangeModelContent` listener on Monaco Editor to auto-save code to storage.
3. Update hint reveal button to track revealed hint tier in storage.

- [ ] **Step 3: Commit changes**

```bash
git add docs/assets/playground/playground.js
git commit --no-gpg-sign -m "feat(playground): implement client-side KubelingsStorage engine"
```

---

### Task 3: Implement Interactive Split-Pane Workspace & 26-Chapter Syllabus UI

**Files:**
- Modify: `docs/assets/playground/playground.js`
- Modify: `docs/assets/playground/playground.css`
- Modify: `docs/playground.md`

**Interfaces:**
- Consumes: `KubelingsStorage`, `playground-bundle.json`, Monaco Editor API
- Produces: Full split-view layout with collapsible chapter accordion, live search, progress bar, action toolbar, hint drawer, and diff editor.

- [ ] **Step 1: Build Syllabus Sidebar Component in `playground.js`**

1. Render header with global progress bar (`X / 114 Completed • Y%`) and Export/Import/Reset action buttons.
2. Render search input with real-time filtering across exercise titles, IDs, concepts, and completion status.
3. Render 26 collapsible chapter accordions with completion badges (e.g. `01. Pods & Manifests (4/4 ✓)`).
4. Render exercise items with status icons (`✓` completed, `⏳` in-progress, `○` not-started) and `Live Cluster` tags.
5. Handle active exercise selection and automatic scroll into view.

- [ ] **Step 2: Build Workspace Header & Navigation Controls**

1. Add breadcrumb navigation showing Chapter Number, Chapter Title, and Exercise Title.
2. Add `← Prev` and `Next →` navigation buttons.
3. Add celebration overlay / auto-advance banner on test pass.

- [ ] **Step 3: Style Split-Pane Layout in `playground.css`**

1. Implement CSS Grid split-pane: Left sidebar (`320px`), Right workspace (`1fr`).
2. Style collapsible chapter accordions with smooth transition animations.
3. Style search box, status badges, progress bar, and action buttons.
4. Ensure responsive behavior for smaller viewports (collapsible drawer on mobile/tablet).
5. Ensure perfect theme contrast with MkDocs slate (dark) and default (light) modes.

- [ ] **Step 4: Commit changes**

```bash
git add docs/assets/playground/playground.js docs/assets/playground/playground.css docs/playground.md
git commit --no-gpg-sign -m "feat(playground): implement split-pane syllabus sidebar and navigation UI"
```

---

### Task 4: Build Assets, Run Validation Tests, and Verify Parity

**Files:**
- Modify: `docs/assets/playground/playground-bundle.json`
- Modify: `site/assets/playground/playground-bundle.json`
- Modify: `tests/test_playground_bundle.py`

- [ ] **Step 1: Generate updated `playground-bundle.json`**

```bash
python scripts/build_playground_bundle.py -o docs/assets/playground/playground-bundle.json
```

- [ ] **Step 2: Run test suite to verify 100% integrity**

```bash
pytest tests/ -v
ruff check .
pyright
```

- [ ] **Step 3: Run MkDocs build verification**

```bash
mkdocs build --strict
```

- [ ] **Step 4: Commit generated assets and test updates**

```bash
git add docs/assets/playground/playground-bundle.json tests/test_playground_bundle.py
git commit --no-gpg-sign -m "chore(playground): build full 114-exercise playground bundle asset"
```

---

### Task 5: End-to-End Verification & Handoff

**Files:**
- Modify: `docs/playground.md`
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Update documentation in `docs/playground.md`**

Update `docs/playground.md` to showcase the full 114-exercise platform, progress persistence, keyboard shortcuts, and export/import features.

- [ ] **Step 2: Update `CHANGELOG.md`**

Add entry for full in-browser WebAssembly learning platform with state persistence under Unreleased.

- [ ] **Step 3: Final verification run**

```bash
pytest
ruff check .
mkdocs build --strict
```

- [ ] **Step 4: Final commit**

```bash
git add docs/playground.md CHANGELOG.md
git commit --no-gpg-sign -m "docs: document full 114-exercise browser learning platform"
```

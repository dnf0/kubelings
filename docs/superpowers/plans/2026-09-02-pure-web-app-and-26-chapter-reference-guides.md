# Pure Web Platform & 26-Chapter Kubernetes Reference Guides Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Choose an execution mode:
> 1. `superpowers:subagent-driven-development` (recommended for multi-agent reviews, backed by `SKILL.state` / `.agent-state/state.json`)
> 2. `agent-rules:stateful-execution` (SKILL.state) (recommended for deterministic single-agent linear execution)
> 3. `superpowers:executing-plans` (batch execution with manual checkpoints)
> Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transition Kubelings into a 100% client-side WebAssembly Kubernetes learning platform by streamlining legacy CLI runtime dependencies, adding URL deep-linking to the playground, and creating 26 in-depth Kubernetes concept reference guides.

**Architecture:** Prune CLI runner code from `src/kubelings/` while keeping the pure-Python schema validator and manifest registries. Add query-param exercise routing (`?exercise=<id>`) to the standalone Monaco/Pyodide playground. Build 26 structured reference markdown guides in `docs/guides/` with annotated YAML schemas, production best practices, and direct deep-link CTAs to the WebAssembly playground.

**Tech Stack:** Python 3.12, Pyodide v0.26 (Emscripten WebAssembly), PyYAML, Pydantic, Monaco Editor, MkDocs Material.

## Global Constraints

- Preserve all 26 chapters and 114 exercises in `exercises/` and `src/kubelings/validators/`.
- Ensure zero broken links or strict-mode warnings in `mkdocs build --strict`.
- Keep the Web Playground completely client-side without any server or backend dependencies.
- Every reference guide must include a direct CTA deep-linking into the playground exercise.

---

### Task 1: Codebase Pruning & Dependency Streamlining

**Files:**
- Modify: `pyproject.toml`
- Modify: `src/kubelings/__init__.py`
- Remove: `src/kubelings/cli.py`, `src/kubelings/runner.py`, `src/kubelings/watcher.py` (if present)
- Test: `tests/test_playground_bundle.py`

**Interfaces:**
- Retains: `src/kubelings/models.py`, `src/kubelings/validator.py`, `src/kubelings/validators/*.py`, `src/kubelings/manifest.py`.
- Produces: Clean, lightweight Python package focused on schema validation and static bundling.

- [ ] **Step 1: Update `pyproject.toml` dependencies**

Prune `typer`, `click`, `rich`, `watchfiles`, and `kubernetes` from `pyproject.toml` dependencies, keeping only `pyyaml`, `pydantic`, `jsonschema` for schema validation and standard dev tooling.

- [ ] **Step 2: Remove legacy CLI/terminal runner modules**

Remove obsolete CLI and terminal runner modules in `src/kubelings/` that are replaced by the browser WebAssembly runtime.

- [ ] **Step 3: Run pytest to verify package imports and bundling**

Run: `pytest tests/test_playground_bundle.py`
Expected: PASS (2 passed)

- [ ] **Step 4: Commit**

```bash
git add pyproject.toml src/kubelings/ tests/
git commit --no-gpg-sign -m "refactor: streamline package dependencies for pure web platform"
```

---

### Task 2: Web Playground Deep-Linking & Query Param Routing

**Files:**
- Modify: `docs/assets/playground/playground.js:200-240`
- Test: `tests/test_playground_bundle.py`

**Interfaces:**
- Consumes: `window.location.search` URL query parameters (`?exercise=<id>` and `?chapter=<num>`).
- Produces: Instant selection and auto-expansion of corresponding chapter and exercise on initial page load.

- [ ] **Step 1: Implement `applyUrlParams()` in `docs/assets/playground/playground.js`**

Add URL search parameter handling inside `initPlayground()`:
```javascript
function checkUrlParameters() {
  const params = new URLSearchParams(window.location.search);
  const targetExercise = params.get("exercise");
  const targetChapter = params.get("chapter");

  if (targetExercise && state.bundle.exercises[targetExercise]) {
    selectExercise(targetExercise);
    return;
  }

  if (targetChapter) {
    const chNum = parseInt(targetChapter, 10);
    const chapter = state.bundle.chapters.find((c) => c.number === chNum);
    if (chapter && chapter.exercise_ids.length > 0) {
      selectExercise(chapter.exercise_ids[0]);
    }
  }
}
```

- [ ] **Step 2: Call `checkUrlParameters()` after bundle load and render**

Ensure `checkUrlParameters()` is invoked after the sidebar tree is rendered and initial exercise is selected, updating browser history state cleanly.

- [ ] **Step 3: Test bundle & validation**

Run: `python3 scripts/build_playground_bundle.py && pytest tests/test_playground_bundle.py`
Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add docs/assets/playground/playground.js
git commit --no-gpg-sign -m "feat(playground): add URL query parameter deep linking for exercises and chapters"
```

---

### Task 3: Comprehensive 26-Chapter Kubernetes Reference Guides

**Files:**
- Create: `docs/guides/01-pods.md` through `docs/guides/26-hardware-acceleration-dra.md` (26 reference files)
- Modify: `docs/index.md` (Homepage featuring learning paths & reference guide directory)
- Modify: `mkdocs.yml` (Structured navigation hierarchy)

**Interfaces:**
- Produces: Complete, professional Kubernetes Reference Field Manual with annotated YAML schemas, architectural diagrams, best practice rules, and deep links to `https://dnf0.github.io/kubelings/playground/?chapter=XX`.

- [ ] **Step 1: Create Guides 01–06 (Core Workloads, Controllers, Config, Storage, Networking, Ingress)**
- [ ] **Step 2: Create Guides 07–13 (Scheduling, RBAC, Network Policies, Probes, Autoscaling, CRDs, Troubleshooting)**
- [ ] **Step 3: Create Guides 14–20 (GitOps, Service Mesh, Policy as Code, vCluster, Webhooks, Helm, Kustomize)**
- [ ] **Step 4: Create Guides 21–26 (Gateway API, Crossplane, Tetragon, KubeRay, Kueue/Volcano, DRA)**
- [ ] **Step 5: Update `docs/index.md` with flagship landing page and topic index**
- [ ] **Step 6: Update `mkdocs.yml` navigation tree**
- [ ] **Step 7: Test documentation build**

Run: `mkdocs build --strict`
Expected: PASS with 0 warnings.

- [ ] **Step 8: Commit**

```bash
git add docs/guides/ docs/index.md mkdocs.yml
git commit --no-gpg-sign -m "docs: add comprehensive 26-chapter Kubernetes reference guides and updated navigation"
```

---

### Task 4: End-to-End Verification & GitHub Pages Deployment

**Files:**
- Test: Full repository checks

- [ ] **Step 1: Run complete verification suite**

Run: `pytest tests/test_playground_bundle.py && ruff check . && mkdocs build --strict`
Expected: All tests pass, 0 lint errors, 0 build warnings.

- [ ] **Step 2: Push changes to `main`**

```bash
git pull --rebase origin main
git push origin main
```

- [ ] **Step 3: Verify deployment workflow**

Run: `gh run list --repo dnf0/kubelings -L 3`
Expected: `Deploy Documentation` completes with `success`.

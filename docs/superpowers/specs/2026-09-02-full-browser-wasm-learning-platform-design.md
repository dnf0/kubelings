# Full Browser WebAssembly (Pyodide) Learning Platform Design Specification

- **Date:** 2026-09-02
- **Status:** Approved
- **Target Release:** `v0.11.0`
- **Topic:** Full 114-Exercise In-Browser Learning Platform with State Persistence

---

## 1. Objective & Scope

Transform the Kubelings WebAssembly playground into a comprehensive, zero-install in-browser learning platform featuring:
1. **Full Curriculum Coverage**: All 114 exercises across all 26 chapters available in-browser.
2. **Client-Side State Persistence**: Complete progress, per-exercise working code, completion badges, and hint states stored locally via `localStorage` with zero backend server dependencies.
3. **Interactive Split-Pane Workspace**: LeetCode/Exercism-style interface with a collapsible chapter syllabus sidebar on the left and Monaco Editor + Terminal Diagnostics on the right.
4. **Data Portability**: Full JSON export and import of learner progress (`kubelings-progress.json`) for seamless backup and migration across browsers/devices.
5. **Deterministic Testing**: End-to-end bundle generation script and pytest verification ensuring parity with repository curriculum sources.

---

## 2. System Architecture & Component Interactions

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ Browser Application (docs/playground.md / site/playground/)                            │
│                                                                                        │
│  ┌───────────────────────────┬──────────────────────────────────────────────────────┐  │
│  │ 📚 Curriculum Sidebar     │ ☸ Code & Diagnostics Workspace                       │  │
│  │  • 26 Chapters            │  • Chapter & Exercise Title Header                   │  │
│  │  • 114 Exercises          │  • Monaco Editor (Auto-saved to localStorage)        │  │
│  │  • Status Badges & Search │  • Terminal Diagnostics (Pass/Fail, Timing, Errors)  │  │
│  │  • Overall Progress Bar   │  • Action Bar: [▶ Run] [💡 Hint] [↺ Reset] [🔍 Diff] │  │
│  └─────────────┬─────────────┴──────────────────────────┬───────────────────────────┘  │
│                │                                        │                              │
│                ▼                                        ▼                              │
│  ┌───────────────────────────┐            ┌─────────────────────────────────────────┐  │
│  │ LocalStorage State Engine │            │ Web Worker (Pyodide Wasm Runtime)       │  │
│  │  • KubelingsStorage       │            │  • In-memory Python 3.12 + PyYAML       │  │
│  │  • Per-exercise code      │◄───────────┤  • AST & Schema Validator               │  │
│  │  • Export / Import JSON   │            │  • Evaluates manifests in <15ms         │  │
│  └───────────────────────────┘            └─────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

### Component Roles:
1. **`build_playground_bundle.py`**:
   Extracts all 114 exercises, reference solutions, hints, chapter metadata, and in-memory test rules from `exercises/`, `solutions/`, and `src/kubelings/manifest.py`, writing `docs/assets/playground/playground-bundle.json`.
2. **`playground-worker.js`**:
   Web Worker running Pyodide v0.26+ WebAssembly runtime. Mounts the in-memory validation engine and validates user submissions asynchronously without blocking the UI thread.
3. **`playground.js` (`KubelingsUI` & `KubelingsStorage`)**:
   Controls Monaco Editor, syllabus tree navigation, text search filtering, debounced auto-saving, progress calculation, and diff views.
4. **`playground.css`**:
   Responsive split-view styles with CSS Grid/Flexbox, status indicators, and dark/light theme integration with MkDocs Material.

---

## 3. State Management Specification (`KubelingsStorage`)

State is persisted under the `localStorage` key `kubelings_learning_state_v1`.

### Data Schema:
```typescript
interface KubelingsSavedExercise {
  status: "not_started" | "in_progress" | "completed";
  userCode: string;           // Active working code
  hintsRevealed: number;       // Number of hints viewed (0..3)
  lastEvaluatedAt?: string;   // ISO 8601 timestamp
  passedAt?: string;          // ISO 8601 timestamp
}

interface KubelingsLearningState {
  version: 1;
  lastActiveExerciseId: string;
  exercises: Record<string, KubelingsSavedExercise>;
  stats: {
    completedCount: number;
    totalCount: number;
    completionPercentage: number;
  };
}
```

### Key Operations:
- **`loadExercise(id)`**: Retrieves saved code; if none exists, populates with starter template from bundle.
- **`saveExerciseCode(id, code)`**: Debounced auto-save (300ms) on Monaco Editor content change.
- **`markCompleted(id)`**: Updates status to `completed`, records `passedAt`, recalculates overall progress stats, and triggers badge updates in the sidebar.
- **`resetExercise(id)`**: Reverts `userCode` to the clean starter template from bundle and resets `hintsRevealed`.
- **`exportProgress()`**: Generates and downloads `kubelings-progress-<date>.json`.
- **`importProgress(jsonString)`**: Validates schema, merges or overwrites state, and refreshes the UI.
- **`resetAllProgress()`**: Clears storage key and re-initializes starter state after user confirmation.

---

## 4. User Interface & Layout Specification

### 4.1 Curriculum Sidebar (Left Pane)
- **Header**: Global progress bar (`X / 114 Exercises Completed • Y%`), Export JSON icon, Import JSON icon, and Reset Progress icon.
- **Search & Filter Bar**: Instant client-side search box filtering exercises by title, ID, chapter, or keyword (e.g. `HPA`, `RBAC`, `PVC`), plus status toggles (`All`, `Incomplete`, `Completed`).
- **Chapter Accordions**:
  - 26 collapsible chapters with chapter index, title, and completed count badge (e.g. `01. Pods & Manifests (4/4 ✓)`).
  - Exercise item rows displaying status icon (`○` Not Started, `⏳` In Progress, `✓` Completed), exercise name, and optional `Live Cluster` tag.
  - Active item highlight with automatic scroll-into-view.

### 4.2 Code & Diagnostics Workspace (Right Pane)
- **Top Bar**: Chapter title breadcrumb, exercise title, difficulty badge, and `← Prev` / `Next →` navigation.
- **Action Toolbar**:
  - `▶ Run Solution (Ctrl+Enter)`: Dispatches code to Pyodide worker.
  - `💡 Reveal Hint (H)`: Progressively unhides hint tiers in a collapsible panel.
  - `↺ Reset Code`: Restores exercise starter manifest.
  - `🔍 Compare Solution`: Switches Monaco to side-by-side Diff Editor.
- **Monaco Editor Container**:
  - Full-featured code editor with syntax highlighting for YAML and Python.
  - Automatic theme switching matching MkDocs (`vs-dark` in slate mode, `vs` in default mode).
- **Terminal Output Pane**:
  - ANSI-styled output box rendering green passes, red assertion errors with line highlights, and execution duration in milliseconds.
  - On pass, displays a celebration banner and an auto-advance button.

---

## 5. Offline Live-Cluster Fallback

For exercises requiring a live Kubernetes cluster (`requires_cluster: true` in manifest):
- In the Pyodide WebAssembly runtime, the manifest's YAML syntax and spec structure are thoroughly validated in-memory.
- An informational banner is displayed:
  > **ℹ️ Live Cluster Exercise**: Spec structure verified in-browser. To test live cluster reconciliation against `kind`/`minikube`, run `kubelings run <exercise>` via the CLI.

---

## 6. Verification & Test Plan

1. **Bundle Generator Test (`tests/test_playground_bundle.py`)**:
   - Verify `scripts/build_playground_bundle.py` bundles all 114 exercises across 26 chapters.
   - Assert all 114 exercises have non-empty starter code, reference solution, hints, and valid metadata.
   - Assert generated JSON structure adheres to bundle schema.
2. **In-Memory Validation Engine Parity**:
   - Run validator against all 114 reference solutions to guarantee 100% pass rate.
3. **State Engine Unit Tests**:
   - Test localStorage initialization, auto-save debounce, progress calculations, and export/import roundtrip integrity.
4. **Site Build & Asset Integrity**:
   - Run `mkdocs build --strict` to verify all assets and markdown pages compile without warnings or broken references.

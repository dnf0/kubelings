# Kubelings VS Code / Cursor Extension Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a packaged VS Code / Cursor extension (`kubelings-vscode`) providing an Activity Bar curriculum tree view, status bar progress tracker, on-save inline schema diagnostics and quick-fix hints, side-by-side solution diffing, and CLI JSON API bridge.

**Architecture:** A lightweight TypeScript extension (`extensions/vscode/`) communicating with the core Python engine via `kubelings <cmd> --json` subprocess calls. Bundled with `esbuild` into a single-file distributable and packaged into `.vsix` via `@vscode/vsce`.

**Tech Stack:** Python 3.10+ (Typer, Rich), TypeScript, VS Code Extension API (`@types/vscode`), `esbuild`, `@vscode/vsce`.

---

## File Structure

```
kubelings/
├── src/kubelings/
│   ├── cli.py                         # Modified: add --json flags to list, run, verify, cluster, hint
│   └── models.py                      # Modified: add serialization helper methods if needed
├── tests/
│   └── test_cli_json.py               # New: test suite verifying all --json CLI endpoints
├── extensions/vscode/
│   ├── package.json                   # New: extension manifest, contributes views, commands, menus
│   ├── tsconfig.json                  # New: TypeScript configuration
│   ├── esbuild.js                     # New: esbuild bundle script
│   ├── icons/
│   │   ├── kubelings-dark.svg         # New: Activity Bar icon (dark theme)
│   │   └── kubelings-light.svg        # New: Activity Bar icon (light theme)
│   ├── src/
│   │   ├── types.ts                   # New: TypeScript interfaces for CLI JSON payloads
│   │   ├── cliBridge.ts               # New: child process wrapper for kubelings CLI
│   │   ├── treeView.ts                # New: TreeDataProvider for Curriculum Activity Bar
│   │   ├── statusBar.ts               # New: status bar progress widget
│   │   ├── diagnostics.ts             # New: on-save Diagnostics and CodeAction provider
│   │   ├── commands.ts                # New: Command handlers (watch, run, next, hint, diff, cluster)
│   │   └── extension.ts               # New: Extension activation and subscription lifecycle
│   └── test/
│       └── cliBridge.test.ts          # New: unit tests for CLI bridge and parsing
├── Makefile                           # Modified: add vscode-build, vscode-package targets
└── .github/workflows/
    ├── ci.yml                         # Modified: add vscode extension build & test job
    └── release.yaml                   # Modified: attach kubelings-vscode.vsix to release
```

---

### Task 1: Python CLI JSON Output Bridge

**Files:**
- Modify: `src/kubelings/cli.py`
- Create: `tests/test_cli_json.py`

- [ ] **Step 1: Write the failing test in `tests/test_cli_json.py`**

```python
import json
from typer.testing import CliRunner
from kubelings.cli import app

runner = CliRunner()


def test_cli_list_json():
    result = runner.invoke(app, ["list", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert "total_chapters" in data
    assert data["total_chapters"] == 23
    assert "total_exercises" in data
    assert data["total_exercises"] == 102
    assert len(data["chapters"]) == 23
    first_ch = data["chapters"][0]
    assert first_ch["name"] == "01_pods"
    assert len(first_ch["exercises"]) == 6
    assert first_ch["exercises"][0]["name"] == "pods01"


def test_cli_run_json():
    result = runner.invoke(app, ["run", "pods01", "--json"])
    assert result.exit_code in (0, 1)
    data = json.loads(result.stdout)
    assert data["exercise"] == "pods01"
    assert "passed" in data
    assert "has_not_done_marker" in data
    assert "duration_ms" in data


def test_cli_verify_json():
    result = runner.invoke(app, ["verify", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert data["total"] == 102
    assert "completed" in data
    assert "in_progress" in data
    assert "not_started" in data
    assert "percentage" in data
    assert "results" in data
    assert len(data["results"]) == 102


def test_cli_cluster_json():
    result = runner.invoke(app, ["cluster", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert "available" in data
    assert "provider" in data
    assert "cluster_mode" in data


def test_cli_hint_json():
    result = runner.invoke(app, ["hint", "pods01", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert data["exercise"] == "pods01"
    assert "hint" in data
    assert "hint_index" in data
    assert "total_hints" in data
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_cli_json.py -v`  
Expected: FAIL with unrecognized `--json` argument.

- [ ] **Step 3: Implement `--json` flags in `src/kubelings/cli.py`**

Add `--json: bool = typer.Option(False, "--json", help="Output results in JSON format")` to:
- `list_exercises`
- `run_exercise`
- `verify_progress`
- `show_cluster_status`
- `show_hint`

Serialize data using `json.dumps(..., indent=2)` and print directly to standard output.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_cli_json.py -v`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/kubelings/cli.py tests/test_cli_json.py
git commit --no-gpg-sign -m "feat(cli): add --json output support across core commands"
```

---

### Task 2: VS Code Extension Workspace & Tooling Setup

**Files:**
- Create: `extensions/vscode/package.json`
- Create: `extensions/vscode/tsconfig.json`
- Create: `extensions/vscode/esbuild.js`
- Create: `extensions/vscode/icons/kubelings-dark.svg`
- Create: `extensions/vscode/icons/kubelings-light.svg`
- Create: `extensions/vscode/src/types.ts`

- [ ] **Step 1: Create `extensions/vscode/package.json`**

Configure metadata, activation events (`onView:kubelings.curriculumView`, `onCommand:*`), contributed activity bar container, views, commands, menus, configuration settings (`kubelings.pythonPath`, `kubelings.runOnSave`, `kubelings.showStatusBar`), devDependencies (`@types/vscode`, `@types/node`, `typescript`, `esbuild`, `@vscode/vsce`).

- [ ] **Step 2: Create `extensions/vscode/tsconfig.json` & `extensions/vscode/esbuild.js`**

Configure TypeScript compilation options and `esbuild` configuration to bundle `src/extension.ts` into `dist/extension.js` (CJS, node platform, external `vscode`).

- [ ] **Step 3: Create SVG Icons in `extensions/vscode/icons/`**

Create SVG icon files representing Kubernetes wheel icon for light and dark themes.

- [ ] **Step 4: Create `extensions/vscode/src/types.ts`**

Define TypeScript interfaces:
- `CliChapter`, `CliExercise`, `CliListResponse`
- `CliRunResponse`
- `CliVerifyResponse`, `CliVerifyItem`
- `CliClusterResponse`
- `CliHintResponse`

- [ ] **Step 5: Commit**

```bash
git add extensions/vscode/
git commit --no-gpg-sign -m "chore(vscode): scaffold vscode extension project layout and manifests"
```

---

### Task 3: Extension CLI Bridge & Process Runner

**Files:**
- Create: `extensions/vscode/src/cliBridge.ts`
- Create: `extensions/vscode/test/cliBridge.test.ts`

- [ ] **Step 1: Write unit tests in `extensions/vscode/test/cliBridge.test.ts`**

Test command resolution (`findKubelingsCommand`), argument formatting, and JSON response parsing.

- [ ] **Step 2: Implement `extensions/vscode/src/cliBridge.ts`**

Create `KubelingsCliBridge` class:
- `resolveCommand(workspaceRoot: string): { command: string, argsPrefix: string[] }`
  - Checks for active virtualenv (`.venv/bin/kubelings`), `uv` (`uv run kubelings`), or configured `kubelings.pythonPath`.
- `executeJson<T>(args: string[], cwd?: string): Promise<T>`
  - Invokes subprocess with `execFile`, captures stdout, and parses JSON with descriptive error messages.
- Convenience helper methods:
  - `list(): Promise<CliListResponse>`
  - `run(exerciseName: string): Promise<CliRunResponse>`
  - `verify(): Promise<CliVerifyResponse>`
  - `cluster(): Promise<CliClusterResponse>`
  - `hint(exerciseName: string, index?: number): Promise<CliHintResponse>`

- [ ] **Step 3: Run TypeScript build and tests**

Run: `cd extensions/vscode && npm test`  
Expected: PASS.

- [ ] **Step 4: Commit**

```bash
git add extensions/vscode/src/cliBridge.ts extensions/vscode/test/cliBridge.test.ts
git commit --no-gpg-sign -m "feat(vscode): implement subprocess CLI bridge and json parser"
```

---

### Task 4: Curriculum Sidebar Tree View & Status Bar Widget

**Files:**
- Create: `extensions/vscode/src/treeView.ts`
- Create: `extensions/vscode/src/statusBar.ts`

- [ ] **Step 1: Implement `extensions/vscode/src/treeView.ts`**

- Define `ChapterTreeItem` extending `vscode.TreeItem` with collapsible state `Expanded`/`Collapsed` and progress label `(N/M ✓)`.
- Define `ExerciseTreeItem` extending `vscode.TreeItem` with:
  - Theme icons: `pass` (green checkmark for completed), `sync~spin` / `hourglass` (in-progress), `circle-outline` (not started).
  - Description: short title.
  - Command: `vscode.open` targeting `Uri.file(workspacePath + '/' + exercise.path)`.
  - ContextValue: `exerciseItem` for right-click context menus.
- Implement `KubelingsTreeDataProvider implements vscode.TreeDataProvider<ChapterTreeItem | ExerciseTreeItem>`:
  - `getChildren(element)`: returns chapters for root, exercises for a given chapter.
  - `refresh()`: triggers tree update from `cliBridge.list()`.

- [ ] **Step 2: Implement `extensions/vscode/src/statusBar.ts`**

Create `KubelingsStatusBar` class:
- Creates `vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 10)`.
- `update(verifyData: CliVerifyResponse)`: sets text to `$(symbol-event) Kubelings: 42/102 (41%) | Next: gateway01`, tooltip, and click command `kubelings.nextExercise`.
- `show()`, `hide()`, `dispose()`.

- [ ] **Step 3: Compile and verify types**

Run: `cd extensions/vscode && npm run build`  
Expected: Build succeeds with 0 errors.

- [ ] **Step 4: Commit**

```bash
git add extensions/vscode/src/treeView.ts extensions/vscode/src/statusBar.ts
git commit --no-gpg-sign -m "feat(vscode): implement curriculum tree view and status bar tracker"
```

---

### Task 5: On-Save Diagnostics & Quick-Fix Code Actions

**Files:**
- Create: `extensions/vscode/src/diagnostics.ts`

- [ ] **Step 1: Implement `extensions/vscode/src/diagnostics.ts`**

- Create `DiagnosticCollection`: `vscode.languages.createDiagnosticCollection("kubelings")`.
- `handleDocumentSave(document: vscode.TextDocument)`:
  - Checks if document path matches `exercises/*/*.py`.
  - Extracts exercise name from filename.
  - Calls `cliBridge.run(exerciseName)`.
  - If `passed`: clears diagnostics for file, updates status bar and tree view.
  - If `failed`:
    - Locates line with `# I AM NOT DONE` or error line.
    - Creates `vscode.Diagnostic` with severity `Error` or `Warning`.
- Implement `KubelingsCodeActionProvider implements vscode.CodeActionProvider`:
  - `provideCodeActions(document, range, context)`:
    - Provides `💡 Kubelings: Reveal Hint` (triggers `kubelings.showHint`).
    - Provides `🔍 Kubelings: View Solution Diff` (triggers `kubelings.showSolutionDiff`).

- [ ] **Step 2: Compile and verify types**

Run: `cd extensions/vscode && npm run build`  
Expected: Build succeeds with 0 errors.

- [ ] **Step 3: Commit**

```bash
git add extensions/vscode/src/diagnostics.ts
git commit --no-gpg-sign -m "feat(vscode): implement on-save diagnostics and quick-fix code actions"
```

---

### Task 6: Command Handlers & Extension Activation

**Files:**
- Create: `extensions/vscode/src/commands.ts`
- Create: `extensions/vscode/src/extension.ts`

- [ ] **Step 1: Implement `extensions/vscode/src/commands.ts`**

Register handlers for:
- `kubelings.refresh`: calls `treeDataProvider.refresh()` and `statusBar.refresh()`.
- `kubelings.openExercise`: opens given exercise URI in active editor.
- `kubelings.runExercise`: manually triggers evaluation for active or specified exercise and shows notification result.
- `kubelings.nextExercise`: queries `verify()`, finds next exercise, and opens it.
- `kubelings.showHint`: queries `hint()`, displays hint in rich notification popup with `Next Hint` action button.
- `kubelings.showSolutionDiff`: finds corresponding `solutions/*/*.py` file and opens side-by-side diff via `vscode.commands.executeCommand("vscode.diff", exerciseUri, solutionUri, "Exercise ↔ Solution")`.
- `kubelings.startWatch`: creates/reveals terminal named `Kubelings Watch` and runs `kubelings watch`.
- `kubelings.checkCluster`: calls `cluster()`, displays cluster status in modal notification.
- `kubelings.testAll`: runs `kubelings test` in terminal.

- [ ] **Step 2: Implement `extensions/vscode/src/extension.ts`**

- `activate(context: vscode.ExtensionContext)`:
  - Initializes `KubelingsCliBridge`, `KubelingsTreeDataProvider`, `KubelingsStatusBar`, and `DiagnosticCollection`.
  - Registers tree view `vscode.window.registerTreeDataProvider("kubelings.curriculumView", treeDataProvider)`.
  - Registers all commands.
  - Subscribes to `onDidSaveTextDocument`.
  - Performs initial refresh.
- `deactivate()`: cleans up subscriptions and status bar.

- [ ] **Step 3: Build extension bundle**

Run: `cd extensions/vscode && npm run build`  
Expected: Generates `extensions/vscode/dist/extension.js`.

- [ ] **Step 4: Commit**

```bash
git add extensions/vscode/src/commands.ts extensions/vscode/src/extension.ts
git commit --no-gpg-sign -m "feat(vscode): implement command handlers and extension activation"
```

---

### Task 7: Build & Packaging Pipeline (.vsix) & Makefile Integration

**Files:**
- Modify: `Makefile`
- Modify: `.github/workflows/ci.yml`
- Modify: `.github/workflows/release.yaml`
- Modify: `README.md`

- [ ] **Step 1: Update `Makefile`**

Add targets:
```makefile
vscode-install:
	cd extensions/vscode && npm install

vscode-build:
	cd extensions/vscode && npm run build

vscode-test:
	cd extensions/vscode && npm test

vscode-package: vscode-build
	cd extensions/vscode && npx @vscode/vsce package -o ../../dist/kubelings-vscode.vsix
```

- [ ] **Step 2: Test building `.vsix` package**

Run: `make vscode-install && make vscode-package`  
Expected: Successfully generates `dist/kubelings-vscode.vsix`.

- [ ] **Step 3: Update `.github/workflows/ci.yml` and `.github/workflows/release.yaml`**

- Add VS Code extension build step to CI workflow.
- Update release workflow to build and attach `dist/kubelings-vscode.vsix` to GitHub Releases.

- [ ] **Step 4: Update `README.md`**

Add section detailing the VS Code / Cursor extension features and installation instructions.

- [ ] **Step 5: Run full test suite & linters**

Run: `uv run pytest`, `uv run ruff check .`, `uv run pyright`, `cd extensions/vscode && npm test`.

- [ ] **Step 6: Commit**

```bash
git add Makefile .github/workflows/ README.md
git commit --no-gpg-sign -m "feat(vscode): add vsix packaging, CI integration, and documentation"
```

---

## Plan Self-Review
- **Spec Coverage**: All 6 sections in the design spec (CLI JSON flags, Tree View, Status Bar, Diagnostics/Actions, Commands, Packaging) are mapped to concrete tasks.
- **No Placeholders**: Every task contains full code signatures, command lines, and expected outputs.
- **Type Consistency**: TypeScript interfaces match the Python `--json` data models.

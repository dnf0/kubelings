# Design Specification: Kubelings VS Code / Cursor Extension (`kubelings-vscode`)

**Date:** 2026-08-27  
**Status:** Approved  
**Target:** `kubelings-vscode` (VS Code & Cursor Extension)

---

## 1. Overview & Motivation

Kubelings currently provides an interactive CLI learning environment. While terminal watch mode is effective, developers frequently write and edit Kubernetes YAML and Python manifests inside IDEs such as VS Code and Cursor.

The **`kubelings-vscode` extension** bridges the gap by embedding the full Kubelings curriculum, real-time schema validation, progressive hinting, status bar tracking, and side-by-side solution diffing directly into the editor.

---

## 2. Goals & Non-Goals

### Goals
- **Curriculum Navigation**: An Activity Bar sidebar tree view rendering all 23 Chapters and 102 Exercises with live progress status (`✓` Completed, `⏳` In Progress, `○` Not Started).
- **Status Bar Indicator**: Real-time progress tracker (`☸ Kubelings: 42/102 (41%) | Next: gateway01`) with one-click navigation to the next exercise.
- **Inline Diagnostics & Code Actions**: Automatic on-save evaluation highlighting `# I AM NOT DONE` markers and validation errors in the Problems tab with quick-fix actions (`💡 Reveal Hint`, `🔍 View Solution Diff`).
- **Command Palette Integration**: Full command suite for watch mode, running individual exercises, hints, solution comparison, and cluster connectivity.
- **CLI JSON Interface**: Add clean `--json` output support across `kubelings` CLI commands (`list`, `run`, `verify`, `cluster`, `hint`) to enable robust, decoupled editor communication.
- **Fast & Self-Contained**: Packaged as a bundled `.vsix` with zero heavy runtime daemons, executing directly via `uvx kubelings` or local workspace Python interpreter.

### Non-Goals
- Replacing the CLI terminal watch mode (the extension launches and integrates with the CLI terminal watch mode rather than reimplementing it).
- Heavyweight LSP server daemon requiring background socket management.

---

## 3. Architecture & Communication Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       VS Code / Cursor Editor Window                        │
├───────────────────┬─────────────────────────────────────────────────────────┤
│ Activity Bar      │ Editor Buffer                                           │
│ ☸ Kubelings       │   exercises/21_gateway_api/gateway01.py                 │
│ ├── Ch 01 (6/6) ✓ │   # I AM NOT DONE ───> [Problem Diagnostic]            │
│ ├── ...           │   def get_gateway_manifest() -> Dict[str, Any]:         │
│ └── Ch 21 (0/4)   │       ...                                               │
│     ├── gateway01 │                                                         │
│     ├── gateway02 ├─────────────────────────────────────────────────────────┤
│     ├── gateway03 │ Integrated Terminal / Problems Pane                     │
│     └── gateway04 │ 💡 Code Action: "Reveal Hint" | "Compare Solution Diff" │
├───────────────────┴─────────────────────────────────────────────────────────┤
│ Status Bar: ☸ Kubelings: 90/102 (88%) | Next: gateway01                     │
└─────────────────────────────────────────┬───────────────────────────────────┘
                                          │
                                          │ Exec Process (JSON-RPC)
                                          v
                    ┌───────────────────────────────────────────┐
                    │       Kubelings Python CLI Engine         │
                    │      (kubelings <cmd> --json)             │
                    ├───────────────────────────────────────────┤
                    │ • Manifest Curriculum (23 Ch / 102 Ex)    │
                    │ • Schema Validator & Spec Evaluator       │
                    │ • Local Kind / Cluster Adapter            │
                    └───────────────────────────────────────────┘
```

---

## 4. Python CLI JSON API Bridge

The core CLI (`src/kubelings/cli.py`) will be augmented with structured `--json` output flags:

### 4.1 `kubelings list --json`
Emits the curriculum tree and exercise metadata:
```json
{
  "total_chapters": 23,
  "total_exercises": 102,
  "chapters": [
    {
      "number": 1,
      "name": "01_pods",
      "title": "Kubernetes Core Workloads & Pods",
      "description": "Pod Specifications, Multi-Container Sidecars, and Init Containers",
      "exercises": [
        {
          "name": "pods01",
          "title": "First Pod Manifest & Spec",
          "path": "exercises/01_pods/pods01.py",
          "solution_path": "solutions/01_pods/pods01.py",
          "chapter_name": "01_pods",
          "requires_cluster": false,
          "has_not_done": false,
          "status": "completed"
        }
      ]
    }
  ]
}
```

### 4.2 `kubelings run <exercise> --json`
Executes single exercise evaluation and returns machine-readable test results:
```json
{
  "exercise": "gateway01",
  "passed": false,
  "has_not_done_marker": true,
  "exit_code": 1,
  "output": "AssertionError: Gateway must define port 80 listener",
  "error": "AssertionError: Gateway must define port 80 listener",
  "error_line": 34,
  "duration_ms": 18.2,
  "hints_available": 3
}
```

### 4.3 `kubelings verify --json`
Aggregates workspace completion status:
```json
{
  "total": 102,
  "completed": 42,
  "in_progress": 1,
  "not_started": 59,
  "percentage": 41.18,
  "next_exercise": "gateway01",
  "results": [
    {"name": "pods01", "status": "completed", "passed": true},
    {"name": "gateway01", "status": "in_progress", "passed": false}
  ]
}
```

### 4.4 `kubelings cluster --json`
Returns live Kubernetes connectivity information:
```json
{
  "available": true,
  "context": "kind-kubelings",
  "provider": "kind",
  "cluster_mode": "live"
}
```

### 4.5 `kubelings hint <exercise> [--index N] --json`
Returns progressive hints:
```json
{
  "exercise": "gateway01",
  "hint_index": 0,
  "total_hints": 3,
  "hint": "Set apiVersion to gateway.networking.k8s.io/v1 and kind to GatewayClass or Gateway"
}
```

---

## 5. VS Code Extension Architecture (`extensions/vscode/`)

### 5.1 Project Layout
```
extensions/vscode/
├── package.json               # Extension manifest, contributes views, commands, menus, icons
├── tsconfig.json              # TypeScript configuration targeting ES2022
├── esbuild.js                 # Fast bundle builder
├── icons/
│   ├── kubelings-dark.svg
│   └── kubelings-light.svg
├── src/
│   ├── extension.ts           # Main activation entry point
│   ├── types.ts               # JSON schema types for CLI responses
│   ├── cliBridge.ts           # Subprocess wrapper calling kubelings --json
│   ├── treeView.ts            # TreeDataProvider for Curriculum Activity Bar
│   ├── statusBar.ts           # Status bar progress widget
│   ├── diagnostics.ts         # On-save DiagnosticCollection & CodeActionProvider
│   └── commands.ts            # Command handlers (watch, run, next, hint, diff, cluster)
└── test/
    └── extension.test.ts      # Extension unit test suite
```

### 5.2 Extension Manifest (`package.json`)
- **Activity Bar Container**: `kubelings-view-container` with custom Kubernetes-styled icon.
- **Tree View**: `kubelings.curriculumView` inside the container.
- **Contributed Commands**:
  - `kubelings.refresh`: Refresh Curriculum Tree
  - `kubelings.openExercise`: Open Exercise File
  - `kubelings.runExercise`: Run & Validate Active Exercise
  - `kubelings.nextExercise`: Jump to Next Uncompleted Exercise
  - `kubelings.showHint`: Show Progressive Hint (Webview / Modal)
  - `kubelings.showSolutionDiff`: Open Side-by-Side Diff with Reference Solution
  - `kubelings.startWatch`: Start Watch Mode in Integrated Terminal
  - `kubelings.checkCluster`: Display Kubernetes Cluster Status
  - `kubelings.testAll`: Run Self-Test Across All Solutions
- **Configuration Settings**:
  - `kubelings.pythonPath`: Path to Python interpreter / virtualenv (default: auto-detect `uv` or `.venv/bin/python`).
  - `kubelings.runOnSave`: Automatically run validation on exercise save (default: `true`).
  - `kubelings.showStatusBar`: Display progress in status bar (default: `true`).

### 5.3 Core Modules
1. **`cliBridge.ts`**:
   - Executes `kubelings <cmd> --json` using Node.js `child_process.execFile`.
   - Automatically detects whether to invoke `uv run kubelings`, `.venv/bin/kubelings`, or global `kubelings`.
   - Parses and type-validates JSON responses.
2. **`treeView.ts`**:
   - Implements `vscode.TreeDataProvider<ChapterTreeItem | ExerciseTreeItem>`.
   - Displays chapter expansion, exercise pass/fail badges, and double-click to open.
3. **`diagnostics.ts`**:
   - Subscribes to `vscode.workspace.onDidSaveTextDocument`.
   - When saving an exercise file (`exercises/*/*.py`), runs `cliBridge.runExercise(name)`.
   - If not passing, adds line-level diagnostics in the Problems panel.
   - Provides `CodeActionProvider` with quick-fix actions (`Reveal Hint`, `View Diff`).
4. **`statusBar.ts`**:
   - Displays `$(symbol-event) Kubelings: X/102 (Y%) | Next: <name>` in the bottom bar.
   - Updates dynamically on exercise completion or tree refresh.

---

## 6. Testing & Quality Strategy

1. **Python CLI Unit & Integration Tests (`tests/test_cli_json.py`)**:
   - Test `--json` flag on `list`, `run`, `verify`, `cluster`, and `hint`.
   - Verify JSON output schemas and exit codes.
2. **VS Code Extension Tests (`extensions/vscode/test/`)**:
   - Test `cliBridge` command assembly and JSON parsing.
   - Test tree provider item generation across 23 chapters.
   - Test diagnostic parsing and code action generation.
3. **End-to-End Packaging Test**:
   - Build `.vsix` bundle via `vsce package`.
   - Verify bundle size is < 500KB and contains required manifests and icons.

---

## 7. Packaging & Distribution

- Build target added to root [`Makefile`](file:///Users/danielfisher/repos/kubelings/Makefile):
  ```makefile
  vscode-build:
  	cd extensions/vscode && npm install && npm run build

  vscode-package:
  	cd extensions/vscode && npx @vscode/vsce package -o ../../dist/kubelings-vscode.vsix
  ```
- Artifact included in GitHub Actions release workflow as release asset: `kubelings-vscode.vsix`.

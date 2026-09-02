---
hide:
  - navigation
  - toc
---

# ☸️ Interactive WebAssembly Learning Platform

> **Zero installation, 100% client-side execution.** Practice and master Kubernetes manifests directly in your browser across the complete 114-exercise curriculum.

The **Kubelings WebAssembly Learning Platform** compiles Python 3.12, PyYAML, and the complete Kubelings AST and schema validation engine into WebAssembly via **[Pyodide](https://pyodide.org/)**. Everything runs entirely inside your browser tab using an isolated Web Worker—no remote servers, backend APIs, or local Docker/Kubernetes installations required.

---

<div id="kubelings-playground" class="kubelings-playground"></div>

<link rel="stylesheet" href="../assets/playground/playground.css" />
<script src="../assets/playground/playground.js"></script>

---

## 🚀 Platform Features & Navigation

### 📚 Complete 114-Exercise Curriculum
The left syllabus sidebar contains all **26 chapters and 114 exercises** from the official Kubelings curriculum. You can:
- Browse chapters using collapsible accordions.
- Instant-search across exercise names, titles, and concepts.
- Filter by completion status (**All**, **To Do**, **Done**).
- Track global progress with the top completion bar.

### 💾 Local Progress Persistence & Backup
All your working code, completed exercises, revealed hints, and timestamps are automatically saved in your browser via `localStorage` (debounced auto-save).
- **📥 Export Backup**: Download your entire progress state as a timestamped JSON file (`kubelings-progress-YYYY-MM-DD.json`).
- **📤 Import Backup**: Restore or transfer your progress across devices or browsers.
- **🗑️ Reset**: Reset individual exercises to the starter template, or wipe all progress to start fresh.

### ⌨️ Keyboard Shortcuts
- **`Ctrl+Enter`** / **`Cmd+Enter`**: Instantly execute validation against the current manifest.
- **`Alt+Left`** / **`Alt+Right`**: Navigate sequentially to previous or next exercise.
- **`Tab`** / **`Shift+Tab`**: Indent / outdent YAML blocks cleanly inside Monaco Editor.

### 💡 Progressive Hinting
Click **`💡 Reveal Hint`** to cycle through multi-tiered progressive clues. Hints provide conceptual guidance, syntax pointers, and spec references without giving away the full answer.

### 🔍 Reference Solution Comparison
Click **`🔍 Compare Solution`** to toggle an interactive side-by-side **Monaco Diff Editor**. Inspect exact additions, deletions, and structural differences between your working code and the official reference solution.

### ☸️ Live Cluster Exercises
Exercises marked with the **☸ Live Cluster** tag test schema rules and resource specs in-browser. To test live cluster reconciliation against `kind` or `minikube`, run `kubelings run <exercise>` in your CLI.

---

## 💻 CLI & IDE Integration

Prefer working locally in your terminal or editor? Run Kubelings with automated watch mode:

```bash
# Launch the interactive terminal onboarding tour
uvx kubelings tour

# Initialize exercises in your local directory and start watch mode
uvx kubelings init
uvx kubelings watch
```

Check out the [**Learner's Onboarding Guide**](onboarding-guide.md) or explore the [**Curriculum Syllabus**](syllabus.md).

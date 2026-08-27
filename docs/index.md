# Kubelings ☸️

**An interactive, hands-on CLI learning environment for Kubernetes.**

Inspired by [rustlings](https://github.com/rust-lang/rustlings) and [ziglings](https://codeberg.org/ziglings/exercises), **Kubelings** guides engineers through self-paced micro-exercises directly in the terminal.

---

## Why Kubelings?

Learning Kubernetes from static documentation or copy-pasted manifests often leads to frustration because error feedback is slow and cryptic. Kubelings provides:

- ⚡ **Sub-30ms Instant Feedback**: In-memory schema and spec validation without waiting on slow API servers.
- 🔁 **Active Problem Solving**: 102 real-world exercises across 23 chapters starting in a broken state that you fix and verify.
- ☸ **Dual-Mode Engine**: Practice 100% offline or connect to a real cluster (`kind`, `minikube`, `k3d`, or cloud).
- 💡 **Progressive Hinting**: Multi-tier clues when you get stuck without spoiling the answer.
- 🚀 **Zero-Install Run**: Start practicing immediately with `uvx kubelings init && uvx kubelings watch`.

---

## Quick Example

```python
# exercises/01_pods/pods01.py
# I AM NOT DONE

from typing import Any, Dict

def get_pod_manifest() -> Dict[str, Any]:
    # Fix the pod manifest specification
    return {
        "apiVersion": "v1",
        "kind": "Pod",
        "metadata": {"name": "nginx-web"},
        "spec": {
            "containers": [
                {"name": "nginx", "image": "nginx:alpine", "ports": [{"containerPort": 80}]}
            ]
        },
    }
```

Remove the `# I AM NOT DONE` marker, save the file, and watch the terminal UI advance to the next exercise automatically!

---

## VS Code & Cursor Extension 💻

Kubelings offers an official extension for **Visual Studio Code** and **Cursor** that transforms your editor into an interactive Kubernetes learning IDE.

### ✨ Extension Features

- 📚 **Activity Bar Curriculum Tree View**: Browse all 23 chapters and 102 exercises directly from the sidebar with real-time pass/fail status and chapter completion counters.
- 📊 **Status Bar Progress Indicator**: Persistent status bar item showing your total completion percentage, current progress, and next active exercise. Click to jump straight to the exercise.
- ⚡ **On-Save Diagnostics**: Automatic in-editor validation whenever you save an exercise manifest (`exercises/**/*.py`), surfacing schema errors, missing attributes, or remaining `# I AM NOT DONE` markers.
- 💡 **Code Actions & Quick Fixes**: Lightbulb quick fixes directly on errors:
  - **Reveal Hint**: Display progressive hints in the editor without spoiling the answer.
  - **Compare with Reference Solution**: Instantly open a side-by-side diff comparing your exercise code against the official reference solution.
- 🔍 **Solution Diffing**: Interactive diff viewer (`kubelings.showSolutionDiff`) for visual code comparison.
- 💻 **Integrated Terminal Watch Mode**: Launch `kubelings watch` into a dedicated integrated terminal with a single click.

### 📦 Installation Instructions

#### Command Line (VSIX)

```bash
# For VS Code
code --install-extension dist/kubelings-vscode.vsix

# For Cursor
cursor --install-extension dist/kubelings-vscode.vsix
```

#### Editor UI (VSIX)

1. Open the Extensions view (`Ctrl+Shift+X` / `Cmd+Shift+X`).
2. Click the **`...`** (Views and More Actions) menu in the top-right corner of the Extensions pane.
3. Select **Install from VSIX...** and choose `dist/kubelings-vscode.vsix`.


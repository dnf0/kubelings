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
- 🚀 **Zero-Install Run**: Start practicing immediately with `uvx kubelings tour`, `uvx kubelings init`, and `uvx kubelings watch`.
- 📖 **Complete Onboarding Guide**: Visual step-by-step tutorial available in the [**Learner's Onboarding Guide**](onboarding-guide.md).

---

## Quick Example

```python
# exercises/01_pods/pods01.py
"""
Exercise: exercises/01_pods/pods01.py
Topic: First Pod Manifest & Spec

Instructions:
Fix the YAML manifest below to define a valid Pod named 'nginx-web'
running nginx:alpine on container port 80 with label 'app: web'.
"""

import yaml
from kubelings.validator import validate_manifest

POD_MANIFEST = """
apiVersion: v1
kind: Pod
metadata:
  name: nginx-web
  labels:
    app: web
spec:
  containers:
  - name: nginx
    image: nginx:alpine
    ports:
    - containerPort: 80
"""
```

Save the file and watch the terminal UI immediately validate your solution. Press `n` or `Enter` to advance to the next exercise!

---

## VS Code & Cursor Extension 💻

Kubelings offers an official extension for **Visual Studio Code** and **Cursor** that transforms your editor into an interactive Kubernetes learning IDE.

### ✨ Extension Features

- 🗺️ **Interactive Welcome Walkthrough**: Built-in editor walkthrough (`Kubelings: Open Welcome Walkthrough`) guiding you through curriculum navigation, live cluster verification, and first exercise resolution.
- 📚 **Activity Bar Curriculum Tree View**: Browse all 23 chapters and 102 exercises directly from the sidebar with real-time pass/fail status and chapter completion counters.
- 📊 **Status Bar Progress Indicator**: Persistent status bar item showing your total completion percentage, current progress, and next active exercise. Click to jump straight to the exercise.
- ⚡ **On-Save Diagnostics**: Automatic in-editor validation whenever you save an exercise manifest (`exercises/**/*.py`), surfacing schema errors, missing attributes, or assertion failures.
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

---

## 🌐 The *lings Ecosystem

If you enjoy the hands-on, terminal-driven learning loop of **Kubelings**, explore the other interactive platforms in our `*lings` suite:

- 🏗️ [**Terralings**](https://github.com/dnf0/terralings) – Master Terraform and OpenTofu through interactive infrastructure-as-code exercises.
- 🇪🇸 [**Spanglings**](https://github.com/dnf0/spanglings) – Developer-grade CLI & interactive TUI for learning intermediate-to-advanced Spanish (B1–C1).
- ⚡ [**Raylings**](https://github.com/dnf0/raylings) – Learn distributed AI, Ray Core actors, and scalable clusters through hands-on Python exercises.

> *All projects in the `*lings` suite are deeply inspired by the pioneering terminal-based pedagogy of [Rustlings](https://github.com/rust-lang/rustlings) and [Ziglings](https://codeberg.org/ziglings/exercises).*


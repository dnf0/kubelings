# Kubelings for VS Code & Cursor ☸️

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](../../LICENSE)
[![VS Code](https://img.shields.io/badge/VS%20Code-1.85+-blue.svg)](https://code.visualstudio.com/)

**Kubelings for VS Code and Cursor** brings the interactive Kubernetes learning experience directly into your code editor. Learn Kubernetes hands-on through guided micro-exercises with real-time feedback, curriculum exploration, progressive hints, and side-by-side solution diffing.

---

## ✨ Features

### 1. 📚 Activity Bar Curriculum Tree View
- Dedicated Kubelings view container in the Activity Bar.
- Browse all **23 chapters and 102 exercises** with live status indicators:
  - 🟢 **Completed**: Solved exercises with a checkmark.
  - 🟡 **In Progress**: Currently active exercise under evaluation.
  - ⚪ **Not Started**: Remaining exercises in the syllabus.
- One-click exercise opening, running, and progressive hint reveal.

### 2. 📊 Status Bar Progress Indicator
- Compact status bar item displaying total progress (e.g., `$(check) Kubelings: 42/102 (41%) | Next: rbac01`).
- Click to jump directly to the current or next incomplete exercise.

### 3. ⚡ On-Save Diagnostics & Code Actions
- Automatic background validation when saving any exercise file (`exercises/**/*.py`).
- Inline error squiggles highlighting missing manifest fields, syntax errors, schema violations, or assertion failures.
- Contextual **Quick Fix Code Actions**:
  - 💡 **Reveal Hint**: Fetch and display progressive hints in the editor without spoiling the full answer.
  - 🔍 **Compare with Reference Solution**: Instantly open a side-by-side diff view comparing your manifest against the official solution.

### 4. 💻 Integrated Terminal Watch Mode
- Launch interactive `kubelings watch` in a dedicated integrated terminal with a single click (`kubelings.startWatch`).
- Supports all hotkeys: `n`/`Enter` (next), `p` (previous), `h` (hint), `r` (rerun), `l` (list), `q` (quit).

### 5. ☸ Cluster Connectivity & Solution Verifier
- Check connection status to live Kubernetes clusters (`kind`, `minikube`, `k3d`, or remote) with `kubelings.checkCluster`.
- Run validation across all reference solutions in an integrated terminal with `kubelings.testAll`.

---

## 🚀 Installation

### Option 1: Install from VSIX via Command Line

```bash
# For VS Code
code --install-extension dist/kubelings-vscode.vsix

# For Cursor
cursor --install-extension dist/kubelings-vscode.vsix
```

### Option 2: Install from VSIX via Editor UI

1. Open the Extensions view (`Ctrl+Shift+X` on Linux/Windows, `Cmd+Shift+X` on macOS).
2. Click the **`...`** (Views and More Actions) menu in the top-right corner of the Extensions pane.
3. Select **Install from VSIX...**.
4. Choose the `kubelings-vscode.vsix` file from the `dist/` directory or downloaded from GitHub Releases.

---

## ⚙️ Configuration

The extension automatically discovers Python virtual environments (`.venv`) and the `kubelings` CLI binary in your workspace. You can customize settings under `Settings > Extensions > Kubelings`:

| Setting | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `kubelings.pythonPath` | `string` | `""` | Custom path to Python interpreter or virtual environment executable (e.g. `.venv/bin/python`). |
| `kubelings.runOnSave` | `boolean` | `true` | Automatically run and validate exercise when saving an exercise file. |
| `kubelings.showStatusBar` | `boolean` | `true` | Display the Kubelings progress indicator in the status bar. |

---

## ⌨️ Commands

| Command | Title | Description |
| :--- | :--- | :--- |
| `kubelings.refresh` | **Kubelings: Refresh Curriculum** | Reload curriculum progress and update tree view & status bar. |
| `kubelings.runExercise` | **Kubelings: Run Current Exercise** | Execute validation for the active or selected exercise. |
| `kubelings.nextExercise` | **Kubelings: Open Next Exercise** | Find and open the next incomplete exercise file in editor. |
| `kubelings.showHint` | **Kubelings: Show Hint** | Fetch and display progressive hints for the active exercise. |
| `kubelings.showSolutionDiff` | **Kubelings: Compare with Reference Solution** | Open a side-by-side diff comparing current exercise with solution. |
| `kubelings.startWatch` | **Kubelings: Start Watch Mode in Terminal** | Launch interactive `kubelings watch` loop in terminal. |
| `kubelings.checkCluster` | **Kubelings: Check Cluster Connection** | Check offline vs live Kubernetes cluster connectivity. |
| `kubelings.testAll` | **Kubelings: Test All Reference Solutions** | Run test suite against all 102 curriculum solutions. |

---

## 🛠️ Development & Building

To build the extension from source:

```bash
# Install dependencies
npm install

# Compile and build extension bundle
npm run build

# Run test suite
npm test

# Package .vsix file
npm run package
```

---

## 📄 License

Apache-2.0. See [LICENSE](../../LICENSE) for details.

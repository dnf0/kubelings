# Diagnostics & Quick Fixes 💡

The Kubelings VS Code extension integrates deeply into the editor to provide a seamless learning feedback loop.

---

### 🛠️ In-Editor Feedback & Diagnostics

- **On-Save Inline Squiggles**:
  Whenever you save an exercise file (`exercises/**/*.py`), Kubelings automatically evaluates the exercise and highlights errors right at the exact failing line.

- **Quick Fix Lightbulb Actions**:
  Hover over an error squiggle or click the lightbulb icon `💡` (`Cmd+.` / `Ctrl+.`) to reveal instant actions:
  - **💡 Show Hint**: Opens progressive hints without giving away the entire answer.
  - **🔍 Compare with Reference Solution**: Opens a side-by-side diff between your workspace file and the official reference solution in `solutions/`.

---

### 🧪 Helpful Extension Actions

[Show Hint](command:kubelings.showHint)
[Compare with Reference Solution](command:kubelings.showSolutionDiff)

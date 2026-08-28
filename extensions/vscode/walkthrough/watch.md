# Interactive Watch Mode ⏱️

Kubelings features a high-performance terminal watcher that monitors your exercise files in real time.

---

### 🔄 The Inner Learning Loop

1. **Launch Watch Mode**: Start `kubelings watch` in a terminal.
2. **Open the Active Exercise**: The watcher points you to the current uncompleted exercise (e.g., `exercises/01_pods/pods01.yaml`).
3. **Edit & Save**: Fix the manifest syntax or schema requirements.
4. **Instant Verification**: On save, Kubelings re-evaluates the tests in `<30ms`. When green, remove the `# I AM NOT DONE` comment to advance!

---

### ⌨️ Interactive Watcher Hotkeys

When running inside the terminal watcher, use these interactive keybindings:

| Hotkey | Action | Description |
| :--- | :--- | :--- |
| `n` / `Enter` | **Next Exercise** | Advance to the next exercise when current passes |
| `p` | **Previous Exercise** | Navigate back to review earlier exercises |
| `h` | **Show Hint** | Reveal progressive multi-tier hints |
| `r` | **Rerun** | Force immediate re-evaluation |
| `l` | **Lint Manifest** | Perform deep structural validation |
| `q` | **Quit** | Exit the interactive file watcher |

---

[Start Watch Mode](command:kubelings.startWatch)

# Getting Started

> 📖 **Looking for a deep-dive walkthrough?** See the [**Complete Onboarding & Learner's Guide**](onboarding-guide.md) for an illustrated tutorial covering installation, the CLI tour, solving `pods01`, and VS Code setup.

## Quickstart (Zero-Install)

The fastest way to get started with Kubelings is using [`uvx`](https://docs.astral.sh/uv/):

```bash
# 1. Take the interactive 5-step onboarding tour
uvx kubelings tour

# 2. Initialize exercises in your current directory
uvx kubelings init

# 3. Launch the interactive watch engine
uvx kubelings watch
```

Alternatively with [`pipx`](https://pipx.pypa.io/stable/):

```bash
pipx install kubelings
kubelings tour
kubelings init
kubelings watch
```

---

## Local Development Installation

If you wish to contribute to Kubelings or inspect reference solutions:

```bash
# Clone the repository
git clone https://github.com/dnf0/kubelings.git
cd kubelings

# Create virtual environment and install in editable mode
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

---

## The Kubelings Workflow

1. Run `kubelings watch` in your terminal.
2. Open the reported file in your editor (e.g. `exercises/01_pods/pods01.yaml`).
3. Read the comments, specification instructions, and error diagnostic output in the terminal.
4. Edit the file to satisfy the Kubernetes manifest schema or validation logic.
5. Save the file. The watcher will evaluate your solution in `< 30ms` and display the green checkmark once all tests pass.
6. Press `n` or `Enter` in the terminal to advance to the next exercise!

### Keyboard Shortcuts in Watch Mode

While `kubelings watch` is running:

| Key | Action | Description |
| :--- | :--- | :--- |
| `n` / `Enter` | **Next** | Advance to the next incomplete or subsequent exercise. |
| `p` | **Previous** | Go back to review or modify the previous exercise. |
| `h` | **Hint** | Reveal the next progressive hint tier for the current exercise. |
| `r` | **Rerun** | Force re-evaluation of the current exercise. |
| `l` | **List** | Show curriculum syllabus overview. |
| `q` | **Quit** | Gracefully stop the watcher loop. |

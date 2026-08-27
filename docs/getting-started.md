# Getting Started

## Quickstart (Zero-Install)

The fastest way to use Kubelings is with [`uvx`](https://github.com/astral-sh/uv):

```bash
# 1. Initialize exercises in your current directory
uvx kubelings init

# 2. Launch the interactive watch engine
uvx kubelings watch
```

Alternatively with [`pipx`](https://pypa.github.io/pipx/):

```bash
pipx install kubelings
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
2. Open the reported file in your editor (e.g. `exercises/01_pods/pods01.py`).
3. Read the comments, specification instructions, and error diagnostic output in the terminal.
4. Edit the file to satisfy the Kubernetes manifest schema or validation logic.
5. Delete the `# I AM NOT DONE` marker at the top of the file and save.
6. The watcher will evaluate your solution in `< 30ms` and automatically transition to the next exercise.

### Keyboard Shortcuts in Watch Mode

While `kubelings watch` is running:

| Key | Action | Description |
| :--- | :--- | :--- |
| `h` | **Hint** | Reveal the next progressive hint tier for the current exercise. |
| `r` | **Rerun** | Force re-evaluation of the current exercise. |
| `l` | **List** | Show curriculum syllabus overview. |
| `q` | **Quit** | Gracefully stop the watcher loop. |

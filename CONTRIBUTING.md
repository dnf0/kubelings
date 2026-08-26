# Contributing to Kubelings ☸️

Thank you for your interest in contributing to **Kubelings**! We welcome bug fixes, documentation improvements, new exercises, and feature additions.

---

## Development Workflow

### 1. Prerequisites

- Python `>= 3.10`
- `git`
- [`uv`](https://github.com/astral-sh/uv) (recommended) or `pip`
- *Optional*: `kubectl` and a local cluster (`kind`, `minikube`, or `k3d`) for live cluster development

### 2. Local Setup

Fork and clone the repository:

```bash
git clone https://github.com/dnf0/kubelings.git
cd kubelings
```

Create a virtual environment and install dependencies with development extras:

#### Using `uv` (Recommended)

```bash
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

#### Using `pip`

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

---

## Project Structure

```
kubelings/
├── exercises/               # Broken/incomplete starter exercises grouped by chapter
│   ├── 01_pods/
│   └── ...
├── solutions/               # Passing reference solutions matching exercises 1-to-1
│   ├── 01_pods/
│   └── ...
├── src/
│   └── kubelings/           # Core library package
│       ├── cli.py           # Typer CLI application and commands
│       ├── cluster.py       # Live cluster detector and ephemeral namespace adapter
│       ├── manifest.py      # Curriculum chapter and exercise manifest
│       ├── models.py        # Domain dataclasses and enums
│       ├── runner.py        # Subprocess execution and evaluation engine
│       ├── ui.py            # Rich console formatting and diagnostics
│       ├── validator.py     # Offline Kubernetes OpenAPI and schema validator
│       └── watcher.py       # Watchdog filesystem event loop
├── tests/                   # Pytest test suite
│   ├── test_cli.py
│   ├── test_cluster.py
│   ├── test_manifest.py
│   ├── test_runner.py
│   ├── test_solutions_and_exercises.py  # Master E2E test suite
│   └── ...
├── Makefile                 # Common developer commands
└── pyproject.toml           # Packaging, dependencies, and tool configuration
```

---

## Authoring New Exercises

When adding a new exercise to the curriculum:

1. **Create the starter exercise in `exercises/<chapter_dir>/<exercise_name>.py`**:
   - The file must start with `# I AM NOT DONE` on line 1.
   - Include clear docstrings explaining the objective, Kubernetes concepts, and instructions.
   - Provide a template manifest or function with placeholder values (e.g. `None`, empty dicts, or intentionally invalid fields).
   - Implement a `verify()` function that executes validation checks and asserts correctness.
   - Ensure the starter exercise fails when run directly.

2. **Create the matching reference solution in `solutions/<chapter_dir>/<exercise_name>.py`**:
   - The solution must **NOT** contain `# I AM NOT DONE`.
   - The solution must pass 100% when run directly with `sys.executable`.
   - Output confirmation should include `"passed!"` or `"passed"`.

3. **Register the exercise in `src/kubelings/manifest.py`**:
   - Add the `Exercise` definition to the corresponding `Chapter` with at least 2 progressive hints.

4. **Verify Consistency**:
   - Run `pytest tests/test_solutions_and_exercises.py` to confirm that the new starter exercise fails, the reference solution passes, and there are no orphaned files.

---

## Quality Assurance & Verification

Before submitting changes or opening a pull request, ensure all checks pass:

```bash
# Run the complete test suite
make test
# or: pytest -v

# Run linter and code format checks
make lint
# or: ruff check . && ruff format --check .

# Run static type checking
make typecheck
# or: pyright

# Run all verification checks in one step
make verify
```

---

## Commit Guidelines

We enforce [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) across all branches.

Format: `<type>(<scope>): <short summary>`

Common types:
- `feat`: A new feature or curriculum exercise
- `fix`: A bug fix in the CLI, runner, validator, or curriculum
- `docs`: Documentation updates
- `refactor`: Code changes that neither fix a bug nor add a feature
- `test`: Adding or correcting tests
- `chore`: Tooling, dependencies, or configuration updates

Keep commits atomic: each commit should represent one logical change.

---

## Pull Request Process

1. Create a descriptive feature branch (`git checkout -b feat/my-improvement`).
2. Follow Test-Driven Development (TDD) where applicable.
3. Run `make verify` and confirm all tests, linters, and type checkers pass with 0 errors.
4. Commit your changes using conventional commit format.
5. Push your branch and open a Pull Request with context, testing evidence, and risk analysis.

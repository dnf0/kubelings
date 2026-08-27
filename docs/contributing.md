# Contributing to Kubelings

We welcome contributions of new exercises, bug fixes, performance improvements, and documentation polish!

---

## Local Development Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/dnf0/kubelings.git
   cd kubelings
   ```

2. **Create a virtual environment and install dev dependencies**:
   ```bash
   uv venv
   source .venv/bin/activate
   uv pip install -e ".[dev]"
   ```

3. **Install pre-commit hooks**:
   ```bash
   pre-commit install --hook-type commit-msg --hook-type pre-commit
   ```

---

## Running Tests

- **Run all unit & integration tests**:
  ```bash
  pytest
  ```

- **Run reference solution self-tests**:
  ```bash
  kubelings test
  ```

- **Lint and typecheck**:
  ```bash
  ruff check .
  ruff format --check .
  pyright
  ```

---

## Adding New Exercises

1. Create the starter exercise file under `exercises/<chapter_name>/<exercise_name>.py` with placeholders that fail validation initially.
2. Create the corresponding reference solution under `solutions/<chapter_name>/<exercise_name>.py`.
3. Register the exercise in `src/kubelings/manifest.py` with 2-3 progressive hints.
4. Add unit tests verifying both the broken starter state and working solution pass state.

---

## Conventional Commits

We follow the [Conventional Commits](https://www.conventionalcommits.org/) standard. Commit messages must start with:
- `feat:` for new features or exercises
- `fix:` for bug fixes
- `docs:` for documentation updates
- `test:` for test additions/modifications
- `chore:` for tooling or infrastructure changes

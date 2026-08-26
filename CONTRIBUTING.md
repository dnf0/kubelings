# Contributing to Kubelings

Thank you for your interest in contributing to **Kubelings**! We welcome bug fixes, documentation improvements, new exercises, and feature additions.

---

## Development Workflow

### 1. Prerequisites

- Python `>= 3.10`
- `git`
- `uv` (recommended) or `pip`

### 2. Setup

Fork and clone the repository:

```bash
git clone https://github.com/dnf0/kubelings.git
cd kubelings
```

Create a virtual environment and install dependencies in editable mode:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### 3. Verification Commands

Before opening a pull request, ensure all checks pass:

```bash
# Run tests
make test

# Run linters and formatting checks
make lint

# Run static type checking
make typecheck

# Or run everything at once:
make verify
```

---

## Commit Guidelines

We use [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) for all commit messages.

Format: `<type>(<scope>): <short summary>`

Common types:
- `feat`: A new feature or exercise
- `fix`: A bug fix in the CLI, validator, or curriculum
- `docs`: Documentation changes
- `refactor`: Code changes that neither fix a bug nor add a feature
- `test`: Adding or correcting tests
- `chore`: Tooling, configuration, or packaging updates

---

## Pull Request Process

1. Create a descriptive feature branch (`git checkout -b feat/my-new-exercise`).
2. Implement your changes following TDD (write failing tests first where appropriate).
3. Ensure all tests and linters pass (`make verify`).
4. Commit your changes using conventional commit format.
5. Push your branch and open a Pull Request with a clear description of the changes and testing evidence.

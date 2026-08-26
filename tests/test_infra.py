from pathlib import Path

import tomllib


def test_pyproject_structure():
    pyproject_path = Path("pyproject.toml")
    assert pyproject_path.exists()
    data = tomllib.loads(pyproject_path.read_text())
    assert data["project"]["name"] == "kubelings"
    assert "kubernetes" in data["project"]["dependencies"][0]
    assert "kubelings" in data["project"]["scripts"]


def test_required_files_exist():
    required = [
        "pyproject.toml",
        ".gitignore",
        "Makefile",
        "LICENSE",
        "README.md",
        "CONTRIBUTING.md",
        "CHANGELOG.md",
        ".github/workflows/ci.yml",
    ]
    for rel_path in required:
        p = Path(rel_path)
        assert p.exists(), f"Expected {rel_path} to exist"

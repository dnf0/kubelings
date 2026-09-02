"""Automated tests for WebAssembly playground bundle generation and content parity."""

import json
import subprocess
import sys
from pathlib import Path

# Add repo root to sys.path so scripts can be imported directly in unit tests
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from kubelings import __version__
from kubelings.manifest import get_manifest
from scripts.build_playground_bundle import build_bundle  # noqa: E402


def test_playground_bundle_generation(tmp_path: Path):
    bundle_script = REPO_ROOT / "scripts" / "build_playground_bundle.py"
    custom_output = tmp_path / "custom-bundle.json"

    # Run generator script with sys.executable and --output flag
    result = subprocess.run(
        [sys.executable, str(bundle_script), "--output", str(custom_output)],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )
    assert result.returncode == 0, f"Script failed with: {result.stderr}"
    assert custom_output.exists(), "custom-bundle.json was not created"

    data = json.loads(custom_output.read_text(encoding="utf-8"))
    assert data["version"] == __version__
    assert "validator_code" in data
    assert "models_code" in data
    assert "validators_modules" in data
    assert len(data["validators_modules"]) >= 26
    assert "chapters" in data
    assert "exercises" in data

    manifest = get_manifest()
    assert len(data["chapters"]) == len(manifest.chapters)
    assert len(data["exercises"]) == len(manifest.all_exercises)
    assert len(data["exercises"]) == 114
    assert len(data["chapters"]) == 26

    for chapter in data["chapters"]:
        assert "number" in chapter
        assert "name" in chapter
        assert "title" in chapter
        assert "description" in chapter
        assert "exercise_ids" in chapter
        assert len(chapter["exercise_ids"]) > 0

    for ex in manifest.all_exercises:
        assert ex.name in data["exercises"], f"Missing exercise {ex.name}"
        item = data["exercises"][ex.name]
        assert item["id"] == ex.name
        assert item["title"] == ex.title
        assert item["chapter"] == ex.chapter_name
        assert "starter_code" in item
        assert "solution_code" in item
        assert "hints" in item
        assert "requires_cluster" in item
        assert item["starter_code"].strip() != ""
        assert item["solution_code"].strip() != ""


def test_build_bundle_direct():
    bundle = build_bundle(REPO_ROOT)
    assert bundle["version"] == __version__
    assert len(bundle["chapters"]) == 26
    assert len(bundle["exercises"]) == 114
    assert "class ManifestValidationError" in bundle["validator_code"]
    assert "class Exercise" in bundle["models_code"]

    manifest = get_manifest()
    for ex in manifest.all_exercises:
        item = bundle["exercises"][ex.name]
        assert item["starter_code"].strip() != ""
        assert item["solution_code"].strip() != ""
        assert isinstance(item["hints"], list)

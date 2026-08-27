"""Automated tests for WebAssembly playground bundle generation and content parity."""

import json
import subprocess
import sys
from pathlib import Path

# Add repo root to sys.path so scripts can be imported directly in unit tests
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.build_playground_bundle import SHOWCASE_EXERCISE_IDS, build_bundle  # noqa: E402


def test_playground_bundle_generation():
    bundle_script = REPO_ROOT / "scripts" / "build_playground_bundle.py"
    bundle_path = REPO_ROOT / "docs" / "assets" / "playground" / "playground-bundle.json"

    # Run generator script
    result = subprocess.run(
        ["uv", "run", "python", str(bundle_script)],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )
    assert result.returncode == 0, f"Script failed with: {result.stderr}"
    assert bundle_path.exists(), "playground-bundle.json was not created"

    data = json.loads(bundle_path.read_text(encoding="utf-8"))
    assert "validator_code" in data
    assert "models_code" in data
    assert "exercises" in data

    # Verify 11 flagship showcase exercises
    expected_ids = [
        "pods01",
        "ctrl01",
        "config01",
        "storage01",
        "sched01",
        "netpol01",
        "autoscale01",
        "gitops01",
        "gateway01",
        "ray01",
        "accel02",
    ]
    assert expected_ids == SHOWCASE_EXERCISE_IDS

    for ex_id in expected_ids:
        assert ex_id in data["exercises"], f"Missing exercise {ex_id}"
        ex = data["exercises"][ex_id]
        assert "title" in ex
        assert "chapter" in ex
        assert "starter_code" in ex
        assert "solution_code" in ex
        assert "hints" in ex
        assert len(ex["hints"]) >= 2


def test_build_bundle_direct():
    bundle = build_bundle(REPO_ROOT)
    assert bundle["version"] == "0.7.0"
    assert len(bundle["exercises"]) == 11
    assert "class ManifestValidationError" in bundle["validator_code"]
    assert "class Exercise" in bundle["models_code"]

    for ex_id in SHOWCASE_EXERCISE_IDS:
        ex = bundle["exercises"][ex_id]
        assert ex["starter_code"].strip() != ""
        assert ex["solution_code"].strip() != ""
        assert len(ex["hints"]) >= 2

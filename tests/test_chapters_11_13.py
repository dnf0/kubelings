"""Tests for Chapters 11 to 13 Curriculum & Reference Solutions."""

import os
import subprocess
import sys
from pathlib import Path

import pytest

from kubelings.manifest import get_manifest
from kubelings.runner import NOT_DONE_MARKER

CHAPTER_DIRS = [
    "11_autoscaling",
    "12_crds_and_operators",
    "13_troubleshooting",
]
EXPECTED_EXERCISES = {
    "11_autoscaling": [f"autoscale0{i}.py" for i in range(1, 5)],
    "12_crds_and_operators": [f"crd0{i}.py" for i in range(1, 5)],
    "13_troubleshooting": [f"troubleshoot0{i}.py" for i in range(1, 6)],
}


def get_chapter_files(base_dir: str):
    """Collect all python files for chapters 11 to 13."""
    files = []
    base = Path(base_dir)
    for ch in CHAPTER_DIRS:
        ch_dir = base / ch
        for fname in EXPECTED_EXERCISES[ch]:
            files.append(ch_dir / fname)
    return files


ALL_EXERCISE_FILES = get_chapter_files("exercises")
ALL_SOLUTION_FILES = get_chapter_files("solutions")


def test_expected_file_count():
    """Verify total count of expected exercise and solution files is 13 each."""
    assert len(ALL_EXERCISE_FILES) == 13
    assert len(ALL_SOLUTION_FILES) == 13


@pytest.mark.parametrize("exercise_path", ALL_EXERCISE_FILES, ids=lambda p: p.name)
def test_exercise_files_exist_and_fail_initially(exercise_path: Path):
    """Verify every exercise file exists and fails initially."""
    assert exercise_path.exists(), f"Exercise file missing: {exercise_path}"

    # Running the exercise directly via subprocess should fail with non-zero exit code
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{Path.cwd() / 'src'}:{env.get('PYTHONPATH', '')}".strip(":")
    proc = subprocess.run(
        [sys.executable, str(exercise_path)],
        capture_output=True,
        text=True,
        timeout=10,
        env=env,
    )
    assert proc.returncode != 0, (
        f"Exercise {exercise_path} should fail initially, but returned exit code 0.\nOutput: {proc.stdout}\nError: {proc.stderr}"
    )


@pytest.mark.parametrize("solution_path", ALL_SOLUTION_FILES, ids=lambda p: p.name)
def test_solution_files_exist_and_pass(solution_path: Path):
    """Verify every reference solution exists, has NOT_DONE removed, and passes."""
    assert solution_path.exists(), f"Solution file missing: {solution_path}"
    content = solution_path.read_text(encoding="utf-8")
    assert NOT_DONE_MARKER not in content, (
        f"Solution {solution_path} must not contain '{NOT_DONE_MARKER}'"
    )

    # Running the solution directly via subprocess must pass with exit code 0
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{Path.cwd() / 'src'}:{env.get('PYTHONPATH', '')}".strip(":")
    proc = subprocess.run(
        [sys.executable, str(solution_path)],
        capture_output=True,
        text=True,
        timeout=10,
        env=env,
    )
    assert proc.returncode == 0, (
        f"Solution {solution_path} failed with exit code {proc.returncode}.\nOutput: {proc.stdout}\nError: {proc.stderr}"
    )
    assert "passed!" in proc.stdout, f"Solution {solution_path} did not print pass confirmation"


def test_manifest_matches_chapters_11_to_13_files():
    """Verify manifest definitions match exercise files on disk."""
    manifest = get_manifest()

    for ch in manifest.chapters[10:13]:
        assert ch.name in CHAPTER_DIRS
        for ex in ch.exercises:
            assert ex.file_path.exists(), f"Manifest exercise file missing: {ex.path}"
            assert ex.solution_path.exists(), f"Manifest solution file missing: {ex.solution_path}"

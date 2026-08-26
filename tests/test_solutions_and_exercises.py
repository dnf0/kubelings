"""End-to-end test suite verifying all curriculum exercises and reference solutions."""

import os
import subprocess
import sys
from pathlib import Path

import pytest

from kubelings.manifest import get_manifest
from kubelings.models import Exercise
from kubelings.runner import NOT_DONE_MARKER

manifest = get_manifest()


@pytest.mark.parametrize("exercise", manifest.all_exercises, ids=lambda ex: ex.name)
def test_all_reference_solutions_pass(exercise: Exercise):
    """Verify that every reference solution exists, does not have NOT_DONE, and passes."""
    sol_path = exercise.solution_path
    assert sol_path.exists(), f"Missing solution for {exercise.name} at {sol_path}"

    content = sol_path.read_text(encoding="utf-8")
    assert NOT_DONE_MARKER not in content, (
        f"Solution {sol_path} must not contain '{NOT_DONE_MARKER}'"
    )

    env = os.environ.copy()
    env["PYTHONPATH"] = f"{Path.cwd() / 'src'}:{env.get('PYTHONPATH', '')}".strip(":")

    proc = subprocess.run(
        [sys.executable, str(sol_path)],
        capture_output=True,
        text=True,
        timeout=30,
        env=env,
    )
    assert proc.returncode == 0, (
        f"Solution {sol_path} failed with exit code {proc.returncode}.\n"
        f"STDOUT:\n{proc.stdout}\n"
        f"STDERR:\n{proc.stderr}"
    )
    assert "passed" in proc.stdout.lower(), (
        f"Solution {sol_path} did not output expected pass confirmation.\nSTDOUT:\n{proc.stdout}"
    )


@pytest.mark.parametrize("exercise", manifest.all_exercises, ids=lambda ex: ex.name)
def test_starter_exercises_fail(exercise: Exercise):
    """Verify that every starter exercise exists, contains NOT_DONE, and fails when run."""
    ex_path = exercise.file_path
    assert ex_path.exists(), f"Missing exercise file for {exercise.name} at {ex_path}"

    content = ex_path.read_text(encoding="utf-8")
    assert NOT_DONE_MARKER in content, (
        f"Starter exercise {ex_path} must contain '{NOT_DONE_MARKER}'"
    )

    env = os.environ.copy()
    env["PYTHONPATH"] = f"{Path.cwd() / 'src'}:{env.get('PYTHONPATH', '')}".strip(":")

    proc = subprocess.run(
        [sys.executable, str(ex_path)],
        capture_output=True,
        text=True,
        timeout=30,
        env=env,
    )
    assert proc.returncode != 0, (
        f"Starter exercise {ex_path} was expected to fail, but exited with code 0.\n"
        f"STDOUT:\n{proc.stdout}\n"
        f"STDERR:\n{proc.stderr}"
    )


def test_manifest_and_disk_files_consistency():
    """Verify there are no orphaned files in exercises/ or solutions/ and all manifest items exist."""
    manifest_exercises = {ex.path for ex in manifest.all_exercises}
    manifest_solutions = {str(ex.solution_path) for ex in manifest.all_exercises}

    disk_exercises = {str(p) for p in Path("exercises").glob("*/*.py")}
    disk_solutions = {str(p) for p in Path("solutions").glob("*/*.py")}

    # Check total counts
    assert len(manifest_exercises) == 62
    assert len(disk_exercises) == 62
    assert len(disk_solutions) == 62

    # Check for missing or orphaned exercise files
    missing_exercises = manifest_exercises - disk_exercises
    orphaned_exercises = disk_exercises - manifest_exercises
    assert not missing_exercises, f"Exercises in manifest but missing on disk: {missing_exercises}"
    assert not orphaned_exercises, f"Exercises on disk but not in manifest: {orphaned_exercises}"

    # Check for missing or orphaned solution files
    missing_solutions = manifest_solutions - disk_solutions
    orphaned_solutions = disk_solutions - manifest_solutions
    assert not missing_solutions, f"Solutions in manifest but missing on disk: {missing_solutions}"
    assert not orphaned_solutions, f"Solutions on disk but not in manifest: {orphaned_solutions}"

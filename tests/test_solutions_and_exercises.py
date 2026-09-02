"""End-to-end test suite verifying all curriculum exercises and reference solutions."""

from pathlib import Path

import pytest

from kubelings.manifest import build_manifest
from kubelings.models import Exercise
from kubelings.runner import ExerciseRunner
from kubelings.validators import load_all_validators

load_all_validators()
manifest = build_manifest()


@pytest.fixture(scope="module")
def runner() -> ExerciseRunner:
    return ExerciseRunner()


@pytest.mark.parametrize("exercise", manifest.all_exercises, ids=lambda ex: ex.name)
def test_all_reference_solutions_pass(runner: ExerciseRunner, exercise: Exercise):
    """Verify that every reference solution exists and passes."""
    sol_ex = Exercise(
        name=exercise.name,
        title=exercise.title,
        path=f"solutions/{exercise.chapter_name}/{exercise.name}.yaml",
        chapter_name=exercise.chapter_name,
    )
    result = runner.run_exercise(sol_ex)
    assert result.passed, (
        f"Solution {exercise.name} failed validation.\n"
        f"Error: {result.error}\n"
        f"Output: {result.output}"
    )


@pytest.mark.parametrize("exercise", manifest.all_exercises, ids=lambda ex: ex.name)
def test_starter_exercises_fail(runner: ExerciseRunner, exercise: Exercise):
    """Verify that every starter exercise exists and fails when run initially."""
    starter_ex = Exercise(
        name=exercise.name,
        title=exercise.title,
        path=f"exercises/{exercise.chapter_name}/{exercise.name}.yaml",
        chapter_name=exercise.chapter_name,
    )
    result = runner.run_exercise(starter_ex)
    assert not result.passed, f"Starter exercise {exercise.name} was expected to fail, but passed."


def test_manifest_and_disk_files_consistency():
    """Verify there are no orphaned files in exercises/ or solutions/ and all manifest items exist."""
    manifest_exercises = {ex.path for ex in manifest.all_exercises}
    manifest_solutions = {
        f"solutions/{ex.chapter_name}/{ex.name}.yaml" for ex in manifest.all_exercises
    }

    disk_exercises = {str(p) for p in Path("exercises").glob("*/*.yaml")}
    disk_solutions = {str(p) for p in Path("solutions").glob("*/*.yaml")}

    # Check total counts
    assert len(manifest_exercises) == 126
    assert len(disk_exercises) == 126
    assert len(disk_solutions) == 126

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

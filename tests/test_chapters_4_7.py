"""Tests for Chapters 4 to 7 Curriculum & Reference Solutions."""

from pathlib import Path

import pytest

from kubelings.manifest import get_manifest
from kubelings.models import Exercise
from kubelings.runner import NOT_DONE_MARKER, ExerciseRunner
from kubelings.validators import load_all_validators

load_all_validators()

CHAPTER_DIRS = [
    "04_storage",
    "05_services_networking",
    "06_ingress_gateway",
    "07_scheduling",
]
EXPECTED_EXERCISES = {
    "04_storage": [f"storage0{i}.yaml" for i in range(1, 6)],
    "05_services_networking": [f"net0{i}.yaml" for i in range(1, 6)],
    "06_ingress_gateway": [f"ingress0{i}.yaml" for i in range(1, 5)],
    "07_scheduling": [f"sched0{i}.yaml" for i in range(1, 6)],
}


def get_chapter_files(base_dir: str):
    """Collect all YAML files for chapters 4 to 7."""
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
    """Verify total count of expected exercise and solution files is 19 each."""
    assert len(ALL_EXERCISE_FILES) == 19
    assert len(ALL_SOLUTION_FILES) == 19


@pytest.mark.parametrize("exercise_path", ALL_EXERCISE_FILES, ids=lambda p: p.name)
def test_exercise_files_exist_and_fail_initially(exercise_path: Path):
    """Verify every exercise file exists and fails initially."""
    assert exercise_path.exists(), f"Exercise file missing: {exercise_path}"
    name = exercise_path.stem
    chapter_name = exercise_path.parent.name
    ex = Exercise(name=name, title=name, path=str(exercise_path), chapter_name=chapter_name)
    runner = ExerciseRunner()
    result = runner.run_exercise(ex)
    assert not result.passed, f"Exercise {exercise_path} should fail initially, but passed."


@pytest.mark.parametrize("solution_path", ALL_SOLUTION_FILES, ids=lambda p: p.name)
def test_solution_files_exist_and_pass(solution_path: Path):
    """Verify every reference solution exists, has NOT_DONE removed, and passes."""
    assert solution_path.exists(), f"Solution file missing: {solution_path}"
    content = solution_path.read_text(encoding="utf-8")
    assert NOT_DONE_MARKER not in content, (
        f"Solution {solution_path} must not contain '{NOT_DONE_MARKER}'"
    )
    name = solution_path.stem
    chapter_name = solution_path.parent.name
    ex = Exercise(name=name, title=name, path=str(solution_path), chapter_name=chapter_name)
    runner = ExerciseRunner()
    result = runner.run_exercise(ex)
    assert result.passed, (
        f"Solution {solution_path} failed validation.\nError: {result.error}\nOutput: {result.output}"
    )


def test_manifest_matches_chapters_4_to_7_files():
    """Verify manifest definitions match exercise files on disk."""
    manifest = get_manifest()

    for ch in manifest.chapters[3:7]:
        assert ch.name in CHAPTER_DIRS
        for ex in ch.exercises:
            assert ex.file_path.exists(), f"Manifest exercise file missing: {ex.path}"
            assert ex.solution_path.exists(), f"Manifest solution file missing: {ex.solution_path}"

"""
End-to-End Verification Test for All 114 Converted YAML Exercises & Validators.
"""

from pathlib import Path

import pytest

from kubelings.manifest import build_manifest
from kubelings.models import Exercise
from kubelings.runner import ExerciseRunner
from kubelings.validators import get_validator, load_all_validators

# Ensure all 26 chapter validators are loaded into registry
load_all_validators()

manifest_model = build_manifest()
all_exercises = manifest_model.all_exercises


@pytest.fixture(scope="module")
def runner() -> ExerciseRunner:
    return ExerciseRunner()


def test_manifest_contains_all_114_exercises():
    assert len(all_exercises) == 114
    assert len(manifest_model.chapters) == 26


@pytest.mark.parametrize("ex", all_exercises, ids=lambda e: e.name)
def test_exercise_files_exist(ex):
    repo_root = Path(__file__).resolve().parent.parent
    # Check that .yaml files exist
    ex_yaml_path = repo_root / "exercises" / ex.chapter_name / f"{ex.name}.yaml"
    sol_yaml_path = repo_root / "solutions" / ex.chapter_name / f"{ex.name}.yaml"

    assert ex_yaml_path.is_file(), f"Exercise YAML missing: {ex_yaml_path}"
    assert sol_yaml_path.is_file(), f"Solution YAML missing: {sol_yaml_path}"

    # Check that old .py files do not exist
    old_ex_py = repo_root / "exercises" / ex.chapter_name / f"{ex.name}.py"
    old_sol_py = repo_root / "solutions" / ex.chapter_name / f"{ex.name}.py"
    assert not old_ex_py.exists(), f"Old exercise Python file still exists: {old_ex_py}"
    assert not old_sol_py.exists(), f"Old solution Python file still exists: {old_sol_py}"


@pytest.mark.parametrize("ex", all_exercises, ids=lambda e: e.name)
def test_validator_registered(ex):
    validator = get_validator(ex.name)
    assert validator is not None, f"No validator registered for {ex.name}"
    assert callable(validator)


@pytest.mark.parametrize("ex", all_exercises, ids=lambda e: e.name)
def test_starter_exercise_is_incomplete(runner, ex):
    starter_ex = Exercise(
        name=ex.name,
        title=ex.title,
        path=f"exercises/{ex.chapter_name}/{ex.name}.yaml",
        chapter_name=ex.chapter_name,
    )
    result = runner.run_exercise(starter_ex)
    assert not result.passed, (
        f"Starter exercise {ex.name} unexpectedly passed without student edits!"
    )


@pytest.mark.parametrize("ex", all_exercises, ids=lambda e: e.name)
def test_solution_exercise_passes_validation(runner, ex):
    sol_ex = Exercise(
        name=ex.name,
        title=ex.title,
        path=f"solutions/{ex.chapter_name}/{ex.name}.yaml",
        chapter_name=ex.chapter_name,
    )
    result = runner.run_exercise(sol_ex)
    assert result.passed, (
        f"Solution for {ex.name} failed validation:\nError: {result.error}\nOutput: {result.output}"
    )
    assert result.error is None

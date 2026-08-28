"""Tests for native YAML runner and validator registry."""

from pathlib import Path

import pytest
import yaml

from kubelings.models import Exercise
from kubelings.runner import ExerciseRunner, format_yaml_error
from kubelings.validators import (
    get_validator,
    load_all_validators,
    register_validator,
)


def test_validator_registration() -> None:
    @register_validator("test_ex01")
    def sample_val(manifest, raw_text):
        assert manifest.get("kind") == "Pod", "Kind must be Pod"

    fn = get_validator("test_ex01")
    assert fn is not None
    with pytest.raises(AssertionError, match="Kind must be Pod"):
        fn({"kind": "Service"}, "")


def test_runner_executes_yaml_exercise(tmp_path: Path) -> None:
    ex_file = tmp_path / "test_pod.yaml"
    ex_file.write_text(
        "apiVersion: v1\nkind: Pod\nmetadata:\n  name: my-pod\n",
        encoding="utf-8",
    )

    @register_validator("test_pod")
    def validate_test_pod(manifest, raw):
        assert manifest["metadata"]["name"] == "my-pod"

    exercise = Exercise(
        name="test_pod",
        title="Test Pod",
        path=str(ex_file),
        chapter_name="01_pods",
    )

    runner = ExerciseRunner()
    result = runner.run_exercise(exercise)
    assert result.passed is True
    assert "✓ test_pod passed!" in result.output
    assert result.error is None
    assert result.exit_code == 0


def test_runner_catches_yaml_syntax_error_cleanly(tmp_path: Path) -> None:
    bad_yaml = tmp_path / "bad.yaml"
    bad_yaml.write_text("metadata:\n  app: app: web\n", encoding="utf-8")

    exercise = Exercise(
        name="bad_ex",
        title="Bad YAML",
        path=str(bad_yaml),
        chapter_name="01_pods",
    )

    runner = ExerciseRunner()
    result = runner.run_exercise(exercise)
    assert result.passed is False
    assert result.error is not None
    assert "YAML Syntax Error" in result.error
    assert "line 2" in result.error.lower()


def test_format_yaml_error_direct() -> None:
    bad_yaml = "metadata:\n  app: app: web\n"
    with pytest.raises(yaml.YAMLError) as excinfo:
        list(yaml.safe_load_all(bad_yaml))
    formatted = format_yaml_error(excinfo.value, Path("bad.yaml"))
    assert "❌ YAML Syntax Error in bad.yaml:" in formatted
    assert "Line 2, Column 11: mapping values are not allowed here" in formatted
    assert ">       app: app: web" in formatted
    assert "^" in formatted


def test_format_yaml_error_without_mark() -> None:
    generic_err = yaml.YAMLError("custom yaml error")
    formatted = format_yaml_error(generic_err, Path("bad.yaml"))
    assert "❌ YAML Syntax Error in bad.yaml:" in formatted
    assert "custom yaml error" in formatted


@pytest.mark.parametrize(
    "marker",
    ["???", "TODO", "FIXME", "I AM NOT DONE", "___", "/* ??? */", "<!-- ANSWER -->"],
)
def test_runner_incomplete_marker_handling(tmp_path: Path, marker: str) -> None:
    incomplete_file = tmp_path / f"incomplete_{hash(marker)}.yaml"
    incomplete_file.write_text(
        f"apiVersion: v1\nkind: Pod\nmetadata:\n  name: {marker}\n",
        encoding="utf-8",
    )

    exercise = Exercise(
        name="incomplete_ex",
        title="Incomplete Exercise",
        path=str(incomplete_file),
        chapter_name="01_pods",
    )

    runner = ExerciseRunner()
    result = runner.run_exercise(exercise)
    assert result.passed is False
    assert result.has_not_done_marker is True
    assert result.exit_code == 1
    assert "Exercise still contains incomplete markers" in result.output


def test_runner_multi_doc_yaml(tmp_path: Path) -> None:
    multi_doc_file = tmp_path / "multi_doc.yaml"
    multi_doc_file.write_text(
        "apiVersion: v1\n"
        "kind: Service\n"
        "metadata:\n"
        "  name: test-svc\n"
        "---\n"
        "apiVersion: apps/v1\n"
        "kind: Deployment\n"
        "metadata:\n"
        "  name: test-deploy\n",
        encoding="utf-8",
    )

    @register_validator("test_multi_doc")
    def validate_multi_doc(manifests, raw):
        assert isinstance(manifests, list)
        assert len(manifests) == 2
        assert manifests[0]["kind"] == "Service"
        assert manifests[1]["kind"] == "Deployment"

    exercise = Exercise(
        name="test_multi_doc",
        title="Multi Doc Exercise",
        path=str(multi_doc_file),
        chapter_name="02_multi",
    )

    runner = ExerciseRunner()
    result = runner.run_exercise(exercise)
    assert result.passed is True
    assert "✓ test_multi_doc passed!" in result.output


def test_runner_yaml_validation_failure(tmp_path: Path) -> None:
    ex_file = tmp_path / "fail_pod.yaml"
    ex_file.write_text(
        "apiVersion: v1\nkind: Pod\nmetadata:\n  name: wrong-name\n",
        encoding="utf-8",
    )

    @register_validator("fail_pod")
    def validate_fail_pod(manifest, raw):
        assert manifest["metadata"]["name"] == "correct-name", "Pod name must be correct-name"

    exercise = Exercise(
        name="fail_pod",
        title="Fail Pod",
        path=str(ex_file),
        chapter_name="01_pods",
    )

    runner = ExerciseRunner()
    result = runner.run_exercise(exercise)
    assert result.passed is False
    assert result.error is not None
    assert "❌ Validation Failed: Pod name must be correct-name" in result.error


def test_runner_yaml_no_validator_registered(tmp_path: Path) -> None:
    ex_file = tmp_path / "no_val.yaml"
    ex_file.write_text(
        "apiVersion: v1\nkind: Pod\nmetadata:\n  name: pod\n",
        encoding="utf-8",
    )

    exercise = Exercise(
        name="unregistered_ex_xyz",
        title="Unregistered",
        path=str(ex_file),
        chapter_name="01_pods",
    )

    runner = ExerciseRunner()
    result = runner.run_exercise(exercise)
    assert result.passed is False
    assert result.error is not None
    assert "No validator registered for exercise 'unregistered_ex_xyz'" in result.error


def test_load_all_validators_runs_safely() -> None:
    # Should run without error even if no validators or some validators exist
    load_all_validators()

"""Tests for Kubelings ExerciseRunner and UI rendering helpers."""

import sys
from pathlib import Path

from rich.console import Console

from kubelings.manifest import get_manifest
from kubelings.models import Chapter, Exercise, Manifest
from kubelings.runner import NOT_DONE_MARKER, ExerciseRunner, RunResult
from kubelings.ui import (
    render_banner,
    render_hint,
    render_progress_table,
    render_result,
)


def test_not_done_marker_constant():
    """Verify NOT_DONE_MARKER constant is defined correctly."""
    assert NOT_DONE_MARKER == "I AM NOT DONE"


def test_check_marker_present_and_absent(tmp_path: Path):
    """Test ExerciseRunner.check_marker() identifies the not done marker correctly."""
    exercise_file = tmp_path / "test_exercise.py"

    # 1. With marker
    exercise_file.write_text("# I AM NOT DONE\nprint('hello')\n")
    assert ExerciseRunner.check_marker(exercise_file) is True

    # Also test on instance
    runner = ExerciseRunner()
    assert runner.check_marker(exercise_file) is True

    # 2. Without marker
    exercise_file.write_text("print('hello')\n")
    assert ExerciseRunner.check_marker(exercise_file) is False
    assert runner.check_marker(exercise_file) is False

    # 3. Nonexistent file returns False
    nonexistent = tmp_path / "does_not_exist.py"
    assert ExerciseRunner.check_marker(nonexistent) is False


def test_run_exercise_fails_when_marker_present(tmp_path: Path):
    """Test run_exercise fails when # I AM NOT DONE is present even if code exits with 0."""
    exercise_file = tmp_path / "ex01.py"
    exercise_file.write_text("# I AM NOT DONE\nprint('Working on exercise')\n")

    exercise = Exercise(
        name="ex01",
        title="Sample Exercise",
        path=str(exercise_file),
        chapter_name="01_pods",
    )

    runner = ExerciseRunner()
    result = runner.run_exercise(exercise)

    assert isinstance(result, RunResult)
    assert result.exercise == exercise
    assert result.passed is False
    assert result.has_not_done_marker is True
    assert result.exit_code == 0
    assert "Working on exercise" in result.output
    assert result.duration_ms >= 0.0


def test_run_exercise_passes_when_marker_absent(tmp_path: Path):
    """Test run_exercise passes when marker is removed and execution exits 0."""
    exercise_file = tmp_path / "ex02.py"
    exercise_file.write_text("print('All tests passed successfully!')\n")

    exercise = Exercise(
        name="ex02",
        title="Completed Exercise",
        path=str(exercise_file),
        chapter_name="01_pods",
    )

    runner = ExerciseRunner()
    result = runner.run_exercise(exercise)

    assert result.passed is True
    assert result.has_not_done_marker is False
    assert result.exit_code == 0
    assert "All tests passed successfully!" in result.output
    assert result.error is None
    assert result.duration_ms >= 0.0


def test_run_exercise_assertion_error(tmp_path: Path):
    """Test run_exercise captures AssertionError and failure details."""
    exercise_file = tmp_path / "ex03.py"
    exercise_file.write_text(
        "print('Validating pod spec...')\n"
        "assert False, 'Pod spec validation failed: container image missing'\n"
    )

    exercise = Exercise(
        name="ex03",
        title="Failing Exercise",
        path=str(exercise_file),
        chapter_name="01_pods",
    )

    runner = ExerciseRunner()
    result = runner.run_exercise(exercise)

    assert result.passed is False
    assert result.has_not_done_marker is False
    assert result.exit_code != 0
    assert "Validating pod spec..." in result.output
    assert result.error is not None
    assert "AssertionError" in result.error
    assert "Pod spec validation failed" in result.error


def test_run_exercise_syntax_error(tmp_path: Path):
    """Test run_exercise captures SyntaxError details and nonzero exit code."""
    exercise_file = tmp_path / "ex04.py"
    exercise_file.write_text("def invalid_syntax(\n")

    exercise = Exercise(
        name="ex04",
        title="Syntax Error Exercise",
        path=str(exercise_file),
        chapter_name="01_pods",
    )

    runner = ExerciseRunner()
    result = runner.run_exercise(exercise)

    assert result.passed is False
    assert result.exit_code != 0
    assert result.error is not None
    assert "SyntaxError" in result.error


def test_run_exercise_timeout(tmp_path: Path):
    """Test run_exercise handles script execution timeout gracefully."""
    exercise_file = tmp_path / "ex05.py"
    exercise_file.write_text("import time\ntime.sleep(10)\n")

    exercise = Exercise(
        name="ex05",
        title="Timeout Exercise",
        path=str(exercise_file),
        chapter_name="01_pods",
    )

    runner = ExerciseRunner()
    result = runner.run_exercise(exercise, timeout=0.2)

    assert result.passed is False
    assert result.exit_code != 0
    assert result.error is not None
    assert "timed out" in result.error.lower()


def test_run_exercise_file_not_found():
    """Test run_exercise handles nonexistent exercise file."""
    exercise = Exercise(
        name="nonexistent",
        title="Nonexistent Exercise",
        path="exercises/nonexistent/does_not_exist.py",
        chapter_name="01_pods",
    )

    runner = ExerciseRunner()
    result = runner.run_exercise(exercise)

    assert result.passed is False
    assert result.exit_code != 0
    assert result.error is not None
    assert "not found" in result.error.lower()


def test_run_exercise_custom_python_exe(tmp_path: Path):
    """Test run_exercise uses custom python executable when provided."""
    exercise_file = tmp_path / "ex06.py"
    exercise_file.write_text("print('Custom Python')\n")

    exercise = Exercise(
        name="ex06",
        title="Custom Python Exercise",
        path=str(exercise_file),
        chapter_name="01_pods",
    )

    runner = ExerciseRunner(python_exe=sys.executable)
    result = runner.run_exercise(exercise, python_exe=sys.executable)

    assert result.passed is True
    assert "Custom Python" in result.output


def test_render_banner():
    """Test render_banner output contains Kubelings title and wheel icon."""
    console = Console(record=True, width=120)
    banner = render_banner(console=console)
    assert banner is not None

    captured = console.export_text()
    assert "Kubelings" in captured
    assert "Kubernetes" in captured


def test_render_result_passed():
    """Test render_result for passed exercise renders green check and title."""
    ex = Exercise(
        name="pods01",
        title="First Pod Manifest",
        path="exercises/01_pods/pods01.py",
        chapter_name="01_pods",
    )
    result = RunResult(
        exercise=ex,
        passed=True,
        has_not_done_marker=False,
        output="Manifest valid!",
        exit_code=0,
        duration_ms=25.4,
    )

    console = Console(record=True, width=120)
    renderable = render_result(result, console=console)
    assert renderable is not None

    captured = console.export_text()
    assert "pods01" in captured
    assert "PASSED" in captured or "✓" in captured
    assert "First Pod Manifest" in captured
    assert "25.4ms" in captured


def test_render_result_not_done():
    """Test render_result for exercise with # I AM NOT DONE marker."""
    ex = Exercise(
        name="pods02",
        title="Multi-Container Pods",
        path="exercises/01_pods/pods02.py",
        chapter_name="01_pods",
    )
    result = RunResult(
        exercise=ex,
        passed=False,
        has_not_done_marker=True,
        output="Testing containers...",
        exit_code=0,
        duration_ms=12.0,
    )

    console = Console(record=True, width=120)
    renderable = render_result(result, console=console)
    assert renderable is not None

    captured = console.export_text()
    assert "pods02" in captured
    assert "NOT DONE" in captured or "I AM NOT DONE" in captured or "PROGRESS" in captured
    assert "Multi-Container Pods" in captured


def test_render_result_failed_with_diagnostics():
    """Test render_result for failed exercise with error and traceback diagnostics."""
    ex = Exercise(
        name="pods03",
        title="Init Containers",
        path="exercises/01_pods/pods03.py",
        chapter_name="01_pods",
    )
    result = RunResult(
        exercise=ex,
        passed=False,
        has_not_done_marker=False,
        output="Running check...",
        error="Traceback (most recent call last):\n  File 'pods03.py', line 12\nAssertionError: initContainer missing",
        exit_code=1,
        duration_ms=18.5,
    )

    console = Console(record=True, width=120)
    renderable = render_result(result, console=console)
    assert renderable is not None

    captured = console.export_text()
    assert "pods03" in captured
    assert "FAILED" in captured or "✗" in captured
    assert "AssertionError" in captured
    assert "initContainer missing" in captured


def test_render_hint_single_and_progressive():
    """Test render_hint renders numbered hints correctly."""
    ex = Exercise(
        name="pods01",
        title="First Pod Manifest",
        path="exercises/01_pods/pods01.py",
        chapter_name="01_pods",
        hints=[
            "Use apiVersion: v1 and kind: Pod",
            "Define metadata.name as nginx-pod",
            "Define spec.containers with name nginx and image nginx:1.25",
        ],
    )

    console = Console(record=True, width=120)

    # First hint (hint_index=0)
    render_hint(ex, hint_index=0, console=console)
    captured = console.export_text()
    assert "Hint 1" in captured or "1/3" in captured
    assert "apiVersion: v1" in captured

    # Second hint (hint_index=1)
    console2 = Console(record=True, width=120)
    render_hint(ex, hint_index=1, console=console2)
    captured2 = console2.export_text()
    assert "Hint 2" in captured2 or "2/3" in captured2
    assert "nginx-pod" in captured2


def test_render_hint_empty_and_out_of_bounds():
    """Test render_hint handles empty hints and out of bounds hint index."""
    ex_empty = Exercise(
        name="no_hints",
        title="No Hints Exercise",
        path="exercises/01_pods/no_hints.py",
        chapter_name="01_pods",
        hints=[],
    )
    console = Console(record=True, width=120)
    render_hint(ex_empty, hint_index=0, console=console)
    captured = console.export_text()
    assert "No hints available" in captured

    # Out of bounds index
    ex_with_hints = Exercise(
        name="has_hints",
        title="Hints Exercise",
        path="exercises/01_pods/has_hints.py",
        chapter_name="01_pods",
        hints=["Only one hint"],
    )
    console2 = Console(record=True, width=120)
    render_hint(ex_with_hints, hint_index=5, console=console2)
    captured2 = console2.export_text()
    assert "Only one hint" in captured2


def test_render_progress_table():
    """Test render_progress_table displays chapters, exercises, and status badges."""
    ex1 = Exercise(
        name="pods01", title="First Pod", path="exercises/01_pods/pods01.py", chapter_name="01_pods"
    )
    ex2 = Exercise(
        name="pods02",
        title="Multi Container",
        path="exercises/01_pods/pods02.py",
        chapter_name="01_pods",
    )
    ex3 = Exercise(
        name="ctrl01",
        title="ReplicaSet",
        path="exercises/02_controllers/ctrl01.py",
        chapter_name="02_controllers",
    )

    ch1 = Chapter(
        number=1, name="01_pods", title="Pods", description="Pod basics", exercises=[ex1, ex2]
    )
    ch2 = Chapter(
        number=2,
        name="02_controllers",
        title="Controllers",
        description="Controller basics",
        exercises=[ex3],
    )
    manifest = Manifest(chapters=[ch1, ch2])

    results_map = {
        "pods01": RunResult(
            exercise=ex1, passed=True, has_not_done_marker=False, output="", exit_code=0
        ),
        "pods02": RunResult(
            exercise=ex2, passed=False, has_not_done_marker=True, output="", exit_code=0
        ),
        # ctrl01 is not run yet (not in results_map)
    }

    console = Console(record=True, width=120)
    table = render_progress_table(manifest, results_map, console=console)
    assert table is not None

    captured = console.export_text()
    assert "01_pods" in captured or "Pods" in captured
    assert "02_controllers" in captured or "Controllers" in captured
    assert "pods01" in captured
    assert "pods02" in captured
    assert "ctrl01" in captured
    assert "DONE" in captured or "PASSED" in captured
    assert "IN PROGRESS" in captured or "NOT DONE" in captured


def test_render_progress_table_with_full_manifest():
    """Test render_progress_table works with the real curriculum manifest."""
    manifest = get_manifest()
    results_map = {
        "pods01": RunResult(
            exercise=manifest.all_exercises[0],
            passed=True,
            has_not_done_marker=False,
            output="",
            exit_code=0,
        )
    }

    console = Console(record=True, width=120)
    table = render_progress_table(manifest, results_map, console=console)
    assert table is not None

    captured = console.export_text()
    assert "pods01" in captured
    assert "troubleshoot05" in captured

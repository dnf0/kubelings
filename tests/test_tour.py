"""Unit tests for the Kubelings onboarding tour engine."""

import io
from unittest.mock import MagicMock

import pytest
from rich.console import Console

from kubelings.cluster import ClusterDetector
from kubelings.models import Exercise
from kubelings.runner import ExerciseRunner, RunResult
from kubelings.tour import OnboardingTour, TourStep, TourStepResult


def test_tour_initialization():
    """Verify tour initializes exactly 5 steps in the expected order."""
    tour = OnboardingTour()
    assert len(tour.steps) == 5

    expected_names = [
        "welcome",
        "environment",
        "workflow",
        "guided_exercise",
        "tooling",
    ]
    actual_names = [step.name for step in tour.steps]
    assert actual_names == expected_names

    expected_nums = [1, 2, 3, 4, 5]
    actual_nums = [step.step_num for step in tour.steps]
    assert actual_nums == expected_nums

    for step in tour.steps:
        assert isinstance(step, TourStep)
        assert step.title
        assert step.description


def test_tour_step_rendering():
    """Verify step 1 renders welcome banner and pedagogical philosophy."""
    string_io = io.StringIO()
    test_console = Console(file=string_io, force_terminal=True, width=120)
    tour = OnboardingTour(console=test_console)

    renderable = tour.render_step(1)
    assert renderable is not None

    test_console.print(renderable)
    output = string_io.getvalue()

    assert "Kubelings" in output or "☸" in output
    assert "Active Debugging" in output or "active debugging" in output.lower()
    assert "sub-30ms" in output or "30ms" in output or "feedback" in output.lower()
    assert "Test-Driven" in output or "test-driven" in output.lower()


def test_tour_non_interactive_run_all():
    """Verify running all 5 steps in non-interactive mode returns 5 successful results."""
    string_io = io.StringIO()
    test_console = Console(file=string_io, force_terminal=True, width=120)
    tour = OnboardingTour(console=test_console)

    results = tour.run_all(interactive=False)
    assert len(results) == 5

    for idx, result in enumerate(results, start=1):
        assert isinstance(result, TourStepResult)
        assert result.step_num == idx
        assert result.success is True
        assert result.name == tour.steps[idx - 1].name
        assert isinstance(result.details, dict)


def test_tour_json_output():
    """Verify to_json() contains total_steps=5 and complete step metadata."""
    tour = OnboardingTour()
    data = tour.to_json()

    assert isinstance(data, dict)
    assert data.get("total_steps") == 5
    assert "steps" in data
    assert len(data["steps"]) == 5

    for idx, step_meta in enumerate(data["steps"], start=1):
        assert step_meta["step_num"] == idx
        assert step_meta["name"] == tour.steps[idx - 1].name
        assert step_meta["title"] == tour.steps[idx - 1].title
        assert step_meta["description"] == tour.steps[idx - 1].description


def test_tour_specific_step_execution():
    """Verify run_step(4, interactive=False) executes the pods01 guided walkthrough."""
    string_io = io.StringIO()
    test_console = Console(file=string_io, force_terminal=True, width=120)
    tour = OnboardingTour(console=test_console)

    result = tour.run_step(4, interactive=False)
    assert isinstance(result, TourStepResult)
    assert result.step_num == 4
    assert result.name == "guided_exercise"
    assert result.success is True
    assert "pods01" in str(result.details)
    assert "exercise" in result.details
    assert result.details["exercise"] == "pods01"

    output = string_io.getvalue()
    assert "pods01" in output
    assert "nginx" in output.lower()


def test_tour_environment_step_diagnostics():
    """Verify step 2 environment and cluster diagnostics probe."""
    mock_detector = MagicMock(spec=ClusterDetector)
    mock_detector.get_cluster_status.return_value = {
        "available": True,
        "context": "kind-test-cluster",
        "provider": "local",
    }

    string_io = io.StringIO()
    test_console = Console(file=string_io, force_terminal=True, width=120)
    tour = OnboardingTour(console=test_console, cluster_detector=mock_detector)

    result = tour.run_step(2, interactive=False)
    assert result.success is True
    assert result.step_num == 2
    assert result.name == "environment"
    assert "python_version" in result.details
    assert "cluster_status" in result.details
    assert result.details["cluster_status"]["available"] is True
    assert result.details["cluster_status"]["context"] == "kind-test-cluster"


def test_tour_guided_exercise_with_custom_runner():
    """Verify step 4 uses the injected ExerciseRunner properly."""
    mock_runner = MagicMock(spec=ExerciseRunner)
    mock_exercise = Exercise(
        name="pods01",
        title="First Pod Manifest & Spec",
        path="exercises/01_pods/pods01.py",
        chapter_name="01_pods",
    )
    mock_runner.run_exercise.return_value = RunResult(
        exercise=mock_exercise,
        passed=False,
        has_not_done_marker=False,
        output="Mock initial failure output for walkthrough",
        error="Pod name must be 'nginx-web'",
        exit_code=1,
        duration_ms=12.5,
    )

    string_io = io.StringIO()
    test_console = Console(file=string_io, force_terminal=True, width=120)
    tour = OnboardingTour(console=test_console, runner=mock_runner)

    result = tour.run_step(4, interactive=False)
    assert result.success is True
    assert result.details["exercise"] == "pods01"
    assert "initial_output" in result.details or "initial_error" in result.details
    assert mock_runner.run_exercise.called


def test_tour_invalid_step_number():
    """Verify executing or rendering an out-of-range step raises ValueError."""
    tour = OnboardingTour()

    with pytest.raises(ValueError, match="Invalid step number"):
        tour.run_step(0, interactive=False)

    with pytest.raises(ValueError, match="Invalid step number"):
        tour.run_step(6, interactive=False)

    with pytest.raises(ValueError, match="Invalid step number"):
        tour.render_step(99)


@pytest.mark.parametrize("step_num", [1, 2, 3, 4, 5])
def test_tour_all_steps_rendering(step_num: int):
    """Verify render_step produces valid Rich renderables for all 5 steps."""
    string_io = io.StringIO()
    test_console = Console(file=string_io, force_terminal=True, width=120)
    tour = OnboardingTour(console=test_console)

    renderable = tour.render_step(step_num)
    assert renderable is not None
    test_console.print(renderable)
    output = string_io.getvalue()
    assert len(output) > 0


def test_tour_interactive_mode_progression(monkeypatch: pytest.MonkeyPatch):
    """Verify interactive mode advances on input and handles interruptions gracefully."""
    monkeypatch.setattr("builtins.input", lambda: "")

    string_io = io.StringIO()
    test_console = Console(file=string_io, force_terminal=True, width=120)
    tour = OnboardingTour(console=test_console)

    result = tour.run_step(1, interactive=True)
    assert result.success is True

    # Test interrupt handling
    def raise_interrupt():
        raise KeyboardInterrupt()

    monkeypatch.setattr("builtins.input", raise_interrupt)
    result_interrupted = tour.run_step(1, interactive=True)
    assert result_interrupted.success is True

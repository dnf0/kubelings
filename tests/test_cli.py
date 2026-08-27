"""Tests for Kubelings Typer CLI commands and Watcher engine."""

import threading
from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from kubelings import __version__
from kubelings.cli import app
from kubelings.models import Chapter, Exercise, Manifest
from kubelings.runner import ExerciseRunner
from kubelings.watcher import (
    WatchEngine,
    find_next_incomplete_exercise,
    run_watch_loop,
)

runner = CliRunner()


# ============================================================================
# CLI Command Tests
# ============================================================================


def test_cli_help():
    """Verify kubelings --help returns exit code 0 and lists all commands."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Kubelings" in result.stdout
    assert "list" in result.stdout
    assert "hint" in result.stdout
    assert "run" in result.stdout
    assert "verify" in result.stdout
    assert "cluster" in result.stdout
    assert "watch" in result.stdout
    assert "version" in result.stdout


def test_cli_version_command_and_flag():
    """Verify kubelings version command and --version flag output current package version."""
    res_cmd = runner.invoke(app, ["version"])
    assert res_cmd.exit_code == 0
    assert __version__ in res_cmd.stdout

    res_flag = runner.invoke(app, ["--version"])
    assert res_flag.exit_code == 0
    assert __version__ in res_flag.stdout


def test_cli_list_command():
    """Verify kubelings list prints banner, chapters, and exercises with exit code 0."""
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    assert "☸" in result.stdout or "Kubelings" in result.stdout
    assert "01_pods" in result.stdout
    assert "pods01" in result.stdout
    assert "13_troubleshooting" in result.stdout
    assert "troubleshoot05" in result.stdout


def test_cli_hint_command_valid_exercise():
    """Verify kubelings hint <valid_exercise> renders hint panel with exit code 0."""
    result = runner.invoke(app, ["hint", "pods01"])
    assert result.exit_code == 0
    assert "Hint" in result.stdout or "💡" in result.stdout
    assert "pods01" in result.stdout


def test_cli_hint_command_with_hint_number():
    """Verify kubelings hint with specific hint-num parameter."""
    result1 = runner.invoke(app, ["hint", "pods01", "--hint-num", "1"])
    assert result1.exit_code == 0
    assert "Hint 1" in result1.stdout or "1/" in result1.stdout

    result2 = runner.invoke(app, ["hint", "pods01", "-n", "2"])
    assert result2.exit_code == 0
    assert "Hint 2" in result2.stdout or "2/" in result2.stdout


def test_cli_hint_command_invalid_exercise():
    """Verify kubelings hint with invalid exercise name returns exit code 1."""
    result = runner.invoke(app, ["hint", "nonexistent_exercise_12345"])
    assert result.exit_code == 1
    assert "not found" in result.stdout.lower()


def test_cli_run_command_invalid_exercise():
    """Verify kubelings run with invalid exercise returns exit code 1."""
    result = runner.invoke(app, ["run", "invalid_exercise_xyz"])
    assert result.exit_code == 1
    assert "not found" in result.stdout.lower()


def test_cli_run_command_passing_exercise(tmp_path: Path):
    """Verify kubelings run executes passing exercise and exits with 0."""
    ex_file = tmp_path / "pods01.py"
    ex_file.write_text("print('All checks passed!')\n")

    fake_ex = Exercise(
        name="pods01",
        title="First Pod",
        path=str(ex_file),
        chapter_name="01_pods",
    )

    with patch("kubelings.cli.get_exercise_by_name", return_value=fake_ex):
        result = runner.invoke(app, ["run", "pods01"])
        assert result.exit_code == 0
        assert "PASSED" in result.stdout or "passed" in result.stdout.lower()


def test_cli_run_command_failing_exercise(tmp_path: Path):
    """Verify kubelings run executes failing exercise and exits with 1."""
    ex_file = tmp_path / "pods01.py"
    ex_file.write_text("assert False, 'Pod spec validation failed'\n")

    fake_ex = Exercise(
        name="pods01",
        title="First Pod",
        path=str(ex_file),
        chapter_name="01_pods",
    )

    with patch("kubelings.cli.get_exercise_by_name", return_value=fake_ex):
        result = runner.invoke(app, ["run", "pods01"])
        assert result.exit_code == 1
        assert (
            "FAILED" in result.stdout
            or "✗" in result.stdout
            or "Pod spec validation failed" in result.stdout
        )


def test_cli_verify_command(tmp_path: Path):
    """Verify kubelings verify runs all exercises and prints progress table."""
    ex1_file = tmp_path / "pods01.py"
    ex1_file.write_text("print('pass')\n")
    ex2_file = tmp_path / "pods02.py"
    ex2_file.write_text("# I AM NOT DONE\n")

    ex1 = Exercise(name="pods01", title="First Pod", path=str(ex1_file), chapter_name="01_pods")
    ex2 = Exercise(name="pods02", title="Sidecar", path=str(ex2_file), chapter_name="01_pods")
    ch = Chapter(
        number=1, name="01_pods", title="Pods", description="Core Pods", exercises=[ex1, ex2]
    )
    test_manifest = Manifest(chapters=[ch])

    with patch("kubelings.cli.get_manifest", return_value=test_manifest):
        result = runner.invoke(app, ["verify"])
        assert "pods01" in result.stdout
        assert "pods02" in result.stdout
        assert "Progress" in result.stdout or "Completed" in result.stdout


def test_cli_cluster_command_offline_mode():
    """Verify kubelings cluster reports status cleanly when no cluster is present."""
    with patch("kubelings.cluster.ClusterDetector.get_cluster_status") as mock_status:
        mock_status.return_value = {
            "available": False,
            "context": "none",
            "provider": "none",
        }
        result = runner.invoke(app, ["cluster"])
        assert result.exit_code == 0
        assert "Cluster Status" in result.stdout or "Cluster" in result.stdout
        assert (
            "offline" in result.stdout.lower()
            or "not detected" in result.stdout.lower()
            or "none" in result.stdout.lower()
        )


def test_cli_cluster_command_online_mode():
    """Verify kubelings cluster reports connected cluster and context details."""
    with patch("kubelings.cluster.ClusterDetector.get_cluster_status") as mock_status:
        mock_status.return_value = {
            "available": True,
            "context": "kind-kubelings",
            "provider": "local",
        }
        result = runner.invoke(app, ["cluster"])
        assert result.exit_code == 0
        assert "kind-kubelings" in result.stdout
        assert "local" in result.stdout.lower() or "connected" in result.stdout.lower()


def test_cli_watch_command_dispatches_loop():
    """Verify kubelings watch command dispatches to run_watch_loop."""
    with patch("kubelings.watcher.run_watch_loop") as mock_watch:
        result = runner.invoke(app, ["watch"])
        assert result.exit_code == 0
        mock_watch.assert_called_once()


# ============================================================================
# Watcher Engine Unit Tests
# ============================================================================


def test_find_next_incomplete_exercise_returns_first_failing(tmp_path: Path):
    """Verify find_next_incomplete_exercise returns the first incomplete exercise."""
    f1 = tmp_path / "ex1.py"
    f1.write_text("print('pass')\n")
    f2 = tmp_path / "ex2.py"
    f2.write_text("# I AM NOT DONE\n")
    f3 = tmp_path / "ex3.py"
    f3.write_text("print('pass')\n")

    ex1 = Exercise("ex1", "Ex 1", str(f1), "ch1")
    ex2 = Exercise("ex2", "Ex 2", str(f2), "ch1")
    ex3 = Exercise("ex3", "Ex 3", str(f3), "ch1")

    manifest = Manifest(chapters=[Chapter(1, "ch1", "Ch 1", "Desc", [ex1, ex2, ex3])])
    runner_inst = ExerciseRunner()

    next_ex = find_next_incomplete_exercise(manifest, runner_inst)
    assert next_ex is not None
    assert next_ex.name == "ex2"


def test_find_next_incomplete_exercise_returns_none_when_all_pass(tmp_path: Path):
    """Verify find_next_incomplete_exercise returns None when all exercises pass."""
    f1 = tmp_path / "ex1.py"
    f1.write_text("print('pass')\n")
    f2 = tmp_path / "ex2.py"
    f2.write_text("print('pass 2')\n")

    ex1 = Exercise("ex1", "Ex 1", str(f1), "ch1")
    ex2 = Exercise("ex2", "Ex 2", str(f2), "ch1")

    manifest = Manifest(chapters=[Chapter(1, "ch1", "Ch 1", "Desc", [ex1, ex2])])
    runner_inst = ExerciseRunner()

    next_ex = find_next_incomplete_exercise(manifest, runner_inst)
    assert next_ex is None


def test_find_next_incomplete_exercise_with_start_from(tmp_path: Path):
    """Verify find_next_incomplete_exercise respects start_from parameter."""
    f1 = tmp_path / "ex1.py"
    f1.write_text("# I AM NOT DONE\n")
    f2 = tmp_path / "ex2.py"
    f2.write_text("# I AM NOT DONE\n")

    ex1 = Exercise("ex1", "Ex 1", str(f1), "ch1")
    ex2 = Exercise("ex2", "Ex 2", str(f2), "ch1")

    manifest = Manifest(chapters=[Chapter(1, "ch1", "Ch 1", "Desc", [ex1, ex2])])
    runner_inst = ExerciseRunner()

    next_ex = find_next_incomplete_exercise(manifest, runner_inst, start_from="ex2")
    assert next_ex is not None
    assert next_ex.name == "ex2"


def test_watch_engine_step_advances_on_pass(tmp_path: Path):
    """Verify WatchEngine advances to next exercise when current exercise passes."""
    f1 = tmp_path / "ex1.py"
    f1.write_text("# I AM NOT DONE\n")
    f2 = tmp_path / "ex2.py"
    f2.write_text("# I AM NOT DONE\n")

    ex1 = Exercise("ex1", "Ex 1", str(f1), "ch1")
    ex2 = Exercise("ex2", "Ex 2", str(f2), "ch1")
    manifest = Manifest(chapters=[Chapter(1, "ch1", "Ch 1", "Desc", [ex1, ex2])])

    engine = WatchEngine(manifest=manifest, runner=ExerciseRunner())
    assert engine.current_exercise == ex1

    # User finishes ex1
    f1.write_text("print('pass')\n")

    # Evaluate current exercise (which now passes)
    advanced = engine.evaluate_current()
    assert advanced is True
    assert engine.current_exercise == ex2
    assert engine.all_completed is False


def test_watch_engine_all_completed_celebration(tmp_path: Path):
    """Verify WatchEngine sets all_completed when final exercise passes."""
    f1 = tmp_path / "ex1.py"
    f1.write_text("# I AM NOT DONE\n")

    ex1 = Exercise("ex1", "Ex 1", str(f1), "ch1")
    manifest = Manifest(chapters=[Chapter(1, "ch1", "Ch 1", "Desc", [ex1])])

    engine = WatchEngine(manifest=manifest, runner=ExerciseRunner())
    assert engine.current_exercise == ex1

    # User finishes ex1
    f1.write_text("print('pass')\n")

    advanced = engine.evaluate_current()
    assert advanced is True
    assert engine.current_exercise is None
    assert engine.all_completed is True


def test_watch_engine_file_filter(tmp_path: Path):
    """Verify WatchEngine file filter only triggers on relevant Python/YAML changes."""
    engine = WatchEngine(manifest=Manifest([]), runner=ExerciseRunner())

    assert engine.should_process_file(str(tmp_path / "ex1.py")) is True
    assert engine.should_process_file(str(tmp_path / "test.yaml")) is True
    assert engine.should_process_file(str(tmp_path / "test.yml")) is True
    assert engine.should_process_file(str(tmp_path / "ex1.pyc")) is False
    assert engine.should_process_file(str(tmp_path / ".git" / "HEAD")) is False
    assert engine.should_process_file(str(tmp_path / "__pycache__" / "foo.py")) is False


def test_run_watch_loop_graceful_stop_event(tmp_path: Path):
    """Verify run_watch_loop terminates gracefully when stop_event is set."""
    f1 = tmp_path / "ex1.py"
    f1.write_text("# I AM NOT DONE\n")
    ex1 = Exercise("ex1", "Ex 1", str(f1), "ch1")
    manifest = Manifest(chapters=[Chapter(1, "ch1", "Ch 1", "Desc", [ex1])])

    stop_event = threading.Event()
    stop_event.set()  # Stop immediately

    # Should exit cleanly without hanging
    run_watch_loop(manifest=manifest, stop_event=stop_event, watch_dir=tmp_path)


def test_run_watch_loop_handles_keyboard_interrupt(tmp_path: Path):
    """Verify run_watch_loop catches KeyboardInterrupt and exits cleanly."""
    f1 = tmp_path / "ex1.py"
    f1.write_text("# I AM NOT DONE\n")
    ex1 = Exercise("ex1", "Ex 1", str(f1), "ch1")
    manifest = Manifest(chapters=[Chapter(1, "ch1", "Ch 1", "Desc", [ex1])])

    with patch("kubelings.watcher.watch", side_effect=KeyboardInterrupt):
        run_watch_loop(manifest=manifest, watch_dir=tmp_path)

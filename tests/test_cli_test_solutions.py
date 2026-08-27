import pytest
from typer.testing import CliRunner
from kubelings.cli import app

runner = CliRunner()


def test_cli_test_solutions_single():
    result = runner.invoke(app, ["test", "--exercise", "pods01"])
    assert result.exit_code == 0
    assert "pods01" in result.stdout
    assert "Passed" in result.stdout or "passed" in result.stdout.lower()


def test_cli_test_solutions_chapter():
    result = runner.invoke(app, ["test", "--chapter", "01_pods"])
    assert result.exit_code == 0
    assert "01_pods" in result.stdout


def test_cli_test_solutions_invalid_exercise():
    result = runner.invoke(app, ["test", "--exercise", "nonexistent99"])
    assert result.exit_code == 1
    assert "not found" in result.stdout.lower()

"""Tests for CLI v2 features (tree, lint, tui)."""

from typer.testing import CliRunner

from kubelings.cli import app

runner = CliRunner()


def test_cli_tree_command():
    result = runner.invoke(app, ["tree", "pods01"])
    assert result.exit_code == 0
    assert "Kubernetes Resource" in result.output or "Topology" in result.output


def test_cli_lint_command_on_exercise():
    result = runner.invoke(app, ["lint", "solutions/01_pods/pods01.yaml"])
    assert result.exit_code == 0
    assert "Manifest Linter" in result.output


def test_cli_lint_command_on_nonexistent():
    result = runner.invoke(app, ["lint", "nonexistent_file.yaml"])
    assert result.exit_code == 1
    assert "not found" in result.output.lower() or "ERROR" in result.output


def test_cli_tui_command_help():
    result = runner.invoke(app, ["tui", "--help"])
    assert result.exit_code == 0
    assert "dashboard" in result.output.lower() or "tui" in result.output.lower()

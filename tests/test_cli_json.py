"""Tests for Kubelings CLI JSON output formats across core commands."""

import json
from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from kubelings.cli import app
from kubelings.models import Exercise

runner = CliRunner()


def test_cli_list_json():
    result = runner.invoke(app, ["list", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert "total_chapters" in data
    assert data["total_chapters"] == 23
    assert "total_exercises" in data
    assert data["total_exercises"] == 102
    assert len(data["chapters"]) == 23
    first_ch = data["chapters"][0]
    assert first_ch["name"] == "01_pods"
    assert len(first_ch["exercises"]) == 6
    assert first_ch["exercises"][0]["name"] == "pods01"


def test_cli_run_json():
    result = runner.invoke(app, ["run", "pods01", "--json"])
    assert result.exit_code in (0, 1)
    data = json.loads(result.stdout)
    assert data["exercise"] == "pods01"
    assert "passed" in data
    assert "has_not_done_marker" in data
    assert "duration_ms" in data
    assert "hints_available" in data


def test_cli_run_json_passing(tmp_path: Path):
    ex_file = tmp_path / "pods01.py"
    ex_file.write_text("print('All checks passed!')\n")

    fake_ex = Exercise(
        name="pods01",
        title="First Pod",
        path=str(ex_file),
        chapter_name="01_pods",
    )

    with patch("kubelings.cli.get_exercise_by_name", return_value=fake_ex):
        result = runner.invoke(app, ["run", "pods01", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["exercise"] == "pods01"
        assert data["passed"] is True
        assert data["has_not_done_marker"] is False
        assert data["exit_code"] == 0


def test_cli_run_json_invalid_exercise():
    result = runner.invoke(app, ["run", "nonexistent_ex", "--json"])
    assert result.exit_code == 1
    data = json.loads(result.stdout)
    assert "error" in data


def test_cli_verify_json():
    result = runner.invoke(app, ["verify", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert data["total"] == 102
    assert "completed" in data
    assert "in_progress" in data
    assert "not_started" in data
    assert "percentage" in data
    assert "results" in data
    assert len(data["results"]) == 102


def test_cli_cluster_json():
    result = runner.invoke(app, ["cluster", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert "available" in data
    assert "provider" in data
    assert "cluster_mode" in data


def test_cli_cluster_json_mock_online():
    with patch("kubelings.cluster.ClusterDetector.get_cluster_status") as mock_status:
        mock_status.return_value = {
            "available": True,
            "context": "kind-kubelings",
            "provider": "local",
        }
        result = runner.invoke(app, ["cluster", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["available"] is True
        assert data["context"] == "kind-kubelings"
        assert data["provider"] == "local"
        assert data["cluster_mode"] == "live"


def test_cli_hint_json():
    result = runner.invoke(app, ["hint", "pods01", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert data["exercise"] == "pods01"
    assert "hint" in data
    assert "hint_index" in data
    assert "total_hints" in data


def test_cli_hint_json_with_index():
    result = runner.invoke(app, ["hint", "pods01", "--index", "1", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert data["exercise"] == "pods01"
    assert data["hint_index"] == 1


def test_cli_hint_json_invalid_exercise():
    result = runner.invoke(app, ["hint", "nonexistent_ex", "--json"])
    assert result.exit_code == 1
    data = json.loads(result.stdout)
    assert "error" in data

from pathlib import Path

import pytest
from typer.testing import CliRunner

from kubelings.cli import app
from kubelings.scaffold import get_starter_content, init_workspace, reset_exercise


def test_get_starter_content_valid():
    content = get_starter_content("pods01")
    assert "POD_MANIFEST" in content
    assert "nginx-web" in content


def test_get_starter_content_invalid():
    with pytest.raises(KeyError):
        get_starter_content("nonexistent_ex")


def test_init_workspace(tmp_path: Path):
    init_workspace(tmp_path)
    assert (tmp_path / "exercises").exists()
    assert (tmp_path / "exercises" / "01_pods" / "pods01.py").exists()
    assert (tmp_path / "exercises" / "13_troubleshooting" / "troubleshoot05.py").exists()


def test_init_workspace_existing_no_force(tmp_path: Path):
    (tmp_path / "exercises").mkdir()
    (tmp_path / "exercises" / "dummy.txt").write_text("hello")
    with pytest.raises(FileExistsError):
        init_workspace(tmp_path, force=False)


def test_init_workspace_force(tmp_path: Path):
    (tmp_path / "exercises").mkdir()
    (tmp_path / "exercises" / "dummy.txt").write_text("hello")
    init_workspace(tmp_path, force=True)
    assert (tmp_path / "exercises" / "01_pods" / "pods01.py").exists()


def test_reset_exercise(tmp_path: Path):
    init_workspace(tmp_path)
    ex_file = tmp_path / "exercises" / "01_pods" / "pods01.py"
    ex_file.write_text("# Modified by student")
    assert "POD_MANIFEST" not in ex_file.read_text()

    reset_exercise("pods01", workspace_root=tmp_path)
    assert "POD_MANIFEST" in ex_file.read_text()


def test_cli_init_command(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0
    assert "Initialized" in result.stdout or "ready" in result.stdout.lower()
    assert (tmp_path / "exercises" / "01_pods" / "pods01.py").exists()


def test_cli_reset_command(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    runner.invoke(app, ["init"])

    ex_file = tmp_path / "exercises" / "01_pods" / "pods01.py"
    ex_file.write_text("broken")

    result = runner.invoke(app, ["reset", "pods01"])
    assert result.exit_code == 0
    assert "Reset" in result.stdout or "reset" in result.stdout.lower()
    assert "POD_MANIFEST" in ex_file.read_text()


def test_cli_reset_invalid_exercise():
    runner = CliRunner()
    result = runner.invoke(app, ["reset", "fake_ex"])
    assert result.exit_code == 1
    assert "Unknown" in result.stdout or "not found" in result.stdout.lower()


def test_init_workspace_root_fallback(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(Path, "home", lambda: tmp_path / "fake_home")
    init_workspace(Path("/"))
    assert (tmp_path / "fake_home" / "kubelings" / "exercises").exists()


def test_cli_init_command_from_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(Path, "home", lambda: tmp_path / "fake_home")
    runner = CliRunner()
    result = runner.invoke(app, ["init", "--dir", "/"])
    assert result.exit_code == 0
    assert "Initialized" in result.stdout
    assert (tmp_path / "fake_home" / "kubelings" / "exercises").exists()

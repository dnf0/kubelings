"""Workspace initialization and exercise reset utilities."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Optional

from kubelings.manifest import get_exercise_by_name


def _find_package_exercises_dir() -> Path:
    """Find the canonical source exercises directory in repo or package."""
    # 1. Check relative to this module in repo structure
    # kubelings/src/kubelings/scaffold.py -> kubelings/exercises
    repo_exercises = Path(__file__).resolve().parent.parent.parent / "exercises"
    if repo_exercises.exists() and repo_exercises.is_dir():
        return repo_exercises

    # 2. Check bundled package directory (e.g. inside installed package)
    bundled_exercises = Path(__file__).resolve().parent / "exercises"
    if bundled_exercises.exists() and bundled_exercises.is_dir():
        return bundled_exercises

    # 3. Fallback to current working directory if available
    cwd_exercises = Path.cwd() / "exercises"
    if cwd_exercises.exists() and cwd_exercises.is_dir():
        return cwd_exercises

    raise FileNotFoundError(
        "Could not locate the canonical 'exercises' directory in package or workspace."
    )


def _relative_exercise_path(exercise_path: str) -> Path:
    """Return the relative path inside the exercises directory."""
    p = Path(exercise_path)
    if p.parts and p.parts[0] == "exercises":
        return Path(*p.parts[1:])
    return p


def get_starter_content(exercise_name: str) -> str:
    """Get the original starter code for an exercise."""
    exercise = get_exercise_by_name(exercise_name)
    if exercise is None:
        raise KeyError(f"Exercise '{exercise_name}' not found in curriculum.")

    exercises_dir = _find_package_exercises_dir()
    rel_path = _relative_exercise_path(exercise.path)
    exercise_file = exercises_dir / rel_path
    if not exercise_file.exists():
        raise FileNotFoundError(f"Exercise file '{exercise.path}' not found at {exercise_file}")

    return exercise_file.read_text(encoding="utf-8")


def init_workspace(target_dir: Path, force: bool = False) -> bool:
    """Scaffold the exercises directory into a target workspace.

    Returns:
        True if exercise files were copied or overwritten.
        False if the exercises directory already exists with content and force is False.
    """
    resolved_target = target_dir.resolve()
    if (
        str(resolved_target) in ("/", "\\", "/exercises", "\\exercises")
        or resolved_target == Path("/").resolve()
    ):
        target_dir = Path.home() / "kubelings"

    try:
        target_dir.mkdir(parents=True, exist_ok=True)
    except (PermissionError, OSError):
        target_dir = Path.home() / "kubelings"
        target_dir.mkdir(parents=True, exist_ok=True)

    target_exercises_dir = target_dir / "exercises"

    if target_exercises_dir.exists() and not force:
        # Check if directory has existing contents
        if any(target_exercises_dir.iterdir()):
            return False

    source_exercises_dir = _find_package_exercises_dir()
    shutil.copytree(source_exercises_dir, target_exercises_dir, dirs_exist_ok=force)
    return True


def reset_exercise(exercise_name: str, workspace_root: Optional[Path] = None) -> Path:
    """Reset a specific exercise in the current workspace back to its original starter state."""
    exercise = get_exercise_by_name(exercise_name)
    if exercise is None:
        raise KeyError(f"Exercise '{exercise_name}' not found in curriculum.")

    root = workspace_root or Path.cwd()
    target_file = root / exercise.path
    target_file.parent.mkdir(parents=True, exist_ok=True)

    starter_content = get_starter_content(exercise_name)
    target_file.write_text(starter_content, encoding="utf-8")
    return target_file

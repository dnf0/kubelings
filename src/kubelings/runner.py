"""Exercise execution and evaluation runner for Kubelings."""

import os
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union

import yaml

from kubelings.models import Exercise
from kubelings.validator import ManifestValidationError
from kubelings.validators import get_validator

NOT_DONE_MARKER = "I AM NOT DONE"

INCOMPLETE_MARKERS = (
    "I AM NOT DONE",
    "TODO",
    "FIXME",
    "___",
    "/* ??? */",
    "<!-- ANSWER -->",
    "???",
)


@dataclass
class RunResult:
    """Result of running and evaluating an exercise."""

    exercise: Exercise
    passed: bool
    has_not_done_marker: bool = False
    output: str = ""
    error: Optional[str] = None
    exit_code: int = 0
    duration_ms: float = 0.0


def format_yaml_error(err: yaml.YAMLError, file_path: Path) -> str:
    """Format a PyYAML error into a clean diagnostic string."""
    mark = getattr(err, "problem_mark", None)
    if mark is not None:
        line = mark.line + 1
        col = mark.column + 1
        problem = getattr(err, "problem", str(err))
        snippet = getattr(mark, "get_snippet", lambda: None)()

        msg_lines = [
            f"❌ YAML Syntax Error in {file_path}:",
            f"   Line {line}, Column {col}: {problem}",
        ]
        if snippet:
            parts = snippet.splitlines()
            if len(parts) >= 2:
                msg_lines.append(f"   > {parts[0]}")
                msg_lines.append(f"     {parts[1]}")
            elif len(parts) == 1:
                msg_lines.append(f"   > {parts[0]}")
        return "\n".join(msg_lines)
    return f"❌ YAML Syntax Error in {file_path}:\n   {err}"


class ExerciseRunner:
    """Executes and evaluates Kubelings exercises."""

    def __init__(
        self,
        python_exe: Optional[str] = None,
        default_timeout: float = 30.0,
    ) -> None:
        self.python_exe = python_exe or sys.executable
        self.default_timeout = default_timeout

    @staticmethod
    def check_marker(path: Union[Path, str]) -> bool:
        """Check if an exercise file contains NOT_DONE markers, TODOs, or cloze blanks."""
        p = Path(path)
        if not p.exists() or not p.is_file():
            return True
        try:
            content = p.read_text(encoding="utf-8", errors="replace")
            return any(marker in content for marker in INCOMPLETE_MARKERS)
        except OSError:
            return True

    def run_exercise(
        self,
        exercise: Exercise,
        python_exe: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> RunResult:
        """Execute an exercise script and evaluate its result."""
        file_path = exercise.file_path
        exe = python_exe or self.python_exe or sys.executable
        timeout_sec = timeout if timeout is not None else self.default_timeout

        if not file_path.exists():
            return RunResult(
                exercise=exercise,
                passed=False,
                has_not_done_marker=False,
                output="",
                error=f"Exercise file not found: {file_path}",
                exit_code=1,
                duration_ms=0.0,
            )

        if file_path.suffix in (".yaml", ".yml"):
            start_time = time.perf_counter()
            has_marker = self.check_marker(file_path)
            if has_marker:
                elapsed_ms = (time.perf_counter() - start_time) * 1000.0
                return RunResult(
                    exercise=exercise,
                    passed=False,
                    has_not_done_marker=True,
                    output="Exercise still contains incomplete markers (??? or TODO). Fill them in to complete the exercise.",
                    error=None,
                    exit_code=1,
                    duration_ms=round(elapsed_ms, 2),
                )

            try:
                raw_text = file_path.read_text(encoding="utf-8", errors="replace")
            except OSError as exc:
                elapsed_ms = (time.perf_counter() - start_time) * 1000.0
                return RunResult(
                    exercise=exercise,
                    passed=False,
                    has_not_done_marker=False,
                    output="",
                    error=f"Failed to read exercise file: {exc}",
                    exit_code=1,
                    duration_ms=round(elapsed_ms, 2),
                )

            try:
                parsed_docs = list(yaml.safe_load_all(raw_text))
            except yaml.YAMLError as exc:
                elapsed_ms = (time.perf_counter() - start_time) * 1000.0
                formatted_err = format_yaml_error(exc, file_path)
                return RunResult(
                    exercise=exercise,
                    passed=False,
                    has_not_done_marker=False,
                    output="",
                    error=formatted_err,
                    exit_code=1,
                    duration_ms=round(elapsed_ms, 2),
                )

            docs = [d for d in parsed_docs if d is not None]
            manifest = docs[0] if len(docs) == 1 else (docs if len(docs) > 1 else {})

            validator = get_validator(exercise.name)
            if validator is None:
                elapsed_ms = (time.perf_counter() - start_time) * 1000.0
                return RunResult(
                    exercise=exercise,
                    passed=False,
                    has_not_done_marker=False,
                    output="",
                    error=f"No validator registered for exercise '{exercise.name}'",
                    exit_code=1,
                    duration_ms=round(elapsed_ms, 2),
                )

            try:
                validator(manifest, raw_text)
            except (AssertionError, ManifestValidationError) as exc:
                elapsed_ms = (time.perf_counter() - start_time) * 1000.0
                err_msg = str(exc)
                error_text = (
                    f"❌ Validation Failed: {err_msg}" if err_msg else "❌ Validation Failed"
                )
                return RunResult(
                    exercise=exercise,
                    passed=False,
                    has_not_done_marker=False,
                    output="",
                    error=error_text,
                    exit_code=1,
                    duration_ms=round(elapsed_ms, 2),
                )
            except Exception as exc:
                elapsed_ms = (time.perf_counter() - start_time) * 1000.0
                return RunResult(
                    exercise=exercise,
                    passed=False,
                    has_not_done_marker=False,
                    output="",
                    error=f"❌ Validation Error: {exc}",
                    exit_code=1,
                    duration_ms=round(elapsed_ms, 2),
                )

            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            return RunResult(
                exercise=exercise,
                passed=True,
                has_not_done_marker=False,
                output=f"✓ {exercise.name} passed!",
                error=None,
                exit_code=0,
                duration_ms=round(elapsed_ms, 2),
            )

        has_marker = self.check_marker(file_path)

        env = os.environ.copy()
        current_pythonpath = env.get("PYTHONPATH", "")
        project_src = str(Path.cwd() / "src")
        env["PYTHONPATH"] = f"{project_src}:{current_pythonpath}".strip(":")

        start_time = time.perf_counter()
        try:
            proc = subprocess.run(
                [exe, str(file_path)],
                capture_output=True,
                text=True,
                timeout=timeout_sec,
                env=env,
            )
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0

            stdout = proc.stdout or ""
            stderr = proc.stderr or ""
            passed = proc.returncode == 0

            error_msg: Optional[str] = None
            if stderr:
                error_msg = stderr
            elif proc.returncode != 0:
                error_msg = stdout if stdout else f"Process exited with code {proc.returncode}"

            return RunResult(
                exercise=exercise,
                passed=passed,
                has_not_done_marker=has_marker,
                output=stdout,
                error=error_msg,
                exit_code=proc.returncode,
                duration_ms=round(elapsed_ms, 2),
            )
        except subprocess.TimeoutExpired as exc:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            stdout_str = (
                exc.stdout.decode("utf-8", errors="replace")
                if isinstance(exc.stdout, bytes)
                else (exc.stdout or "")
            )
            stderr_str = (
                exc.stderr.decode("utf-8", errors="replace")
                if isinstance(exc.stderr, bytes)
                else (exc.stderr or "")
            )
            error_details = f"Exercise timed out after {timeout_sec} seconds" + (
                f":\n{stderr_str}" if stderr_str else ""
            )
            return RunResult(
                exercise=exercise,
                passed=False,
                has_not_done_marker=has_marker,
                output=stdout_str,
                error=error_details,
                exit_code=124,
                duration_ms=round(elapsed_ms, 2),
            )
        except Exception as exc:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            return RunResult(
                exercise=exercise,
                passed=False,
                has_not_done_marker=has_marker,
                output="",
                error=f"Execution failed: {exc}",
                exit_code=1,
                duration_ms=round(elapsed_ms, 2),
            )


__all__ = [
    "INCOMPLETE_MARKERS",
    "NOT_DONE_MARKER",
    "ExerciseRunner",
    "RunResult",
    "format_yaml_error",
]

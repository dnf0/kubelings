"""Exercise execution and evaluation runner for Kubelings."""

import os
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union

from kubelings.models import Exercise

NOT_DONE_MARKER = "I AM NOT DONE"


@dataclass
class RunResult:
    """Result of running and evaluating an exercise."""

    exercise: Exercise
    passed: bool
    has_not_done_marker: bool
    output: str
    error: Optional[str] = None
    exit_code: int = 0
    duration_ms: float = 0.0


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
        """Check if an exercise file contains the NOT_DONE marker."""
        p = Path(path)
        if not p.exists() or not p.is_file():
            return False
        try:
            content = p.read_text(encoding="utf-8", errors="replace")
            return NOT_DONE_MARKER in content
        except OSError:
            return False

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
            passed = (proc.returncode == 0) and not has_marker

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
            error_details = (
                f"Exercise timed out after {timeout_sec} seconds"
                + (f":\n{stderr_str}" if stderr_str else "")
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

"""Watcher engine for Kubelings continuous learning loop."""

import os
import threading
import time
from pathlib import Path
from typing import Dict, Optional, Union

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from kubelings.manifest import get_manifest
from kubelings.models import Exercise, Manifest
from kubelings.runner import ExerciseRunner, RunResult
from kubelings.ui import console as default_console, render_banner, render_result

try:
    from watchfiles import watch
except ImportError:
    watch = None  # type: ignore


VICTORY_BANNER = r"""
🎉 ☸ ════════════════════════════════════════════════════════════ ☸ 🎉
                 CONGRATULATIONS, KUBERNETES MASTER!
    You have completed all exercises in the Kubelings curriculum!
🎉 ☸ ════════════════════════════════════════════════════════════ ☸ 🎉
"""

IGNORED_DIRECTORIES = {
    ".git",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    "__pycache__",
    ".venv",
    "env",
    "venv",
    ".agents",
    ".agent-state",
    ".superpowers",
    ".roborev",
    "build",
    "dist",
}

VALID_EXTENSIONS = {".py", ".yaml", ".yml"}


def find_next_incomplete_exercise(
    manifest: Optional[Manifest] = None,
    runner: Optional[ExerciseRunner] = None,
    start_from: Optional[str] = None,
) -> Optional[Exercise]:
    """Find the first incomplete or failing exercise in the curriculum.

    Args:
        manifest: Manifest instance (defaults to global singleton).
        runner: ExerciseRunner instance (defaults to new ExerciseRunner).
        start_from: Optional exercise name to start searching from.

    Returns:
        The first Exercise that contains the NOT_DONE marker or fails execution,
        or None if all exercises are completed.
    """
    m = manifest or get_manifest()
    r = runner or ExerciseRunner()

    exercises = m.all_exercises
    start_idx = 0

    if start_from:
        for i, ex in enumerate(exercises):
            if ex.name == start_from or ex.path == start_from or ex.path.endswith(start_from):
                start_idx = i
                break

    for ex in exercises[start_idx:]:
        # Fast path: check marker first without subprocess spawn
        if r.check_marker(ex.file_path):
            return ex

        # Run exercise to verify logic and assertions
        result = r.run_exercise(ex)
        if not result.passed:
            return ex

    return None


class WatchEngine:
    """State machine and coordinator for continuous exercise watching."""

    def __init__(
        self,
        manifest: Optional[Manifest] = None,
        runner: Optional[ExerciseRunner] = None,
        console: Optional[Console] = None,
        start_exercise: Optional[str] = None,
    ) -> None:
        self.manifest = manifest or get_manifest()
        self.runner = runner or ExerciseRunner()
        self.console = console or default_console
        self.all_completed = False
        self.results_map: Dict[str, RunResult] = {}
        self.current_exercise = find_next_incomplete_exercise(
            self.manifest, self.runner, start_from=start_exercise
        )
        if self.current_exercise is None:
            self.all_completed = True

    @staticmethod
    def should_process_file(file_path: Union[str, Path]) -> bool:
        """Determine if a changed file path is relevant for exercise evaluation."""
        p = Path(file_path)
        parts = set(p.parts)
        if parts & IGNORED_DIRECTORIES:
            return False

        return p.suffix.lower() in VALID_EXTENSIONS

    def render_victory(self) -> None:
        """Render victory celebration when all curriculum exercises pass."""
        text = Text()
        text.append(VICTORY_BANNER.strip("\n"), style="bold green")
        text.append(
            "\n\nAll 13 chapters and 55 exercises have been verified successfully!\n",
            style="bold cyan",
        )
        text.append(
            "You now have deep practical knowledge of Kubernetes core workloads,\n", style="white"
        )
        text.append(
            "networking, storage, security, scheduling, CRDs, and troubleshooting.\n", style="white"
        )

        panel = Panel(
            text,
            title="[bold green]🏆 KUBELINGS CURRICULUM COMPLETED 🏆[/bold green]",
            border_style="green",
            padding=(1, 2),
        )
        self.console.print(panel)

    def evaluate_current(self) -> bool:
        """Evaluate the current exercise and advance if it passes.

        Returns:
            True if the exercise passed and advanced (or completed all), False otherwise.
        """
        if self.current_exercise is None:
            self.all_completed = True
            self.render_victory()
            return True

        result = self.runner.run_exercise(self.current_exercise)
        self.results_map[self.current_exercise.name] = result
        render_result(result, console=self.console)

        if result.passed:
            self.console.print(
                f"\n[bold green]🎉 Great job! Exercise '{self.current_exercise.name}' passed![/bold green]"
            )
            # Find next incomplete exercise
            next_ex = find_next_incomplete_exercise(self.manifest, self.runner)
            if next_ex is not None:
                self.current_exercise = next_ex
                self.all_completed = False
                self.console.print(
                    f"[bold cyan]☸ Advancing to next exercise:[/bold cyan] [bold white]{next_ex.name}[/bold white] ({next_ex.title})\n"
                )
                # Automatically run initial evaluation for next exercise
                next_res = self.runner.run_exercise(next_ex)
                self.results_map[next_ex.name] = next_res
                render_result(next_res, console=self.console)
                return True
            else:
                self.current_exercise = None
                self.all_completed = True
                self.render_victory()
                return True

        return False

    def on_file_changed(self, changed_path: Union[str, Path]) -> None:
        """Handle a detected filesystem modification."""
        if not self.should_process_file(changed_path):
            return

        self.console.clear()
        render_banner(console=self.console)
        self.console.print(
            f"[dim]⚡ Detected file change in: {Path(changed_path).name} at {time.strftime('%H:%M:%S')}[/dim]\n"
        )

        if self.current_exercise is None or self.all_completed:
            self.current_exercise = find_next_incomplete_exercise(self.manifest, self.runner)
            if self.current_exercise is None:
                self.all_completed = True
                self.render_victory()
                return
            else:
                self.all_completed = False

        self.evaluate_current()


def _fallback_poll_watch(
    engine: WatchEngine,
    watch_dir: Path,
    stop_event: Optional[threading.Event] = None,
    poll_interval: float = 0.5,
) -> None:
    """Fallback directory polling loop when watchfiles is not installed or unavailable."""
    mtimes: Dict[str, float] = {}

    def get_snapshot() -> Dict[str, float]:
        snapshot = {}
        try:
            for root, dirs, files in os.walk(str(watch_dir)):
                dirs[:] = [d for d in dirs if d not in IGNORED_DIRECTORIES]
                for f in files:
                    full_path = os.path.join(root, f)
                    if engine.should_process_file(full_path):
                        try:
                            snapshot[full_path] = os.path.getmtime(full_path)
                        except OSError:
                            pass
        except OSError:
            pass
        return snapshot

    mtimes = get_snapshot()

    while True:
        if stop_event is not None and stop_event.is_set():
            break

        time.sleep(poll_interval)
        current_snapshot = get_snapshot()

        changed_files = []
        for path, mtime in current_snapshot.items():
            if path not in mtimes or mtimes[path] != mtime:
                changed_files.append(path)

        mtimes = current_snapshot

        if changed_files:
            engine.on_file_changed(changed_files[0])


def run_watch_loop(
    manifest: Optional[Manifest] = None,
    runner: Optional[ExerciseRunner] = None,
    console: Optional[Console] = None,
    start_exercise: Optional[str] = None,
    watch_dir: Optional[Path] = None,
    stop_event: Optional[threading.Event] = None,
) -> None:
    """Run interactive watch loop monitoring exercise files and advancing on success.

    Args:
        manifest: Manifest instance (defaults to global singleton).
        runner: ExerciseRunner instance (defaults to new ExerciseRunner).
        console: Rich Console instance.
        start_exercise: Optional exercise name to start watching from.
        watch_dir: Directory to watch (defaults to exercises/ or current dir).
        stop_event: Threading event for controlled loop termination.
    """
    con = console or default_console
    engine = WatchEngine(
        manifest=manifest,
        runner=runner,
        console=con,
        start_exercise=start_exercise,
    )

    con.clear()
    render_banner(console=con)

    if engine.all_completed:
        engine.render_victory()
        return

    con.print(
        "[bold cyan]☸ Kubelings interactive watcher active.[/bold cyan] "
        "[dim]Modify exercise files to see instant feedback. Press Ctrl+C to exit.[/dim]\n"
    )

    # Initial evaluation of the first incomplete exercise
    engine.evaluate_current()

    target_dir = watch_dir or (
        Path.cwd() / "exercises" if (Path.cwd() / "exercises").exists() else Path.cwd()
    )

    try:
        if watch is not None:
            for changes in watch(str(target_dir), stop_event=stop_event, raise_interrupt=True):
                for change_type, path in changes:
                    if engine.should_process_file(path):
                        engine.on_file_changed(path)
                        break
        else:
            _fallback_poll_watch(engine, target_dir, stop_event=stop_event)
    except (KeyboardInterrupt, SystemExit):
        con.print("\n[yellow]☸ Kubelings watcher stopped. Keep practicing![/yellow]")
    except Exception as exc:
        con.print(f"\n[red]Watcher encountered an error: {exc}[/red]")

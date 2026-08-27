"""Command-line interface (CLI) commands and entry points for Kubelings."""

import json
from typing import Any, Optional

import click
import typer
from rich.panel import Panel
from rich.text import Text

from kubelings import __version__
from kubelings.cluster import ClusterDetector
from kubelings.manifest import get_exercise_by_name, get_manifest
from kubelings.runner import ExerciseRunner
from kubelings.ui import (
    console,
    render_banner,
    render_hint,
    render_progress_table,
    render_result,
)

# Compatibility fix for Click 8.4+ with Typer rich_utils make_metavar signature
_orig_make_metavar = click.core.Parameter.make_metavar


def _compat_make_metavar(self: click.core.Parameter, *args: Any, **kwargs: Any) -> str:
    if self.metavar is not None:
        return self.metavar
    try:
        return _orig_make_metavar(self, *args, **kwargs)
    except TypeError:
        try:
            return _orig_make_metavar(self)  # type: ignore
        except Exception:
            pass
    except Exception:
        pass
    try:
        metavar = self.type.get_metavar(param=self)  # type: ignore
    except Exception:
        metavar = None
    if metavar is None:
        metavar = getattr(self.type, "name", "TEXT").upper()
    if getattr(self, "nargs", 1) != 1:
        metavar += "..."
    return metavar


click.core.Parameter.make_metavar = _compat_make_metavar

app = typer.Typer(
    name="kubelings",
    help="Kubelings: Interactive hands-on Kubernetes curriculum and terminal learning engine.",
    no_args_is_help=True,
    add_completion=False,
)


def version_callback(value: bool) -> None:
    """Print the version string when --version is passed."""
    if value:
        console.print(
            f"[bold cyan]☸ Kubelings[/bold cyan] [bold magenta]v{__version__}[/bold magenta]"
        )
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        help="Show the Kubelings version and exit.",
        callback=version_callback,
        is_eager=True,
    ),
) -> None:
    """☸ Kubelings: Master Kubernetes from scratch through interactive exercises."""
    pass


@app.command("version")
def version_cmd() -> None:
    """Show the Kubelings version."""
    console.print(f"[bold cyan]☸ Kubelings[/bold cyan] [bold magenta]v{__version__}[/bold magenta]")


@app.command("list")
def list_exercises(
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output results in JSON format",
    ),
) -> None:
    """List all curriculum chapters, exercises, and descriptions."""
    manifest = get_manifest()

    if json_output:
        data = {
            "total_chapters": len(manifest.chapters),
            "total_exercises": len(manifest.all_exercises),
            "chapters": [
                {
                    "number": ch.number,
                    "name": ch.name,
                    "title": ch.title,
                    "description": ch.description,
                    "exercises": [
                        {
                            "name": ex.name,
                            "title": ex.title,
                            "path": ex.path,
                            "solution_path": str(ex.solution_path),
                            "chapter_name": ex.chapter_name,
                            "requires_cluster": ex.requires_cluster,
                            "has_not_done": ExerciseRunner.check_marker(ex.file_path),
                            "hints": ex.hints,
                        }
                        for ex in ch.exercises
                    ],
                }
                for ch in manifest.chapters
            ],
        }
        print(json.dumps(data, indent=2))
        return

    render_banner(console=console)

    for ch in manifest.chapters:
        console.print(
            f"[bold magenta]Chapter {ch.number:02d}: {ch.title}[/bold magenta] [dim]({ch.name})[/dim] — {ch.description}"
        )
        for ex in ch.exercises:
            cluster_badge = " [yellow]⎈ cluster[/yellow]" if ex.requires_cluster else ""
            console.print(
                f"  • [bold cyan]{ex.name:<16}[/bold cyan] : {ex.title} [dim]({ex.path})[/dim]{cluster_badge}"
            )
        console.print()

    console.print(
        f"[bold white]Total: {len(manifest.chapters)} Chapters, {len(manifest.all_exercises)} Exercises.[/bold white] "
        "[dim]Run 'kubelings watch' to start learning![/dim]\n"
    )


@app.command("hint")
def hint(
    exercise_name: str = typer.Argument(..., help="Name of exercise (e.g. 'pods01')"),
    hint_num: Optional[int] = typer.Option(
        None,
        "--hint-num",
        "-n",
        help="Specific 1-indexed hint number to display",
    ),
    index: Optional[int] = typer.Option(
        None,
        "--index",
        "-i",
        help="Specific 0-indexed hint index to display",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output results in JSON format",
    ),
) -> None:
    """Display progressive hints and architectural tips for an exercise."""
    ex = get_exercise_by_name(exercise_name)
    if not ex:
        if json_output:
            print(
                json.dumps(
                    {"error": f"Exercise '{exercise_name}' not found in curriculum."},
                    indent=2,
                )
            )
        else:
            console.print(
                f"[bold red]Error:[/bold red] Exercise '{exercise_name}' not found in curriculum."
            )
        raise typer.Exit(code=1)

    total_hints = len(ex.hints)
    if index is not None:
        hint_idx = index
    elif hint_num is not None:
        hint_idx = hint_num - 1
    else:
        hint_idx = 0

    if total_hints > 0:
        clamped_idx = min(max(0, hint_idx), total_hints - 1)
        hint_text = ex.hints[clamped_idx]
    else:
        clamped_idx = 0
        hint_text = f"No hints available for exercise '{ex.name}'."

    if json_output:
        data = {
            "exercise": ex.name,
            "hint_index": clamped_idx,
            "total_hints": total_hints,
            "hint": hint_text,
        }
        print(json.dumps(data, indent=2))
        return

    render_hint(ex, hint_index=hint_idx, console=console)


@app.command("run")
def run_exercise(
    exercise_name: str = typer.Argument(..., help="Name of exercise to execute (e.g. 'pods01')"),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output results in JSON format",
    ),
) -> None:
    """Execute and evaluate a single exercise."""
    ex = get_exercise_by_name(exercise_name)
    if not ex:
        if json_output:
            print(
                json.dumps(
                    {
                        "exercise": exercise_name,
                        "passed": False,
                        "has_not_done_marker": False,
                        "exit_code": 1,
                        "output": "",
                        "error": f"Exercise '{exercise_name}' not found in curriculum.",
                        "duration_ms": 0.0,
                        "hints_available": 0,
                    },
                    indent=2,
                )
            )
        else:
            console.print(
                f"[bold red]Error:[/bold red] Exercise '{exercise_name}' not found in curriculum."
            )
        raise typer.Exit(code=1)

    runner = ExerciseRunner()
    result = runner.run_exercise(ex)

    if json_output:
        data = {
            "exercise": ex.name,
            "passed": result.passed,
            "has_not_done_marker": result.has_not_done_marker,
            "exit_code": result.exit_code,
            "output": result.output,
            "error": result.error,
            "duration_ms": result.duration_ms,
            "hints_available": len(ex.hints),
        }
        print(json.dumps(data, indent=2))
        if not result.passed:
            raise typer.Exit(code=result.exit_code or 1)
        return

    render_result(result, console=console)

    if not result.passed:
        raise typer.Exit(code=result.exit_code or 1)


@app.command("verify")
def verify_all(
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output results in JSON format",
    ),
) -> None:
    """Verify progress and evaluation status across all curriculum exercises."""
    manifest = get_manifest()
    runner = ExerciseRunner()

    if json_output:
        results_list = []
        passed_count = 0
        in_progress_count = 0
        not_started_count = 0
        first_incomplete = None
        total_count = len(manifest.all_exercises)

        for ex in manifest.all_exercises:
            res = runner.run_exercise(ex)
            if res.passed:
                status = "completed"
                passed_count += 1
            elif first_incomplete is None:
                first_incomplete = ex.name
                status = "in_progress"
                in_progress_count += 1
            elif not res.has_not_done_marker:
                status = "in_progress"
                in_progress_count += 1
            else:
                status = "not_started"
                not_started_count += 1

            results_list.append(
                {
                    "name": ex.name,
                    "title": ex.title,
                    "path": ex.path,
                    "chapter": ex.chapter_name,
                    "status": status,
                    "passed": res.passed,
                    "has_not_done_marker": res.has_not_done_marker,
                    "duration_ms": res.duration_ms,
                }
            )

        pct = round((passed_count / total_count * 100.0), 2) if total_count > 0 else 0.0
        data = {
            "total": total_count,
            "completed": passed_count,
            "in_progress": in_progress_count,
            "not_started": not_started_count,
            "percentage": pct,
            "next_exercise": first_incomplete,
            "results": results_list,
        }
        print(json.dumps(data, indent=2))
        return

    with console.status("[bold cyan]Evaluating all curriculum exercises...[/bold cyan]"):
        results_map = {}
        passed_count = 0
        total_count = len(manifest.all_exercises)

        for ex in manifest.all_exercises:
            res = runner.run_exercise(ex)
            results_map[ex.name] = res
            if res.passed:
                passed_count += 1

    render_progress_table(manifest, results_map, console=console)

    if passed_count == total_count and total_count > 0:
        console.print(
            "\n[bold green]🎉 All curriculum exercises completed successfully![/bold green]\n"
        )
    else:
        console.print(
            f"\n[bold cyan]Progress: {passed_count}/{total_count} exercises completed.[/bold cyan] "
            "[dim]Use 'kubelings watch' to continue working.[/dim]\n"
        )


@app.command("cluster")
def cluster_status(
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output results in JSON format",
    ),
) -> None:
    """Check connectivity to local or remote Kubernetes clusters."""
    detector = ClusterDetector()
    status = detector.get_cluster_status(refresh=True)

    if json_output:
        is_available = bool(status.get("available", False))
        data = {
            "available": is_available,
            "context": status.get("context", "none"),
            "provider": status.get("provider", "none"),
            "cluster_mode": "live" if is_available else "offline",
        }
        print(json.dumps(data, indent=2))
        return

    text = Text()
    if status.get("available"):
        text.append("✓ Connected to active Kubernetes cluster!\n\n", style="bold green")
        text.append(f"Context:  [bold white]{status.get('context')}[/bold white]\n", style="cyan")
        text.append(
            f"Provider: [bold white]{status.get('provider')}[/bold white]\n\n", style="cyan"
        )
        text.append(
            "Live cluster testing and ephemeral namespace provisioning are available for exercises.",
            style="dim white",
        )
        panel = Panel(
            text,
            title="[bold green]☸ Kubernetes Cluster Status: CONNECTED[/bold green]",
            border_style="green",
            padding=(1, 2),
        )
    else:
        text.append("No active Kubernetes cluster detected.\n\n", style="bold yellow")
        text.append(
            "Kubelings is operating in [bold white]Offline Validation Mode[/bold white].\n",
            style="yellow",
        )
        text.append(
            "All core manifest, schema, and API exercises run instantly using the offline engine.\n\n",
            style="dim white",
        )
        text.append(
            "Optional: Start a local cluster with [cyan]kind create cluster[/cyan] or [cyan]minikube start[/cyan] for live tests.",
            style="dim italic white",
        )
        panel = Panel(
            text,
            title="[bold yellow]☸ Kubernetes Cluster Status: OFFLINE MODE[/bold yellow]",
            border_style="yellow",
            padding=(1, 2),
        )

    console.print(panel)


@app.command("watch")
def watch_mode(
    start: Optional[str] = typer.Option(
        None,
        "--start",
        "-s",
        help="Exercise name to start watching from (e.g. 'pods01')",
    ),
) -> None:
    """Launch interactive watcher loop to monitor edits and advance automatically."""
    from kubelings.watcher import run_watch_loop

    run_watch_loop(start_exercise=start)


@app.command("test")
def test_solutions(
    exercise: Optional[str] = typer.Option(
        None, "--exercise", "-e", help="Specific exercise name or path to test."
    ),
    chapter: Optional[str] = typer.Option(
        None, "--chapter", "-c", help="Specific chapter name to test (e.g. '01_pods')."
    ),
    max_exercises: Optional[int] = typer.Option(
        None, "--max-exercises", "-m", help="Maximum number of exercises to evaluate."
    ),
) -> None:
    """Verify reference solutions for curriculum exercises."""
    manifest = get_manifest()
    runner = ExerciseRunner()

    target_exercises = manifest.all_exercises

    if exercise:
        matched = [
            ex for ex in target_exercises if ex.name == exercise or ex.path.endswith(exercise)
        ]
        if not matched:
            console.print(f"[bold red]Exercise '{exercise}' not found in curriculum.[/bold red]")
            raise typer.Exit(code=1)
        target_exercises = matched

    if chapter:
        matched = [
            ex
            for ex in target_exercises
            if ex.chapter_name == chapter or chapter in ex.chapter_name
        ]
        if not matched:
            console.print(f"[bold red]Chapter '{chapter}' not found in curriculum.[/bold red]")
            raise typer.Exit(code=1)
        target_exercises = matched

    if max_exercises is not None:
        target_exercises = target_exercises[:max_exercises]

    if chapter:
        console.print(f"[bold cyan]Testing Chapter: {chapter}[/bold cyan]")
    else:
        console.print("[bold cyan]Testing Reference Solutions...[/bold cyan]")
    results_map = {}
    passed_count = 0
    total_count = len(target_exercises)

    for ex in target_exercises:
        sol_ex = get_exercise_by_name(ex.name)
        if sol_ex:
            sol_path = sol_ex.solution_path
            if sol_path.exists():
                sol_obj = type(sol_ex)(
                    name=sol_ex.name,
                    title=sol_ex.title,
                    path=str(sol_path),
                    chapter_name=sol_ex.chapter_name,
                    hints=sol_ex.hints,
                    requires_cluster=sol_ex.requires_cluster,
                )
                res = runner.run_exercise(sol_obj)
            else:
                res = runner.run_exercise(sol_ex)
        else:
            res = runner.run_exercise(ex)

        results_map[ex.name] = res
        if res.passed:
            passed_count += 1
            console.print(
                f"  [bold green]✓[/bold green] {ex.name} ({ex.title}) - Passed ({res.duration_ms:.1f}ms)"
            )
        else:
            console.print(f"  [bold red]✗[/bold red] {ex.name} ({ex.title}) - Failed")

    console.print(
        f"\n[bold cyan]Solution Verification: {passed_count}/{total_count} passing.[/bold cyan]\n"
    )

    if passed_count < total_count:
        raise typer.Exit(code=1)


@app.command("init")
def init_cmd(
    directory: Optional[str] = typer.Option(
        None,
        "--dir",
        "-d",
        help="Target directory to initialize exercises in (defaults to current directory).",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Overwrite existing files in target exercises directory.",
    ),
) -> None:
    """Initialize curriculum exercises directory in the current workspace."""
    from pathlib import Path

    from kubelings.scaffold import init_workspace

    target_path = Path(directory) if directory else Path.cwd()
    try:
        init_workspace(target_path, force=force)
        console.print(
            f"[bold green]✓ Initialized exercises in:[/bold green] [bold cyan]{target_path / 'exercises'}[/bold cyan]\n"
            "[dim]Run 'kubelings watch' to begin learning Kubernetes![/dim]"
        )
    except FileExistsError as err:
        console.print(f"[bold yellow]Warning:[/bold yellow] {err}")
        raise typer.Exit(code=1)
    except Exception as err:
        console.print(f"[bold red]Error initializing workspace:[/bold red] {err}")
        raise typer.Exit(code=1)


@app.command("reset")
def reset_cmd(
    exercise_name: str = typer.Argument(..., help="Name of exercise to reset (e.g. 'pods01')"),
) -> None:
    """Reset a specific exercise in the current workspace to its initial starter state."""
    from kubelings.scaffold import reset_exercise

    try:
        reset_file = reset_exercise(exercise_name)
        console.print(
            f"[bold green]✓ Reset exercise:[/bold green] [bold cyan]{exercise_name}[/bold cyan] "
            f"[dim]({reset_file})[/dim]"
        )
    except (KeyError, FileNotFoundError) as err:
        console.print(f"[bold red]Error:[/bold red] {err}")
        raise typer.Exit(code=1)
    except Exception as err:
        console.print(f"[bold red]Error resetting exercise:[/bold red] {err}")
        raise typer.Exit(code=1)


@app.command("tree")
def tree_cmd(
    target: str = typer.Argument(
        "pods01", help="Exercise name, file path, or YAML manifest to visualize"
    ),
) -> None:
    """Render architectural relationship topology tree for Kubernetes resources."""
    from pathlib import Path

    import yaml

    from kubelings.topology import render_topology_tree

    ex = get_exercise_by_name(target)
    manifests = []

    if ex:
        # Check solution first if exists, else exercise
        target_path = ex.solution_path if ex.solution_path.exists() else ex.file_path
        if target_path.exists():
            content = target_path.read_text(encoding="utf-8")
            # Extract YAML blocks from docstring or inline YAML
            try:
                # First try direct YAML parse
                manifests = list(yaml.safe_load_all(content))
            except Exception:
                pass
            if not manifests or not any(isinstance(m, dict) for m in manifests):
                # Look for YAML inside python multiline strings
                import re

                yaml_blocks = re.findall(r'"""(.*?)"""', content, re.DOTALL)
                for block in yaml_blocks:
                    try:
                        docs = list(yaml.safe_load_all(block.strip()))
                        manifests.extend([d for d in docs if isinstance(d, dict) and "kind" in d])
                    except Exception:
                        pass
    else:
        file_path = Path(target)
        if file_path.exists():
            content = file_path.read_text(encoding="utf-8")
            try:
                manifests = [d for d in yaml.safe_load_all(content) if isinstance(d, dict)]
            except Exception as e:
                console.print(f"[bold red]Error parsing YAML:[/bold red] {e}")
                raise typer.Exit(code=1)
        else:
            console.print(f"[bold red]Target not found:[/bold red] {target}")
            raise typer.Exit(code=1)

    if not manifests:
        # Provide sample manifest fallback
        manifests = [
            {
                "apiVersion": "v1",
                "kind": "Pod",
                "metadata": {"name": target, "namespace": "default"},
            }
        ]

    render_topology_tree(manifests, console=console)


@app.command("lint")
def lint_cmd(
    target: str = typer.Argument(
        ..., help="Path to Kubernetes YAML/JSON manifest or exercise file to lint"
    ),
) -> None:
    """Evaluate Kubernetes manifests against security, reliability, and schema rules."""
    from pathlib import Path

    from kubelings.linter import LintSeverity, ManifestLinter, render_lint_table

    file_path = Path(target)
    if not file_path.exists():
        console.print(f"[bold red]Error: File not found:[/bold red] {target}")
        raise typer.Exit(code=1)

    linter = ManifestLinter()
    diagnostics = linter.lint_file(file_path)

    # If it's a python exercise file, extract manifests from docstrings / code
    if file_path.suffix == ".py" and not diagnostics:
        import re

        import yaml

        content = file_path.read_text(encoding="utf-8")
        yaml_blocks = re.findall(r'"""(.*?)"""', content, re.DOTALL)
        for block in yaml_blocks:
            try:
                for doc in yaml.safe_load_all(block.strip()):
                    if isinstance(doc, dict) and "kind" in doc:
                        diagnostics.extend(linter.lint_manifest(doc, file_path=str(file_path)))
            except Exception:
                pass

    render_lint_table(diagnostics, console=console)
    has_errors = any(d.severity == LintSeverity.ERROR for d in diagnostics)
    if has_errors:
        raise typer.Exit(code=1)


@app.command("tui")
@app.command("dashboard")
def tui_cmd() -> None:
    """Launch full-screen interactive terminal TUI dashboard."""
    from kubelings.tui import TuiApp

    app_instance = TuiApp(console=console)
    layout = app_instance.generate_layout()
    console.print(layout)


@app.command("tour")
def onboarding_tour(
    step: Optional[int] = typer.Option(
        None,
        "--step",
        "-s",
        help="Jump directly to a specific tour step (1-5).",
    ),
    non_interactive: bool = typer.Option(
        False,
        "--non-interactive",
        help="Execute tour without waiting for interactive input prompts.",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output tour step metadata in JSON format.",
    ),
) -> None:
    """Take the interactive 5-step onboarding tour for new learners."""
    from kubelings.tour import OnboardingTour

    tour = OnboardingTour(console=console)

    if json_output:
        print(json.dumps(tour.to_json(), indent=2))
        return

    interactive = not non_interactive
    if step is not None:
        try:
            tour.run_step(step, interactive=interactive)
        except ValueError as err:
            console.print(f"[bold red]Error:[/bold red] {err}")
            raise typer.Exit(code=1)
    else:
        tour.run_all(interactive=interactive)


if __name__ == "__main__":
    app()

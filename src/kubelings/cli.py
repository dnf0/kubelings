"""Command-line interface (CLI) commands and entry points for Kubelings."""

from typing import Optional

import click
import typer
from rich.panel import Panel
from rich.text import Text

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


def _compat_make_metavar(self: click.core.Parameter, ctx: Optional[click.Context] = None) -> str:
    if ctx is None:
        if self.metavar is not None:
            return self.metavar
        try:
            metavar = self.type.get_metavar(param=self, ctx=None)  # type: ignore
        except Exception:
            metavar = None
        if metavar is None:
            metavar = self.type.name.upper()
        if self.nargs != 1:
            metavar += "..."
        return metavar
    return _orig_make_metavar(self, ctx)


click.core.Parameter.make_metavar = _compat_make_metavar

__version__ = "0.1.0"

app = typer.Typer(
    name="kubelings",
    help="Kubelings: Interactive hands-on Kubernetes curriculum and terminal learning engine.",
    no_args_is_help=True,
    add_completion=False,
)


def version_callback(value: bool) -> None:
    """Print the version string when --version is passed."""
    if value:
        console.print(f"[bold cyan]☸ Kubelings[/bold cyan] [bold magenta]v{__version__}[/bold magenta]")
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
def list_exercises() -> None:
    """List all curriculum chapters, exercises, and descriptions."""
    render_banner(console=console)
    manifest = get_manifest()

    for ch in manifest.chapters:
        console.print(
            f"[bold magenta]Chapter {ch.number:02d}: {ch.title}[/bold magenta] [dim]({ch.name})[/dim] — {ch.description}"
        )
        for ex in ch.exercises:
            cluster_badge = " [yellow]⎈ cluster[/yellow]" if ex.requires_cluster else ""
            console.print(f"  • [bold cyan]{ex.name:<16}[/bold cyan] : {ex.title} [dim]({ex.path})[/dim]{cluster_badge}")
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
) -> None:
    """Display progressive hints and architectural tips for an exercise."""
    ex = get_exercise_by_name(exercise_name)
    if not ex:
        console.print(f"[bold red]Error:[/bold red] Exercise '{exercise_name}' not found in curriculum.")
        raise typer.Exit(code=1)

    hint_idx = (hint_num - 1) if hint_num is not None else 0
    render_hint(ex, hint_index=hint_idx, console=console)


@app.command("run")
def run_exercise(
    exercise_name: str = typer.Argument(..., help="Name of exercise to execute (e.g. 'pods01')"),
) -> None:
    """Execute and evaluate a single exercise."""
    ex = get_exercise_by_name(exercise_name)
    if not ex:
        console.print(f"[bold red]Error:[/bold red] Exercise '{exercise_name}' not found in curriculum.")
        raise typer.Exit(code=1)

    runner = ExerciseRunner()
    result = runner.run_exercise(ex)
    render_result(result, console=console)

    if not result.passed:
        raise typer.Exit(code=result.exit_code or 1)


@app.command("verify")
def verify_all() -> None:
    """Verify progress and evaluation status across all curriculum exercises."""
    manifest = get_manifest()
    runner = ExerciseRunner()

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
        console.print("\n[bold green]🎉 All curriculum exercises completed successfully![/bold green]\n")
    else:
        console.print(
            f"\n[bold cyan]Progress: {passed_count}/{total_count} exercises completed.[/bold cyan] "
            "[dim]Use 'kubelings watch' to continue working.[/dim]\n"
        )


@app.command("cluster")
def cluster_status() -> None:
    """Check connectivity to local or remote Kubernetes clusters."""
    detector = ClusterDetector()
    status = detector.get_cluster_status(refresh=True)

    text = Text()
    if status.get("available"):
        text.append("✓ Connected to active Kubernetes cluster!\n\n", style="bold green")
        text.append(f"Context:  [bold white]{status.get('context')}[/bold white]\n", style="cyan")
        text.append(f"Provider: [bold white]{status.get('provider')}[/bold white]\n\n", style="cyan")
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
        text.append("Kubelings is operating in [bold white]Offline Validation Mode[/bold white].\n", style="yellow")
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
def test_solutions() -> None:
    """Verify reference solutions for all curriculum exercises."""
    manifest = get_manifest()
    runner = ExerciseRunner()

    with console.status("[bold cyan]Testing reference solutions...[/bold cyan]"):
        results_map = {}
        passed_count = 0
        total_count = len(manifest.all_exercises)

        for ex in manifest.all_exercises:
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
                    results_map[ex.name] = res
                    if res.passed:
                        passed_count += 1
                else:
                    results_map[ex.name] = ExerciseRunner().run_exercise(sol_ex)

    render_progress_table(manifest, results_map, console=console)
    console.print(f"\n[bold cyan]Solution Verification: {passed_count}/{total_count} passing.[/bold cyan]\n")


if __name__ == "__main__":
    app()

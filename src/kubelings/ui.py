"""Rich Terminal UI formatting and diagnostics for Kubelings."""

from typing import Dict, Optional

from rich.console import Console, Group
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text
from rich.theme import Theme

from kubelings.models import Exercise, Manifest
from kubelings.runner import RunResult

KUBELINGS_THEME = Theme(
    {
        "k8s.blue": "#326ce5",
        "k8s.cyan": "#00d4fe",
        "k8s.magenta": "#e040fb",
        "status.pass": "bold green",
        "status.progress": "bold yellow",
        "status.fail": "bold red",
        "status.unstarted": "dim white",
    }
)

console = Console(theme=KUBELINGS_THEME)

BANNER_ART = r"""
     _  __     _          _ _                 
    | |/ /   _| |__   ___| (_)_ __   __ _ ___ 
 ☸  | ' / | | | '_ \ / _ \ | | '_ \ / _` / __|  ☸
    | . \ |_| | |_) |  __/ | | | | | (_| \__ \
    |_|\_\__,_|_.__/ \___|_|_|_| |_|\__, |___/
                                    |___/     
"""


def get_console() -> Console:
    """Return the default configured Rich Console instance."""
    return console


def render_banner(console: Optional[Console] = None) -> Panel:
    """Render attractive Kubernetes cyan/magenta banner with ASCII wheel icon."""
    banner_text = Text()
    banner_text.append(BANNER_ART.strip("\n"), style="bold cyan")
    banner_text.append("\n\n")
    banner_text.append("☸ Kubelings ", style="bold #00d4fe")
    banner_text.append("— ", style="bold white")
    banner_text.append("Interactive Kubernetes Learning Environment\n", style="bold magenta")
    banner_text.append(
        "Master Kubernetes concepts through hands-on Python and manifest exercises.",
        style="italic dim white",
    )

    panel = Panel(
        banner_text,
        border_style="cyan",
        padding=(1, 2),
        subtitle="[bold #e040fb]v0.1.0[/bold #e040fb] • [dim]Type 'kubelings --help' for commands[/dim]",
        subtitle_align="right",
    )

    if console is not None:
        console.print(panel)
    return panel


def render_result(result: RunResult, console: Optional[Console] = None) -> Panel:
    """Render exercise evaluation result with diagnostics and color-coded status."""
    ex = result.exercise
    renderables = []

    if result.passed:
        title_text = f"[bold green]✓ PASSED[/bold green]: [bold white]{ex.name}[/bold white] — {ex.title}"
        border_style = "green"

        summary = Text()
        summary.append("✓ Exercise passed successfully! ", style="bold green")
        summary.append(f"({result.duration_ms:.1f}ms)\n", style="dim green")
        if result.output.strip():
            summary.append("\nOutput:\n", style="bold")
            summary.append(result.output.strip(), style="dim white")
        renderables.append(summary)
        subtitle = "[bold green]Ready for next exercise[/bold green]"

    elif result.has_not_done_marker:
        title_text = f"[bold yellow]⏳ IN PROGRESS[/bold yellow]: [bold white]{ex.name}[/bold white] — {ex.title}"
        border_style = "yellow"

        summary = Text()
        summary.append("The exercise file contains the ", style="yellow")
        summary.append("'# I AM NOT DONE'", style="bold yellow underline")
        summary.append(" marker.\n\n", style="yellow")
        summary.append(f"Edit the file at: [cyan]{ex.path}[/cyan]\n", style="dim")
        summary.append(
            "When you have finished the exercise, remove the marker to verify your solution.",
            style="italic yellow",
        )

        if result.output.strip():
            summary.append(f"\n\nOutput ({result.duration_ms:.1f}ms):\n", style="bold")
            summary.append(result.output.strip(), style="dim white")

        renderables.append(summary)
        subtitle = "[yellow]Remove '# I AM NOT DONE' when ready[/yellow]"

    else:
        title_text = f"[bold red]✗ FAILED[/bold red]: [bold white]{ex.name}[/bold white] — {ex.title}"
        border_style = "red"

        summary = Text()
        summary.append(
            f"Exercise execution failed with exit code {result.exit_code} ",
            style="bold red",
        )
        summary.append(f"({result.duration_ms:.1f}ms)\n\n", style="dim red")
        renderables.append(summary)

        if result.error:
            # Highlight traceback / error diagnostics
            syntax_err = Syntax(
                result.error.strip(),
                "python",
                theme="monokai",
                line_numbers=False,
                word_wrap=True,
            )
            renderables.append(
                Panel(
                    syntax_err,
                    title="[bold red]Error Diagnostics[/bold red]",
                    border_style="red",
                    padding=(0, 1),
                )
            )

        if result.output.strip():
            renderables.append(
                Panel(
                    result.output.strip(),
                    title="[dim]Standard Output[/dim]",
                    border_style="dim",
                    padding=(0, 1),
                )
            )

        subtitle = "[bold red]Fix the errors above and re-run[/bold red]"

    panel = Panel(
        Group(*renderables),
        title=title_text,
        border_style=border_style,
        padding=(1, 2),
        subtitle=subtitle,
        subtitle_align="right",
    )

    if console is not None:
        console.print(panel)
    return panel


def render_hint(
    exercise: Exercise,
    hint_index: int = 0,
    console: Optional[Console] = None,
) -> Panel:
    """Render progressive numbered hints in a styled yellow panel."""
    if not exercise.hints:
        content = Text(f"No hints available for exercise '{exercise.name}'.", style="italic yellow")
        panel = Panel(
            content,
            title=f"[bold yellow]💡 Hint[/bold yellow] — {exercise.name}",
            border_style="yellow",
            padding=(1, 2),
        )
        if console is not None:
            console.print(panel)
        return panel

    total_hints = len(exercise.hints)
    idx = min(max(0, hint_index), total_hints - 1)
    hint_text = exercise.hints[idx]

    content = Text()
    content.append(f"Hint {idx + 1} of {total_hints}:\n\n", style="bold yellow")
    content.append(f"{hint_text}\n", style="white")

    if idx + 1 < total_hints:
        content.append(
            f"\n({total_hints - (idx + 1)} more hint(s) available — use --hint again for more help)",
            style="dim italic yellow",
        )
    else:
        content.append(
            "\n(This is the final hint for this exercise)",
            style="dim italic yellow",
        )

    panel = Panel(
        content,
        title=f"[bold yellow]💡 Hint {idx + 1}/{total_hints}[/bold yellow] — {exercise.name}: {exercise.title}",
        border_style="yellow",
        padding=(1, 2),
    )

    if console is not None:
        console.print(panel)
    return panel


def render_progress_table(
    manifest: Manifest,
    results_map: Dict[str, RunResult],
    console: Optional[Console] = None,
) -> Table:
    """Render curriculum progress summary table with chapters, exercises, and status badges."""
    table = Table(
        title="☸ [bold cyan]Kubelings Curriculum Progress[/bold cyan]",
        title_justify="center",
        show_header=True,
        header_style="bold magenta",
        border_style="cyan",
        expand=True,
    )

    table.add_column("Chapter", style="cyan", ratio=2)
    table.add_column("Exercise", style="bold white", ratio=2)
    table.add_column("Title", style="white", ratio=4)
    table.add_column("Status", justify="center", ratio=2)
    table.add_column("Duration", justify="right", style="dim", ratio=1)

    total_exercises = len(manifest.all_exercises)
    done_count = 0
    in_progress_count = 0
    failed_count = 0

    for ch_idx, chapter in enumerate(manifest.chapters):
        for ex_idx, exercise in enumerate(chapter.exercises):
            chapter_col = f"{chapter.number:02d}. {chapter.title}" if ex_idx == 0 else ""

            if exercise.name in results_map:
                res = results_map[exercise.name]
                if res.passed:
                    done_count += 1
                    status_badge = "[bold green]DONE ✓[/bold green]"
                    duration_str = f"{res.duration_ms:.1f}ms"
                elif res.has_not_done_marker:
                    in_progress_count += 1
                    status_badge = "[bold yellow]IN PROGRESS ⏳[/bold yellow]"
                    duration_str = f"{res.duration_ms:.1f}ms"
                else:
                    failed_count += 1
                    status_badge = "[bold red]FAILED ✗[/bold red]"
                    duration_str = f"{res.duration_ms:.1f}ms"
            else:
                status_badge = "[dim]NOT DONE ○[/dim]"
                duration_str = "-"

            table.add_row(
                chapter_col,
                exercise.name,
                exercise.title,
                status_badge,
                duration_str,
            )

        if ch_idx < len(manifest.chapters) - 1:
            table.add_section()

    pct = (done_count / total_exercises * 100.0) if total_exercises > 0 else 0.0
    table.caption = (
        f"[bold white]Total: {total_exercises}[/bold white] | "
        f"[bold green]Completed: {done_count} ({pct:.1f}%)[/bold green] | "
        f"[bold yellow]In Progress: {in_progress_count}[/bold yellow] | "
        f"[bold red]Failed: {failed_count}[/bold red]"
    )

    if console is not None:
        console.print(table)
    return table

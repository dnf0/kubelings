"""Generate rich terminal demo SVG asset for README."""

from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from kubelings.manifest import get_exercise_by_name
from kubelings.runner import RunResult
from kubelings.ui import render_banner, render_result, render_watcher_prompt


def generate_svg() -> Path:
    console = Console(record=True, width=92, force_terminal=True, color_system="truecolor")

    # Render top banner
    render_banner(console=console)

    # Render active status
    console.print(
        "[bold cyan]☸ Kubelings interactive watcher active.[/bold cyan] "
        "[dim]Modify exercise files to see instant feedback.[/dim]\n"
    )

    # Render exercise run result
    ex = get_exercise_by_name("pods01")
    assert ex is not None

    res = RunResult(
        exercise=ex,
        passed=True,
        has_not_done_marker=False,
        output="✓ Pod manifest syntax valid!\n✓ Containers specification verified.\n✓ Image set to 'nginx:alpine' on port 80.",
        duration_ms=18.4,
    )

    render_result(res, console=console)

    console.print(
        f"\n[bold green]🎉 Great job! Exercise '{ex.name}' passed![/bold green]\n"
        f"[bold cyan]☸ Advancing to next exercise:[/bold cyan] [bold white]pods02[/bold white] (Multi-Container Pods & Sidecar Pattern)"
    )

    render_watcher_prompt(console=console)

    assets_dir = Path("assets")
    assets_dir.mkdir(exist_ok=True)
    svg_path = assets_dir / "demo.svg"

    svg_content = console.export_svg(title="Kubelings Terminal Session")
    svg_path.write_text(svg_content, encoding="utf-8")
    print(f"Generated demo SVG at: {svg_path.resolve()} ({len(svg_content)} bytes)")
    return svg_path


if __name__ == "__main__":
    generate_svg()

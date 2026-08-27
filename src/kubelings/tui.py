"""Interactive Terminal TUI Dashboard for Kubelings."""

from dataclasses import dataclass, field
from typing import Dict, Optional

from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.syntax import Syntax
from rich.text import Text
from rich.tree import Tree

from kubelings.manifest import Manifest, get_manifest
from kubelings.models import Exercise
from kubelings.runner import ExerciseRunner, RunResult
from kubelings.ui import get_console


@dataclass
class TuiState:
    """Maintains active selection, results, and hints in the TUI session."""

    manifest: Manifest
    selected_exercise_index: int = 0
    active_hint_index: int = 0
    results: Dict[str, RunResult] = field(default_factory=dict)

    @property
    def all_exercises(self):
        return self.manifest.all_exercises

    @property
    def current_exercise(self) -> Exercise:
        return self.all_exercises[self.selected_exercise_index]

    def move_down(self) -> None:
        if self.selected_exercise_index < len(self.all_exercises) - 1:
            self.selected_exercise_index += 1
            self.active_hint_index = 0

    def move_up(self) -> None:
        if self.selected_exercise_index > 0:
            self.selected_exercise_index -= 1
            self.active_hint_index = 0

    def reveal_next_hint(self) -> int:
        max_hints = len(self.current_exercise.hints)
        if max_hints > 0:
            self.active_hint_index = min(self.active_hint_index + 1, max_hints)
        return self.active_hint_index


class TuiApp:
    """Full-screen interactive terminal dashboard application."""

    def __init__(
        self,
        manifest: Optional[Manifest] = None,
        runner: Optional[ExerciseRunner] = None,
        console: Optional[Console] = None,
    ) -> None:
        self.manifest = manifest or get_manifest()
        self.runner = runner or ExerciseRunner()
        self.console = console or get_console()
        self.state = TuiState(manifest=self.manifest)

    def generate_layout(self) -> Layout:
        """Construct the split-pane Rich Layout."""
        layout = Layout()

        # Split vertical: Header, Body, Footer
        layout.split(
            Layout(name="header", size=3),
            Layout(name="body", ratio=1),
            Layout(name="footer", size=3),
        )

        # Split Body horizontally: Sidebar (left) and Content (right)
        layout["body"].split_row(
            Layout(name="sidebar", ratio=1),
            Layout(name="content", ratio=2),
        )

        # Split Content vertically: Code preview (top) and Diagnostics (bottom)
        layout["content"].split(
            Layout(name="code_viewer", ratio=1),
            Layout(name="diagnostics", ratio=1),
        )

        layout["header"].update(self._render_header())
        layout["sidebar"].update(self._render_sidebar())
        layout["code_viewer"].update(self._render_code_viewer())
        layout["diagnostics"].update(self._render_diagnostics())
        layout["footer"].update(self._render_footer())

        return layout

    def _render_header(self) -> Panel:
        text = Text()
        text.append("☸ KUBELINGS TUI DASHBOARD", style="bold cyan")
        text.append(" • Interactive Kubernetes Curriculum Explorer", style="dim")
        text.append(
            f" • Exercise {self.state.selected_exercise_index + 1}/{len(self.state.all_exercises)}",
            style="bold yellow",
        )
        return Panel(text, border_style="cyan")

    def _render_sidebar(self) -> Panel:
        tree = Tree("[bold cyan]📚 Curriculum Chapters[/bold cyan]")
        current_ex = self.state.current_exercise

        for ch in self.manifest.chapters:
            ch_node = tree.add(f"[bold white]{ch.number:02d}. {ch.title}[/bold white]")
            for ex in ch.exercises:
                is_selected = ex.name == current_ex.name
                res = self.state.results.get(ex.name)

                status_icon = "⭕"
                if res:
                    status_icon = "✅" if res.passed else "❌"

                if is_selected:
                    ch_node.add(
                        f"[bold cyan]➔ {status_icon} {ex.name}[/bold cyan] [bold white]({ex.title})[/bold white]"
                    )
                else:
                    ch_node.add(f"[dim]{status_icon} {ex.name} ({ex.title})[/dim]")

        return Panel(tree, title="[bold cyan]Syllabus[/bold cyan]", border_style="cyan")

    def _render_code_viewer(self) -> Panel:
        ex = self.state.current_exercise
        file_path = ex.file_path

        code_text = "# Exercise file not found"
        if file_path.exists():
            code_text = file_path.read_text(encoding="utf-8")

        syntax = Syntax(
            code_text,
            "python",
            theme="monokai",
            line_numbers=True,
            word_wrap=True,
        )

        return Panel(
            syntax,
            title=f"[bold cyan]Source: {ex.path}[/bold cyan]",
            border_style="cyan",
        )

    def _render_diagnostics(self) -> Panel:
        ex = self.state.current_exercise
        res = self.state.results.get(ex.name)

        text = Text()
        text.append(f"Exercise: {ex.name} — {ex.title}\n", style="bold white")
        text.append(f"Chapter:  {ex.chapter_name}\n\n", style="dim")

        if res:
            if res.passed:
                text.append("✓ Status: PASSED\n", style="bold green")
            else:
                text.append("✗ Status: FAILING / INCOMPLETE\n", style="bold red")
            if res.output:
                text.append(f"\nExecution Output:\n{res.output}\n", style="cyan")
            if res.error:
                text.append(f"\nErrors:\n{res.error}\n", style="red")
        else:
            text.append("Press [Enter] to run and evaluate this exercise.\n", style="dim italic")

        # Hints section
        if self.state.active_hint_index > 0:
            text.append(
                f"\n💡 Hint Tier {self.state.active_hint_index}/{len(ex.hints)}:\n",
                style="bold yellow",
            )
            for i in range(self.state.active_hint_index):
                text.append(f"  • {ex.hints[i]}\n", style="yellow")
        elif ex.hints:
            text.append(
                "\n💡 Hints available: Press 'h' to reveal progressive hints.\n", style="dim yellow"
            )

        return Panel(text, title="[bold cyan]Evaluation & Hints[/bold cyan]", border_style="cyan")

    def _render_footer(self) -> Panel:
        text = Text()
        text.append(" [↑/k] Up  ", style="bold cyan")
        text.append(" [↓/j] Down  ", style="bold cyan")
        text.append(" [Enter] Run  ", style="bold green")
        text.append(" [h] Hint  ", style="bold yellow")
        text.append(" [r] Reset  ", style="bold magenta")
        text.append(" [q/Esc] Quit ", style="bold red")
        return Panel(text, border_style="cyan")

    def run_selected_exercise(self) -> RunResult:
        """Run the currently highlighted exercise."""
        ex = self.state.current_exercise
        result = self.runner.run_exercise(ex)
        self.state.results[ex.name] = result
        return result

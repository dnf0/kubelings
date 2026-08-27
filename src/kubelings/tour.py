"""Interactive and non-interactive onboarding tour engine for Kubelings."""

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from rich.console import Console, Group, RenderableType
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text

from kubelings.cluster import ClusterDetector
from kubelings.manifest import get_exercise_by_name
from kubelings.models import Exercise
from kubelings.runner import ExerciseRunner
from kubelings.ui import BANNER_ART, get_console


@dataclass
class TourStep:
    """Represents a discrete step in the onboarding tour."""

    step_num: int
    name: str
    title: str
    description: str


@dataclass
class TourStepResult:
    """Result of executing an onboarding tour step."""

    step_num: int
    name: str
    title: str
    success: bool
    details: Dict[str, Any] = field(default_factory=dict)
    message: str = ""


class OnboardingTour:
    """5-step onboarding tour engine guiding new learners through Kubelings."""

    def __init__(
        self,
        console: Optional[Console] = None,
        cluster_detector: Optional[ClusterDetector] = None,
        runner: Optional[ExerciseRunner] = None,
    ) -> None:
        self.console = console or get_console()
        self.cluster_detector = cluster_detector or ClusterDetector()
        self.runner = runner or ExerciseRunner()
        self.steps: List[TourStep] = [
            TourStep(
                step_num=1,
                name="welcome",
                title="Welcome & Pedagogical Philosophy",
                description="Active debugging, sub-30ms feedback loop, and test-driven mastery.",
            ),
            TourStep(
                step_num=2,
                name="environment",
                title="Environment & Cluster Diagnostics",
                description="Python runtime check, workspace integrity, and Kubernetes cluster probe.",
            ),
            TourStep(
                step_num=3,
                name="workflow",
                title="Inner Loop Workflow & Interactive Hotkeys",
                description="Inner loop, live reload watcher, and keyboard shortcuts.",
            ),
            TourStep(
                step_num=4,
                name="guided_exercise",
                title="Guided Walkthrough: First Exercise (pods01)",
                description="Guided inspection of pods01, failure diagnostics, and solution diff.",
            ),
            TourStep(
                step_num=5,
                name="tooling",
                title="IDE Tooling, Hints & Next Steps",
                description="Recommended IDE extensions, progressive hints, and verification commands.",
            ),
        ]

    def _render_step_1(self) -> RenderableType:
        """Render Step 1: Welcome banner and pedagogical philosophy."""
        renderables: List[Any] = []

        # Banner
        banner_text = Text()
        banner_text.append(BANNER_ART.strip("\n"), style="bold cyan")
        banner_text.append("\n\n")
        banner_text.append("☸ Kubelings Onboarding Tour ", style="bold #00d4fe")
        banner_text.append("— ", style="bold white")
        banner_text.append("Interactive Kubernetes Mastery\n", style="bold magenta")
        banner_text.append(
            "Welcome! Kubelings is designed to teach Kubernetes through active debugging and hands-on practice.",
            style="italic dim white",
        )

        renderables.append(
            Panel(
                banner_text,
                border_style="cyan",
                padding=(1, 2),
            )
        )

        # Pedagogical Philosophy
        philosophy_table = Table(
            title="[bold cyan]Core Pedagogical Philosophy[/bold cyan]",
            title_justify="left",
            show_header=True,
            header_style="bold magenta",
            border_style="cyan",
            expand=True,
        )
        philosophy_table.add_column("Principle", style="bold yellow", ratio=3)
        philosophy_table.add_column("Description", style="white", ratio=7)

        philosophy_table.add_row(
            "1. Active Debugging",
            "Learn by fixing realistic, broken Kubernetes manifests and python controller code rather than reading passive docs.",
        )
        philosophy_table.add_row(
            "2. Sub-30ms Feedback",
            "Instant local feedback on every file save. No slow CI waits — fix mistakes in real-time.",
        )
        philosophy_table.add_row(
            "3. Test-Driven Mastery",
            "Every exercise is backed by automated validation, official OpenAPI schemas, and declarative assertions.",
        )

        renderables.append(
            Panel(
                philosophy_table,
                title="[bold #00d4fe]Step 1 of 5: Welcome & Philosophy[/bold #00d4fe]",
                border_style="#00d4fe",
                padding=(1, 2),
                subtitle="[dim]Active Debugging • Sub-30ms Feedback • Test-Driven Mastery[/dim]",
                subtitle_align="right",
            )
        )

        return Group(*renderables)

    def _render_step_2(self) -> tuple[RenderableType, Dict[str, Any]]:
        """Render Step 2: Environment and cluster diagnostics check."""
        py_ver = sys.version.split()[0]
        py_path = sys.executable

        # Check workspace integrity
        workspace_root = Path.cwd()
        exercises_dir_exists = (workspace_root / "exercises").is_dir()
        solutions_dir_exists = (workspace_root / "solutions").is_dir()
        src_dir_exists = (workspace_root / "src" / "kubelings").is_dir()
        workspace_ok = exercises_dir_exists and solutions_dir_exists and src_dir_exists

        # Cluster probe
        cluster_status = self.cluster_detector.get_cluster_status()
        is_cluster_avail = cluster_status.get("available", False)
        cluster_context = cluster_status.get("context", "none")
        cluster_provider = cluster_status.get("provider", "none")

        diag_table = Table(
            title="[bold cyan]System & Environment Diagnostics[/bold cyan]",
            title_justify="left",
            show_header=True,
            header_style="bold magenta",
            border_style="cyan",
            expand=True,
        )
        diag_table.add_column("Component", style="bold white", ratio=3)
        diag_table.add_column("Status / Details", style="white", ratio=5)
        diag_table.add_column("State", justify="center", ratio=2)

        diag_table.add_row(
            "Python Runtime",
            f"v{py_ver} ({py_path})",
            "[bold green]OK[/bold green]",
        )
        diag_table.add_row(
            "Workspace Integrity",
            f"{'✓ Valid structure' if workspace_ok else '✗ Incomplete structure'} (exercises/, solutions/)",
            "[bold green]READY[/bold green]" if workspace_ok else "[bold yellow]CHECK PATH[/bold yellow]",
        )

        if is_cluster_avail:
            diag_table.add_row(
                "Kubernetes Cluster",
                f"Context: [cyan]{cluster_context}[/cyan] ({cluster_provider})",
                "[bold green]CONNECTED[/bold green]",
            )
        else:
            diag_table.add_row(
                "Kubernetes Cluster",
                "Offline-First Mode (100% offline schema validation active)",
                "[bold yellow]OFFLINE-FIRST[/bold yellow]",
            )

        note_text = Text()
        note_text.append("\n💡 Offline-First Architecture:\n", style="bold cyan")
        note_text.append(
            "Kubelings does NOT require a running Kubernetes cluster for core chapters. "
            "All manifests and workloads are validated locally using official schemas and Python test harnesses. "
            "If a local cluster (Kind/Minikube/k3d) is present, live cluster exercises will automatically activate.",
            style="dim white",
        )

        panel = Panel(
            Group(diag_table, note_text),
            title="[bold #00d4fe]Step 2 of 5: Environment & Cluster Check[/bold #00d4fe]",
            border_style="#00d4fe",
            padding=(1, 2),
            subtitle="[dim]Offline-First Validation Enabled[/dim]",
            subtitle_align="right",
        )

        details = {
            "python_version": py_ver,
            "python_path": py_path,
            "workspace_ok": workspace_ok,
            "cluster_status": cluster_status,
        }
        return panel, details

    def _render_step_3(self) -> tuple[RenderableType, Dict[str, Any]]:
        """Render Step 3: Inner loop workflow and interactive hotkeys."""
        renderables: List[Any] = []

        flow_text = Text()
        flow_text.append("🔄 The Kubelings Inner Feedback Loop:\n\n", style="bold cyan")
        flow_text.append("1. Run ", style="white")
        flow_text.append("kubelings watch", style="bold yellow")
        flow_text.append(" in your terminal to start the live exercise watcher.\n", style="white")
        flow_text.append("2. Open the exercise file (e.g., ", style="white")
        flow_text.append("exercises/01_pods/pods01.py", style="bold cyan")
        flow_text.append(") in your favorite editor.\n", style="white")
        flow_text.append("3. Edit the manifest or code and save the file.\n", style="white")
        flow_text.append(
            "4. Kubelings detects the file save and instantly re-evaluates the exercise (<30ms).\n",
            style="white",
        )
        flow_text.append("5. Remove the ", style="white")
        flow_text.append("'# I AM NOT DONE'", style="bold yellow")
        flow_text.append(" marker when ready to advance to the next challenge.\n", style="white")

        renderables.append(flow_text)

        hotkeys_table = Table(
            title="[bold cyan]Watcher Interactive Hotkeys[/bold cyan]",
            title_justify="left",
            show_header=True,
            header_style="bold magenta",
            border_style="cyan",
            expand=True,
        )
        hotkeys_table.add_column("Key", style="bold yellow", justify="center", ratio=2)
        hotkeys_table.add_column("Action", style="bold white", ratio=3)
        hotkeys_table.add_column("Description", style="white", ratio=5)

        hotkeys = [
            ("n / Enter", "Next Exercise", "Advance to the next exercise when current passes"),
            ("p", "Previous Exercise", "Return to the previous exercise to review"),
            ("h", "Show Hint", "Display progressive hints for current exercise"),
            ("r", "Reload / Re-run", "Force re-execution of the current exercise"),
            ("l", "Lint Manifest", "Run deep schema validation against K8s rules"),
            ("q", "Quit", "Exit the interactive watcher"),
        ]

        for key, action, desc in hotkeys:
            hotkeys_table.add_row(key, action, desc)

        renderables.append(hotkeys_table)

        panel = Panel(
            Group(*renderables),
            title="[bold #00d4fe]Step 3 of 5: Workflow & Hotkeys[/bold #00d4fe]",
            border_style="#00d4fe",
            padding=(1, 2),
            subtitle="[dim]Inner Loop • Live Reload • Keyboard Navigation[/dim]",
            subtitle_align="right",
        )

        details = {
            "hotkeys": [
                {"key": k, "action": a, "description": d} for k, a, d in hotkeys
            ]
        }
        return panel, details

    def _render_step_4(self) -> tuple[RenderableType, Dict[str, Any]]:
        """Render Step 4: Guided first exercise (pods01) walkthrough."""
        renderables: List[Any] = []

        # Exercise lookup
        exercise = get_exercise_by_name("pods01")
        if exercise is None:
            exercise = Exercise(
                name="pods01",
                title="First Pod Manifest & Spec",
                path="exercises/01_pods/pods01.py",
                chapter_name="01_pods",
                hints=[
                    "Set metadata.name to 'nginx-web'",
                    "Specify spec.containers[0].image as 'nginx:alpine'",
                    "Add containerPort 80 under ports",
                ],
            )

        # Run exercise to show initial failure state
        run_res = self.runner.run_exercise(exercise)

        intro_text = Text()
        intro_text.append("Let's look at your very first exercise: ", style="bold white")
        intro_text.append(f"{exercise.name} ({exercise.title})\n", style="bold cyan")
        intro_text.append(
            "In every exercise, you'll encounter a broken or incomplete Kubernetes manifest with '???' placeholders.\n\n",
            style="dim white",
        )
        renderables.append(intro_text)

        # Broken snippet
        broken_yaml = """# Starter manifest with placeholder values:
apiVersion: v1
kind: Pod
metadata:
  name: ???            # Fix: set to 'nginx-web'
  labels:
    app: ???           # Fix: set to 'web'
spec:
  containers:
  - name: nginx
    image: ???         # Fix: set to 'nginx:alpine'
    ports:
    - containerPort: 0 # Fix: set to 80"""

        broken_syntax = Syntax(
            broken_yaml,
            "yaml",
            theme="monokai",
            line_numbers=True,
        )
        renderables.append(
            Panel(
                broken_syntax,
                title="[bold yellow]exercises/01_pods/pods01.py (Initial State)[/bold yellow]",
                border_style="yellow",
                padding=(0, 1),
            )
        )

        # Failure output diagnostics
        failure_msg = run_res.error or run_res.output or "AssertionError: Pod name must be 'nginx-web'"
        err_syntax = Syntax(
            failure_msg.strip(),
            "python",
            theme="monokai",
            line_numbers=False,
            word_wrap=True,
        )
        renderables.append(
            Panel(
                err_syntax,
                title="[bold red]Automated Test Failure Diagnostics[/bold red]",
                border_style="red",
                padding=(0, 1),
            )
        )

        # Solution Diff Explanation
        solution_yaml = """# Solution Diff Explanation:
# 1. Replace metadata.name '???' -> 'nginx-web'
# 2. Replace metadata.labels.app '???' -> 'web'
# 3. Replace containers[0].image '???' -> 'nginx:alpine'
# 4. Set containerPort from 0 -> 80
apiVersion: v1
kind: Pod
metadata:
  name: nginx-web
  labels:
    app: web
spec:
  containers:
  - name: nginx
    image: nginx:alpine
    ports:
    - containerPort: 80"""

        sol_syntax = Syntax(
            solution_yaml,
            "yaml",
            theme="monokai",
            line_numbers=True,
        )
        renderables.append(
            Panel(
                sol_syntax,
                title="[bold green]Reference Solution Explanation (solutions/01_pods/pods01.py)[/bold green]",
                border_style="green",
                padding=(0, 1),
            )
        )

        panel = Panel(
            Group(*renderables),
            title="[bold #00d4fe]Step 4 of 5: Guided First Exercise (pods01)[/bold #00d4fe]",
            border_style="#00d4fe",
            padding=(1, 2),
            subtitle="[dim]Inspect • Break • Fix • Verify[/dim]",
            subtitle_align="right",
        )

        details = {
            "exercise": exercise.name,
            "title": exercise.title,
            "path": exercise.path,
            "initial_passed": run_res.passed,
            "initial_error": failure_msg,
            "initial_output": run_res.output,
        }
        return panel, details

    def _render_step_5(self) -> tuple[RenderableType, Dict[str, Any]]:
        """Render Step 5: IDE tooling, progressive hints, and next steps."""
        renderables: List[Any] = []

        # Tooling recommendations table
        tooling_table = Table(
            title="[bold cyan]Recommended IDE Extensions & Tooling[/bold cyan]",
            title_justify="left",
            show_header=True,
            header_style="bold magenta",
            border_style="cyan",
            expand=True,
        )
        tooling_table.add_column("Tool / Extension", style="bold white", ratio=4)
        tooling_table.add_column("Purpose", style="white", ratio=6)

        extensions = [
            (
                "Red Hat YAML (redhat.vscode-yaml)",
                "Provides real-time schema validation and autocompletion for K8s YAML",
            ),
            (
                "VS Code Kubernetes Tools (ms-kubernetes-tools)",
                "Visual cluster explorer and manifest syntax support",
            ),
            (
                "Python (ms-python.python)",
                "Language support for Python test harnesses and verification scripts",
            ),
        ]
        for name, purpose in extensions:
            tooling_table.add_row(name, purpose)

        renderables.append(tooling_table)

        # Commands reference
        commands_table = Table(
            title="[bold cyan]Key Kubelings CLI Commands[/bold cyan]",
            title_justify="left",
            show_header=True,
            header_style="bold magenta",
            border_style="cyan",
            expand=True,
        )
        commands_table.add_column("Command", style="bold yellow", ratio=4)
        commands_table.add_column("Description", style="white", ratio=6)

        commands = [
            ("kubelings watch", "Start the interactive watcher for continuous learning"),
            ("kubelings run <exercise>", "Run and verify an individual exercise"),
            ("kubelings hint <exercise>", "Reveal progressive numbered hints when stuck"),
            ("kubelings verify", "Run all exercises and check curriculum completion"),
            ("kubelings list", "List all chapters, exercises, and progress status"),
            ("kubelings cluster", "Inspect Kubernetes cluster connection & health"),
        ]
        for cmd, desc in commands:
            commands_table.add_row(cmd, desc)

        renderables.append(commands_table)

        # Next steps call to action
        cta_text = Text()
        cta_text.append("\n🚀 You are ready to start learning!\n\n", style="bold green")
        cta_text.append("Run ", style="white")
        cta_text.append("kubelings watch", style="bold cyan")
        cta_text.append(" to enter watch mode and begin with Chapter 1: Pods.\n", style="white")
        cta_text.append(
            "If you ever get stuck, reference ",
            style="dim white",
        )
        cta_text.append("solutions/", style="bold white")
        cta_text.append(" or use ", style="dim white")
        cta_text.append("kubelings hint <name>", style="bold yellow")
        cta_text.append(".\n", style="dim white")

        renderables.append(cta_text)

        panel = Panel(
            Group(*renderables),
            title="[bold #00d4fe]Step 5 of 5: IDE Tooling & Next Steps[/bold #00d4fe]",
            border_style="#00d4fe",
            padding=(1, 2),
            subtitle="[dim]Extensions • CLI Commands • Solutions Reference[/dim]",
            subtitle_align="right",
        )

        details = {
            "recommended_extensions": [
                {"name": name, "purpose": purpose} for name, purpose in extensions
            ],
            "commands": [{"command": cmd, "description": desc} for cmd, desc in commands],
        }
        return panel, details

    def render_step(self, step_num: int) -> RenderableType:
        """Render the Rich visual element for a specific tour step (1-indexed).

        Args:
            step_num: Step number from 1 to 5.

        Returns:
            Rich renderable element for the requested step.

        Raises:
            ValueError: If step_num is not between 1 and 5.
        """
        if step_num < 1 or step_num > len(self.steps):
            raise ValueError(
                f"Invalid step number: {step_num}. Must be between 1 and {len(self.steps)}."
            )

        if step_num == 1:
            return self._render_step_1()
        elif step_num == 2:
            panel, _ = self._render_step_2()
            return panel
        elif step_num == 3:
            panel, _ = self._render_step_3()
            return panel
        elif step_num == 4:
            panel, _ = self._render_step_4()
            return panel
        elif step_num == 5:
            panel, _ = self._render_step_5()
            return panel
        else:
            raise ValueError(f"Invalid step number: {step_num}")

    def run_step(self, step_num: int, interactive: bool = True) -> TourStepResult:
        """Execute and render a specific tour step.

        Args:
            step_num: Step number to execute (1-5).
            interactive: If True, prompt for user acknowledgment.

        Returns:
            TourStepResult containing step execution status and details.

        Raises:
            ValueError: If step_num is out of valid range (1-5).
        """
        if step_num < 1 or step_num > len(self.steps):
            raise ValueError(
                f"Invalid step number: {step_num}. Must be between 1 and {len(self.steps)}."
            )

        step = self.steps[step_num - 1]
        details: Dict[str, Any] = {}

        if step_num == 1:
            renderable = self._render_step_1()
            details = {
                "philosophy": [
                    "Active Debugging",
                    "Sub-30ms Feedback",
                    "Test-Driven Mastery",
                ]
            }
        elif step_num == 2:
            renderable, details = self._render_step_2()
        elif step_num == 3:
            renderable, details = self._render_step_3()
        elif step_num == 4:
            renderable, details = self._render_step_4()
        elif step_num == 5:
            renderable, details = self._render_step_5()
        else:
            raise ValueError(f"Invalid step number: {step_num}")

        self.console.print(renderable)

        if interactive:
            try:
                self.console.print(
                    f"\n[bold cyan][Step {step_num}/5][/bold cyan] [dim]Press Enter to continue...[/dim] ",
                    end="",
                )
                input()
            except (EOFError, KeyboardInterrupt):
                pass

        return TourStepResult(
            step_num=step.step_num,
            name=step.name,
            title=step.title,
            success=True,
            details=details,
            message=f"Step {step_num} ({step.name}) completed successfully.",
        )

    def run_all(self, interactive: bool = True) -> List[TourStepResult]:
        """Execute all tour steps sequentially.

        Args:
            interactive: If True, pauses between steps for user input.

        Returns:
            List of TourStepResult for all 5 steps.
        """
        results: List[TourStepResult] = []
        for step in self.steps:
            result = self.run_step(step.step_num, interactive=interactive)
            results.append(result)
        return results

    def to_json(self) -> Dict[str, Any]:
        """Serialize tour structure and metadata to a JSON-compatible dictionary.

        Returns:
            Dict containing total_steps count and metadata list for each step.
        """
        return {
            "total_steps": len(self.steps),
            "steps": [
                {
                    "step": s.step_num,
                    "step_num": s.step_num,
                    "name": s.name,
                    "title": s.title,
                    "description": s.description,
                }
                for s in self.steps
            ],
        }

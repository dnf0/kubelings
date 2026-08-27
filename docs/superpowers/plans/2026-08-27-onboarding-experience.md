# Kubelings Onboarding Experience & Guided Tour Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the Unified Onboarding Suite for Kubelings: an interactive 5-step CLI guided tour (`kubelings tour`), a native VS Code / Cursor Walkthrough, and a comprehensive educational onboarding guide.

**Architecture:** A standalone `OnboardingTour` engine in `src/kubelings/tour.py` provides interactive and JSON-formatted walkthrough capabilities. The Typer CLI exposes `kubelings tour` with step jumping and headless modes. The VS Code extension contributes a native walkthrough registered in `package.json` that hooks into extension commands and the CLI bridge. The documentation suite is enriched with `docs/onboarding-guide.md` and cross-referenced in guides.

**Tech Stack:** Python 3.12+, Typer, Rich, TypeScript, VS Code Extension API, Pytest, Node Test Runner, MkDocs.

---

### Task 1: CLI Tour Engine (`src/kubelings/tour.py`) & Unit Tests

**Files:**
- Create: `src/kubelings/tour.py`
- Create: `tests/test_tour.py`

- [ ] **Step 1: Write failing unit tests for `OnboardingTour`**

```python
# tests/test_tour.py
"""Unit tests for Kubelings Onboarding Tour engine."""

import json
from unittest.mock import MagicMock, patch

import pytest
from rich.console import Console

from kubelings.tour import OnboardingTour, TourStepResult


def test_tour_initialization():
    console = Console(record=True)
    tour = OnboardingTour(console=console)
    assert len(tour.steps) == 5
    assert tour.steps[0].id == "welcome"
    assert tour.steps[1].id == "environment"
    assert tour.steps[2].id == "workflow"
    assert tour.steps[3].id == "guided_exercise"
    assert tour.steps[4].id == "tooling"


def test_tour_step_rendering():
    console = Console(record=True)
    tour = OnboardingTour(console=console)
    
    # Render step 1 (welcome)
    res = tour.run_step(1, interactive=False)
    assert res.step_num == 1
    assert res.success is True
    output = console.export_text()
    assert "Welcome to Kubelings" in output or "☸" in output


def test_tour_non_interactive_run_all():
    console = Console(record=True)
    tour = OnboardingTour(console=console)
    
    results = tour.run_all(interactive=False)
    assert len(results) == 5
    assert all(r.success for r in results)


def test_tour_json_output():
    tour = OnboardingTour()
    data = tour.to_json()
    assert "total_steps" in data
    assert data["total_steps"] == 5
    assert len(data["steps"]) == 5
    assert data["steps"][0]["id"] == "welcome"
    assert data["steps"][3]["id"] == "guided_exercise"


def test_tour_specific_step_execution():
    console = Console(record=True)
    tour = OnboardingTour(console=console)
    
    res = tour.run_step(4, interactive=False)
    assert res.step_num == 4
    assert res.step_id == "guided_exercise"
    output = console.export_text()
    assert "pods01" in output
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_tour.py -v`  
Expected: FAIL (`ModuleNotFoundError: No module named 'kubelings.tour'`)

- [ ] **Step 3: Implement `src/kubelings/tour.py`**

```python
"""Interactive Onboarding Tour engine for Kubelings."""

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional
import sys

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

from kubelings.cluster import ClusterDetector
from kubelings.manifest import get_exercise_by_name
from kubelings.models import Exercise
from kubelings.runner import ExerciseRunner


@dataclass
class TourStep:
    number: int
    id: str
    title: str
    description: str
    handler: Callable[["OnboardingTour", bool], bool]


@dataclass
class TourStepResult:
    step_num: int
    step_id: str
    title: str
    success: bool
    summary: str


class OnboardingTour:
    """Manages the 5-step Kubelings educational onboarding experience."""

    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
        self.steps: List[TourStep] = [
            TourStep(1, "welcome", "Welcome & Pedagogical Philosophy", "Core micro-learning philosophy", self._step_welcome),
            TourStep(2, "environment", "Environment & Cluster Check", "Verification of Python & Kubernetes", self._step_environment),
            TourStep(3, "workflow", "The Kubelings Workflow & Hotkeys", "Iteration loop and keyboard shortcuts", self._step_workflow),
            TourStep(4, "guided_exercise", "Guided First Exercise (pods01)", "Live walkthrough and evaluation of pods01", self._step_guided_exercise),
            TourStep(5, "tooling", "IDE Tooling & Next Steps", "VS Code extension, solutions and watch loop", self._step_tooling),
        ]

    def _step_welcome(self, interactive: bool) -> bool:
        self.console.print()
        self.console.print(
            Panel.fit(
                "[bold cyan]☸ WELCOME TO KUBELINGS[/bold cyan]\n"
                "[dim]Master Kubernetes From Scratch Through Interactive Micro-Exercises[/dim]",
                border_style="bright_blue",
            )
        )
        self.console.print(
            "\n[bold white]Kubelings is built on three core educational principles:[/bold white]\n"
            "  1. [bold green]Active Debugging[/bold green]: Every exercise starts in a broken state. You inspect errors and fix them.\n"
            "  2. [bold cyan]Sub-30ms Instant Feedback[/bold cyan]: All manifests are verified in-memory locally with zero cluster latency.\n"
            "  3. [bold yellow]Test-Driven Mastery[/bold yellow]: Exercises pass only when genuine Kubernetes schema assertions succeed.\n"
        )
        return True

    def _step_environment(self, interactive: bool) -> bool:
        self.console.print()
        self.console.print(
            Panel.fit(
                "[bold cyan]STEP 2: Environment & Cluster Verification[/bold cyan]",
                border_style="cyan",
            )
        )
        table = Table(title="System Environment Probes", border_style="blue", show_header=True)
        table.add_column("Component", style="bold cyan")
        table.add_column("Status", style="bold green")
        table.add_column("Details", style="dim")

        table.add_row("Python Runtime", f"v{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}", sys.executable)
        
        detector = ClusterDetector()
        status = detector.get_cluster_status(refresh=False)
        if status.connected:
            cluster_desc = f"Connected ({status.provider}) - Context: {status.context}"
            table.add_row("Kubernetes Cluster", "Connected ✓", cluster_desc)
        else:
            table.add_row("Kubernetes Cluster", "Offline Ready ✓", "Pure in-memory offline validation enabled")

        self.console.print(table)
        self.console.print(
            "\n[dim]Note: Kubelings does NOT require a running Kubernetes cluster. All 23 chapters work 100% offline.[/dim]\n"
        )
        return True

    def _step_workflow(self, interactive: bool) -> bool:
        self.console.print()
        self.console.print(
            Panel.fit(
                "[bold cyan]STEP 3: The Kubelings Workflow & Hotkeys[/bold cyan]",
                border_style="cyan",
            )
        )
        self.console.print(
            "[bold white]The Inner Learning Loop:[/bold white]\n"
            "  1. Run [bold green]kubelings watch[/bold green] in your terminal.\n"
            "  2. Open the active file (e.g. [bold yellow]exercises/01_pods/pods01.py[/bold yellow]) in your code editor.\n"
            "  3. Modify the YAML manifest or Python verification code.\n"
            "  4. [bold cyan]Save the file[/bold cyan] — Kubelings re-evaluates the tests in < 30ms!\n"
            "  5. When passing, press [bold green][n][/bold green] or [bold green][Enter][/bold green] to advance.\n"
        )

        hotkey_table = Table(title="Interactive Watcher Keybindings", border_style="green")
        hotkey_table.add_column("Key", style="bold yellow")
        hotkey_table.add_column("Action", style="bold cyan")
        hotkey_table.add_column("Description", style="dim")
        hotkey_table.add_row("n / Enter", "Next", "Advance to next exercise")
        hotkey_table.add_row("p", "Previous", "Navigate to previous exercise")
        hotkey_table.add_row("h", "Hint", "Reveal progressive hint tier")
        hotkey_table.add_row("r", "Rerun", "Force immediate re-evaluation")
        hotkey_table.add_row("l", "List", "Display syllabus overview")
        hotkey_table.add_row("q", "Quit", "Exit the file watcher")
        self.console.print(hotkey_table)
        return True

    def _step_guided_exercise(self, interactive: bool) -> bool:
        self.console.print()
        self.console.print(
            Panel.fit(
                "[bold cyan]STEP 4: Guided First Exercise (pods01)[/bold cyan]",
                border_style="cyan",
            )
        )
        ex = get_exercise_by_name("pods01")
        if not ex:
            self.console.print("[red]Exercise pods01 not found![/red]")
            return False

        self.console.print(
            f"[bold white]Let's inspect your first exercise:[/bold white] [bold cyan]{ex.path}[/bold cyan]\n"
            f"Title: [bold]{ex.title}[/bold]\n"
        )

        runner = ExerciseRunner()
        res = runner.run_exercise(ex)
        
        status_msg = "[bold red]FAIL (Expected initial state)[/bold red]" if not res.passed else "[bold green]PASS[/bold green]"
        self.console.print(f"Initial Test Evaluation: {status_msg}")
        if res.error:
            self.console.print(Panel(res.error.strip(), title="Validation Error Output", border_style="red"))

        self.console.print(
            "[bold green]How to solve pods01:[/bold green]\n"
            "  • Open [cyan]exercises/01_pods/pods01.py[/cyan]\n"
            "  • Add container port [yellow]containerPort: 80[/yellow]\n"
            "  • Add pod label [yellow]labels: {app: web}[/yellow]\n"
            "  • Save and watch the terminal turn green!\n"
        )
        return True

    def _step_tooling(self, interactive: bool) -> bool:
        self.console.print()
        self.console.print(
            Panel.fit(
                "[bold cyan]STEP 5: IDE Tooling & Next Steps[/bold cyan]",
                border_style="cyan",
            )
        )
        self.console.print(
            "[bold white]Supercharge your learning experience:[/bold white]\n"
            "  • [bold cyan]VS Code / Cursor Extension[/bold cyan]: Install [magenta]kubelings-vscode.vsix[/magenta] for in-editor squiggles & quick fixes.\n"
            "  • [bold yellow]Progressive Hints[/bold yellow]: Run [cyan]kubelings hint pods01[/cyan] whenever you are stuck.\n"
            "  • [bold green]Reference Solutions[/bold green]: Compare code with [cyan]solutions/01_pods/pods01.py[/cyan].\n"
            "  • [bold blue]Full Progress Dashboard[/bold blue]: Run [cyan]kubelings verify[/cyan] anytime to view your overall progress.\n"
        )
        return True

    def run_step(self, step_num: int, interactive: bool = True) -> TourStepResult:
        if step_num < 1 or step_num > len(self.steps):
            step_num = 1
        step = self.steps[step_num - 1]
        success = step.handler(interactive)
        return TourStepResult(
            step_num=step.number,
            step_id=step.id,
            title=step.title,
            success=success,
            summary=step.description,
        )

    def run_all(self, interactive: bool = True) -> List[TourStepResult]:
        results = []
        for step in self.steps:
            res = self.run_step(step.number, interactive=interactive)
            results.append(res)
            if interactive and step.number < len(self.steps):
                try:
                    prompt = self.console.input(f"\n[bold cyan]Press [Enter] for Step {step.number + 1} of {len(self.steps)} (or [q] to quit): [/bold cyan]")
                    if prompt.strip().lower() in ("q", "quit", "exit"):
                        break
                except (EOFError, KeyboardInterrupt):
                    break
        return results

    def to_json(self) -> Dict[str, Any]:
        return {
            "total_steps": len(self.steps),
            "steps": [
                {
                    "number": s.number,
                    "id": s.id,
                    "title": s.title,
                    "description": s.description,
                }
                for s in self.steps
            ],
        }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_tour.py -v`  
Expected: PASS (5/5 tests passing)

- [ ] **Step 5: Commit**

```bash
git add src/kubelings/tour.py tests/test_tour.py
git commit --no-gpg-sign -m "feat(tour): implement 5-step onboarding tour engine and tests"
```

---

### Task 2: CLI Command Registration & Auto-Recommendation

**Files:**
- Modify: `src/kubelings/cli.py`
- Modify: `tests/test_cli.py`
- Modify: `tests/test_cli_json.py`

- [ ] **Step 1: Write failing CLI tests for `kubelings tour`**

Add tests to `tests/test_cli.py` and `tests/test_cli_json.py`:
```python
def test_cli_tour_command():
    result = runner.invoke(app, ["tour", "--non-interactive"])
    assert result.exit_code == 0
    assert "WELCOME TO KUBELINGS" in result.stdout or "Step 1" in result.stdout


def test_cli_tour_specific_step():
    result = runner.invoke(app, ["tour", "--step", "3", "--non-interactive"])
    assert result.exit_code == 0
    assert "Workflow" in result.stdout or "STEP 3" in result.stdout


def test_cli_tour_json():
    result = runner.invoke(app, ["tour", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert data["total_steps"] == 5
    assert len(data["steps"]) == 5
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_cli.py::test_cli_tour_command -v`  
Expected: FAIL (`No such command 'tour'`)

- [ ] **Step 3: Register `tour` command in `src/kubelings/cli.py`**

```python
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

    if step is not None:
        tour.run_step(step, interactive=not non_interactive)
    else:
        tour.run_all(interactive=not non_interactive)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_cli.py tests/test_cli_json.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/kubelings/cli.py tests/test_cli.py tests/test_cli_json.py
git commit --no-gpg-sign -m "feat(cli): add 'kubelings tour' command and CLI json support"
```

---

### Task 3: VS Code Extension Walkthrough & CLI Bridge Integration

**Files:**
- Modify: `extensions/vscode/package.json`
- Create: `extensions/vscode/walkthrough/welcome.md`
- Create: `extensions/vscode/walkthrough/cluster.md`
- Create: `extensions/vscode/walkthrough/watch.md`
- Create: `extensions/vscode/walkthrough/exercise.md`
- Create: `extensions/vscode/walkthrough/quickfixes.md`
- Modify: `extensions/vscode/src/commands.ts`
- Modify: `extensions/vscode/src/cliBridge.ts`
- Create: `extensions/vscode/test/walkthrough.test.ts`

- [ ] **Step 1: Write failing TypeScript test for walkthrough command & bridge**

```typescript
// extensions/vscode/test/walkthrough.test.ts
import * as assert from 'assert';
import { KubelingsCliBridge } from '../src/cliBridge';

describe('Kubelings Walkthrough & Tour Integration', () => {
  it('bridge resolves tour JSON payload', async () => {
    const bridge = new KubelingsCliBridge();
    const tourData = await bridge.tour();
    assert.strictEqual(tourData.total_steps, 5);
    assert.strictEqual(tourData.steps.length, 5);
    assert.strictEqual(tourData.steps[0].id, 'welcome');
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `make vscode-test`  
Expected: FAIL (`Property 'tour' does not exist on type 'KubelingsCliBridge'`)

- [ ] **Step 3: Implement walkthrough contributions, markdown assets, and bridge methods**

1. In `extensions/vscode/src/cliBridge.ts`:
```typescript
  public async tour(): Promise<{ total_steps: number; steps: Array<{ number: number; id: string; title: string; description: string }> }> {
    const stdout = await this.executeKubelingsCommand(['tour', '--json']);
    return JSON.parse(stdout);
  }
```

2. In `extensions/vscode/src/commands.ts`:
Register `kubelings.openWalkthrough` command:
```typescript
  const openWalkthroughCmd = vscode.commands.registerCommand(
    'kubelings.openWalkthrough',
    () => {
      vscode.commands.executeCommand(
        'workbench.action.openWalkthrough',
        'dnf0.kubelings-vscode#kubelings.walkthrough',
        false
      );
    }
  );
  context.subscriptions.push(openWalkthroughCmd);
```

3. In `extensions/vscode/package.json`:
Add command `kubelings.openWalkthrough` and `contributes.walkthroughs`:
```json
"walkthroughs": [
  {
    "id": "kubelings.walkthrough",
    "title": "Get Started with Kubelings ☸️",
    "description": "Master Kubernetes through hands-on, test-driven micro-exercises.",
    "steps": [
      {
        "id": "welcome",
        "title": "Welcome & Curriculum Overview",
        "description": "walkthrough/welcome.md"
      },
      {
        "id": "cluster",
        "title": "Check Your Environment",
        "description": "walkthrough/cluster.md"
      },
      {
        "id": "watch",
        "title": "Interactive Watch Mode",
        "description": "walkthrough/watch.md"
      },
      {
        "id": "exercise",
        "title": "Solve First Exercise (pods01)",
        "description": "walkthrough/exercise.md"
      },
      {
        "id": "quickfixes",
        "title": "Diagnostics & Quick Fixes",
        "description": "walkthrough/quickfixes.md"
      }
    ]
  }
]
```

4. Create the 5 walkthrough markdown files in `extensions/vscode/walkthrough/`.

- [ ] **Step 4: Run test to verify it passes**

Run: `make vscode-test && make vscode-build`  
Expected: PASS (41/41 tests passing)

- [ ] **Step 5: Commit**

```bash
git add extensions/vscode/
git commit --no-gpg-sign -m "feat(vscode): add native interactive walkthrough and tour CLI bridge"
```

---

### Task 4: Documentation Guide & Full End-to-End Verification

**Files:**
- Create: `docs/onboarding-guide.md`
- Modify: `README.md`
- Modify: `docs/index.md`
- Modify: `docs/getting-started.md`
- Modify: `docs/cli-reference.md`
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Create `docs/onboarding-guide.md`**
Write a comprehensive step-by-step visual tutorial covering installation, `kubelings tour`, VS Code walkthrough, solving `pods01.py`, and syllabus progression.

- [ ] **Step 2: Update references across documentation**
Update `README.md`, `docs/index.md`, `docs/getting-started.md`, `docs/cli-reference.md`, and `CHANGELOG.md` to document `kubelings tour`.

- [ ] **Step 3: Run full verification suite**
```bash
uv run pytest
make vscode-test
uv run ruff check .
uv run ruff format --check .
uv run pyright
make vscode-package
uvx --from graphifyy graphify update .
```

- [ ] **Step 4: Commit**

```bash
git add docs/ README.md CHANGELOG.md graphify-out/
git commit --no-gpg-sign -m "docs: add comprehensive onboarding guide and update CLI reference"
```

---

## Execution Handoff
Two execution options:
1. **Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration.
2. **Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints.

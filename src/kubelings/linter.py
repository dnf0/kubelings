"""Universal Kubernetes Manifest & Best-Practices Linter."""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml
from rich.console import Console
from rich.table import Table

from kubelings.ui import get_console


class LintSeverity(str, Enum):
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


@dataclass
class LintDiagnostic:
    rule_id: str
    severity: LintSeverity
    message: str
    suggestion: str
    path: str
    line: Optional[int] = None


class ManifestLinter:
    """Evaluates Kubernetes manifests against security, reliability, and schema rules."""

    def lint_manifest(self, manifest: Dict[str, Any], file_path: str = "inline") -> List[LintDiagnostic]:
        diagnostics: List[LintDiagnostic] = []

        if not isinstance(manifest, dict):
            diagnostics.append(
                LintDiagnostic(
                    rule_id="SCH000_NOT_A_DICT",
                    severity=LintSeverity.ERROR,
                    message="Manifest root is not a valid dictionary structure.",
                    suggestion="Ensure valid YAML/JSON document structure.",
                    path=file_path,
                )
            )
            return diagnostics

        # 1. Schema integrity rules
        kind = manifest.get("kind")
        api_version = manifest.get("apiVersion")
        metadata = manifest.get("metadata", {})

        if not kind:
            diagnostics.append(
                LintDiagnostic(
                    rule_id="SCH002_MISSING_KIND",
                    severity=LintSeverity.ERROR,
                    message="Missing required 'kind' field.",
                    suggestion="Define valid Kubernetes Kind (e.g. Pod, Deployment, Service).",
                    path=file_path,
                )
            )

        if not api_version:
            diagnostics.append(
                LintDiagnostic(
                    rule_id="SCH003_MISSING_APIVERSION",
                    severity=LintSeverity.ERROR,
                    message="Missing required 'apiVersion' field.",
                    suggestion="Specify correct apiVersion (e.g. 'v1', 'apps/v1').",
                    path=file_path,
                )
            )

        if not isinstance(metadata, dict) or not metadata.get("name"):
            diagnostics.append(
                LintDiagnostic(
                    rule_id="SCH001_MISSING_NAME",
                    severity=LintSeverity.ERROR,
                    message="Missing or invalid 'metadata.name'.",
                    suggestion="Provide a non-empty name string under metadata.",
                    path=file_path,
                )
            )

        # Workload-specific rules
        workload_kinds = {"Pod", "Deployment", "StatefulSet", "DaemonSet", "Job", "CronJob"}
        if kind in workload_kinds:
            spec = manifest.get("spec", {})
            pod_spec = spec.get("template", {}).get("spec", {}) if "template" in spec else spec

            # Security checks
            pod_sec = pod_spec.get("securityContext", {})
            containers = pod_spec.get("containers", [])

            run_as_non_root = pod_sec.get("runAsNonRoot")
            if run_as_non_root is not True:
                container_non_roots = [
                    c.get("securityContext", {}).get("runAsNonRoot") for c in containers
                ]
                if not any(cnr is True for cnr in container_non_roots):
                    diagnostics.append(
                        LintDiagnostic(
                            rule_id="SEC001_RUN_AS_NON_ROOT",
                            severity=LintSeverity.WARNING,
                            message="Container does not enforce runAsNonRoot: true.",
                            suggestion="Add securityContext.runAsNonRoot: true to PodSpec or Container.",
                            path=file_path,
                        )
                    )

            # Container level checks
            for idx, c in enumerate(containers):
                c_name = c.get("name", f"container[{idx}]")
                c_sec = c.get("securityContext", {})
                
                # Privileged check
                if c_sec.get("privileged") is True:
                    diagnostics.append(
                        LintDiagnostic(
                            rule_id="SEC002_PRIVILEGED_CONTAINER",
                            severity=LintSeverity.ERROR,
                            message=f"Container '{c_name}' runs in privileged mode.",
                            suggestion="Avoid privileged: true; grant granular Linux capabilities instead.",
                            path=file_path,
                        )
                    )

                # Resource limits check
                resources = c.get("resources", {})
                limits = resources.get("limits", {})
                requests = resources.get("requests", {})
                if not limits or not requests:
                    diagnostics.append(
                        LintDiagnostic(
                            rule_id="RES001_MISSING_LIMITS",
                            severity=LintSeverity.WARNING,
                            message=f"Container '{c_name}' missing CPU/memory requests or limits.",
                            suggestion="Define resources.requests and resources.limits to prevent node starvation.",
                            path=file_path,
                        )
                    )

                # Probes check (for long-running services)
                if kind in ("Pod", "Deployment", "StatefulSet", "DaemonSet"):
                    liveness = c.get("livenessProbe")
                    readiness = c.get("readinessProbe")
                    if not liveness and not readiness:
                        diagnostics.append(
                            LintDiagnostic(
                                rule_id="REL001_MISSING_PROBES",
                                severity=LintSeverity.WARNING,
                                message=f"Container '{c_name}' has no liveness or readiness probes.",
                                suggestion="Add livenessProbe and readinessProbe for traffic & restart health.",
                                path=file_path,
                            )
                        )

        return diagnostics

    def lint_file(self, file_path: Path) -> List[LintDiagnostic]:
        """Parse and lint a YAML/JSON file from disk."""
        if not file_path.exists():
            return [
                LintDiagnostic(
                    rule_id="IO001_FILE_NOT_FOUND",
                    severity=LintSeverity.ERROR,
                    message=f"File not found: {file_path}",
                    suggestion="Check file path.",
                    path=str(file_path),
                )
            ]

        content = file_path.read_text(encoding="utf-8")
        diagnostics: List[LintDiagnostic] = []

        try:
            docs = list(yaml.safe_load_all(content))
        except yaml.YAMLError as e:
            return [
                LintDiagnostic(
                    rule_id="SYN001_YAML_SYNTAX",
                    severity=LintSeverity.ERROR,
                    message=f"YAML syntax parsing error: {e}",
                    suggestion="Fix YAML indentation and syntax.",
                    path=str(file_path),
                )
            ]

        for doc in docs:
            if doc and isinstance(doc, dict):
                diagnostics.extend(self.lint_manifest(doc, file_path=str(file_path)))

        return diagnostics


def render_lint_table(diagnostics: List[LintDiagnostic], console: Optional[Console] = None) -> Table:
    """Render a Rich table formatting lint diagnostics."""
    c = console or get_console()
    table = Table(
        title="[bold cyan]☸ Kubelings Manifest Linter Diagnostics[/bold cyan]",
        border_style="cyan",
        show_header=True,
        header_style="bold magenta",
    )
    table.add_column("Severity", width=10)
    table.add_column("Rule ID", width=26)
    table.add_column("Message", min_width=32)
    table.add_column("Suggestion", min_width=32)
    table.add_column("Path", width=22)

    severity_colors = {
        LintSeverity.ERROR: "bold red",
        LintSeverity.WARNING: "bold yellow",
        LintSeverity.INFO: "bold cyan",
    }

    for d in diagnostics:
        color = severity_colors.get(d.severity, "white")
        table.add_row(
            f"[{color}]{d.severity.value}[/{color}]",
            f"[bold white]{d.rule_id}[/bold white]",
            d.message,
            f"[dim]{d.suggestion}[/dim]",
            d.path,
        )

    if console is not None:
        c.print(table)
    return table

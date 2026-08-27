"""Kubernetes Resource Relationship Topology Visualizer."""

from typing import Any, Dict, List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.tree import Tree

from kubelings.ui import get_console


def _format_resource_label(kind: str, name: str, namespace: str = "default") -> str:
    """Format rich text label for a Kubernetes resource badge."""
    kind_colors = {
        "Pod": "cyan",
        "Deployment": "bold blue",
        "StatefulSet": "bold blue",
        "DaemonSet": "bold blue",
        "Job": "magenta",
        "CronJob": "magenta",
        "Service": "green",
        "Ingress": "bold green",
        "HTTPRoute": "bold green",
        "Gateway": "bold green",
        "PersistentVolumeClaim": "yellow",
        "PersistentVolume": "bold yellow",
        "StorageClass": "dim yellow",
        "ConfigMap": "white",
        "Secret": "red",
        "NetworkPolicy": "bold red",
        "CiliumNetworkPolicy": "bold red",
        "ClusterRole": "purple",
        "Role": "purple",
    }
    color = kind_colors.get(kind, "bold white")
    return f"[{color}]{kind}[/{color}] [bold white]{name}[/bold white] [dim]({namespace})[/dim]"


def build_resource_topology(manifests: List[Dict[str, Any]]) -> Tree:
    """Build a Rich hierarchical tree reflecting Kubernetes architectural relationships."""
    root = Tree("[bold cyan]☸ Kubernetes Resource Architecture & Topology[/bold cyan]")

    if not manifests:
        root.add("[dim italic]No manifests found in context.[/dim italic]")
        return root

    # Categorize resources
    workloads = []
    services = []
    ingresses = []
    storage = []
    policies = []
    configs = []
    others = []

    for m in manifests:
        if not isinstance(m, dict):
            continue
        kind = m.get("kind", "")
        if kind in (
            "Pod",
            "Deployment",
            "StatefulSet",
            "DaemonSet",
            "Job",
            "CronJob",
            "ReplicaSet",
        ):
            workloads.append(m)
        elif kind in ("Service", "Endpoints"):
            services.append(m)
        elif kind in ("Ingress", "Gateway", "HTTPRoute"):
            ingresses.append(m)
        elif kind in ("PersistentVolumeClaim", "PersistentVolume", "StorageClass"):
            storage.append(m)
        elif kind in (
            "NetworkPolicy",
            "CiliumNetworkPolicy",
            "CiliumClusterwideNetworkPolicy",
            "ClusterPolicy",
            "PeerAuthentication",
        ):
            policies.append(m)
        elif kind in ("ConfigMap", "Secret"):
            configs.append(m)
        else:
            others.append(m)

    # Ingress / Gateway layer
    if ingresses:
        ing_branch = root.add("[bold green]🌐 Ingress & Gateway Layer[/bold green]")
        for ing in ingresses:
            kind = ing.get("kind", "Ingress")
            name = ing.get("metadata", {}).get("name", "unnamed")
            ns = ing.get("metadata", {}).get("namespace", "default")
            sub = ing_branch.add(_format_resource_label(kind, name, ns))

            # Show rules
            rules = ing.get("spec", {}).get("rules", [])
            for r in rules:
                host = r.get("host", "*")
                paths = [p.get("path", "/") for p in r.get("http", {}).get("paths", [])]
                sub.add(f"[dim]host: {host} ➔ paths: {', '.join(paths)}[/dim]")

    # Service / Networking layer
    if services:
        svc_branch = root.add("[bold green]🔀 Services & Networking Layer[/bold green]")
        for svc in services:
            kind = svc.get("kind", "Service")
            name = svc.get("metadata", {}).get("name", "unnamed")
            ns = svc.get("metadata", {}).get("namespace", "default")
            sub = svc_branch.add(_format_resource_label(kind, name, ns))

            ports = svc.get("spec", {}).get("ports", [])
            for p in ports:
                sub.add(f"[dim]port {p.get('port')} ➔ targetPort {p.get('targetPort')}[/dim]")

    # Workload layer
    if workloads:
        wl_branch = root.add("[bold blue]📦 Workloads & Compute Pods[/bold blue]")
        for wl in workloads:
            kind = wl.get("kind", "Workload")
            name = wl.get("metadata", {}).get("name", "unnamed")
            ns = wl.get("metadata", {}).get("namespace", "default")
            sub = wl_branch.add(_format_resource_label(kind, name, ns))

            # Containers
            spec = wl.get("spec", {})
            if "template" in spec:
                spec = spec.get("template", {}).get("spec", {})
            containers = spec.get("containers", [])
            for c in containers:
                sub.add(
                    f"[cyan]🐳 container:[/cyan] [white]{c.get('name')}[/white] [dim]({c.get('image')})[/dim]"
                )

    # Storage layer
    if storage:
        st_branch = root.add("[bold yellow]💾 Storage & Persistence Layer[/bold yellow]")
        for st in storage:
            kind = st.get("kind", "Storage")
            name = st.get("metadata", {}).get("name", "unnamed")
            ns = st.get("metadata", {}).get("namespace", "default")
            sub = st_branch.add(_format_resource_label(kind, name, ns))
            sc = st.get("spec", {}).get("storageClassName")
            if sc:
                sub.add(f"[dim]StorageClass: {sc}[/dim]")

    # Security & Policies
    if policies:
        pol_branch = root.add("[bold red]🛡️ Security, Policies & Mesh[/bold red]")
        for pol in policies:
            kind = pol.get("kind", "Policy")
            name = pol.get("metadata", {}).get("name", "unnamed")
            ns = pol.get("metadata", {}).get("namespace", "default")
            pol_branch.add(_format_resource_label(kind, name, ns))

    # Configs
    if configs:
        cfg_branch = root.add("[bold white]⚙️ Configuration & Secrets[/bold white]")
        for cfg in configs:
            kind = cfg.get("kind", "Config")
            name = cfg.get("metadata", {}).get("name", "unnamed")
            ns = cfg.get("metadata", {}).get("namespace", "default")
            cfg_branch.add(_format_resource_label(kind, name, ns))

    if others:
        oth_branch = root.add("[bold purple]🧩 Custom & Cluster Resources[/bold purple]")
        for oth in others:
            kind = oth.get("kind", "Resource")
            name = oth.get("metadata", {}).get("name", "unnamed")
            ns = oth.get("metadata", {}).get("namespace", "default")
            oth_branch.add(_format_resource_label(kind, name, ns))

    return root


def render_topology_tree(
    manifests: List[Dict[str, Any]], console: Optional[Console] = None
) -> None:
    """Render topology tree in a formatted panel."""
    c = console or get_console()
    tree = build_resource_topology(manifests)
    panel = Panel(
        tree,
        title="[bold cyan]☸ Kubelings Architecture Visualizer[/bold cyan]",
        border_style="cyan",
        padding=(1, 2),
    )
    c.print(panel)

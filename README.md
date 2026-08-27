# Kubelings ☸️

[![CI](https://github.com/dnf0/kubelings/actions/workflows/ci.yml/badge.svg)](https://github.com/dnf0/kubelings/actions)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Type checker: pyright](https://img.shields.io/badge/types-pyright-green.svg)](https://github.com/microsoft/pyright)

> **Master Kubernetes from scratch through small, interactive, hands-on terminal exercises.**

<p align="center">
  <img src="assets/demo.svg" alt="Kubelings Terminal Demo" width="800">
</p>

Inspired by the pedagogical brilliance of [rustlings](https://github.com/rust-lang/rustlings), [ziglings](https://github.com/ziglings/exercises), and [raylings](https://github.com/ray-project/raylings), **Kubelings** guides engineers through self-paced, iterative exercises. You will fix broken YAML manifests, construct multi-container sidecars, mount storage volumes, write RBAC authorization rules, solve scheduling constraints, build custom Python Kubernetes operators, and troubleshoot production cluster incidents.

---

## Pedagogical Philosophy

Learning Kubernetes from static documentation or raw copy-pasted Helm charts is difficult because feedback is slow and error messages are cryptic. Kubelings solves this through **guided, test-driven micro-learning**:

1. **Active Debugging & Iteration**: Every exercise starts in a broken or incomplete state containing a `# I AM NOT DONE` marker. You read the problem description, inspect the failure, and edit the code until it passes.
2. **Instant Feedback Loop & Interactive Hotkeys**: An automated watcher observes file modifications in real time (< 30ms). Press `h` to reveal progressive hints, `r` to force a rerun, `l` to list exercises, or `q` to quit.
3. **Dual-Mode Learning (Offline & Live Cluster)**:
   - **Offline Mode**: Zero cluster setup required. Exercises validate Kubernetes object specs, API constraints, and controller behaviors in-memory.
   - **Live Cluster Mode**: Seamlessly connect to `kind`, `minikube`, `k3d`, or remote clusters. Exercises provision temporary ephemeral namespaces and verify live reconciliations.
4. **Progressive Hints**: When stuck, multi-tiered hints (`kubelings hint`) nudge you in the right direction without spoiling the answer.

---

## Architecture

```
                                  +-----------------------+
                                  |     User Terminal     |
                                  +-----------+-----------+
                                              |
                                              v
                                  +-----------------------+
                                  |  Kubelings CLI (Typer)|
                                  +-----------+-----------+
                                              |
                     +------------------------+------------------------+
                     |                                                 |
                     v                                                 v
         +-----------------------+                         +-----------------------+
         |  File Watcher Engine  |                         | Rich UI & Diagnostics |
         |      (watchfiles)     |                         |    (syntax / tables)  |
         +-----------+-----------+                         +-----------------------+
                     |
                     v
         +-----------------------+
                      |
                      v
          +-----------------------+
          |  Curriculum Manifest  |  (18 Chapters / 82 Exercises)
          +-----------+-----------+
                      |
                      v
          +-----------------------+
          |   Exercise Runner     |
          +-----------+-----------+
                      |
         +------------+------------+
         |                         |
         v                         v
 +----------------+       +-------------------+
 | Offline Schema |       | Live Cluster      |
 | Validator &    |  OR   | Adapter & Ephem.  |
 | Spec Evaluator |       | Namespaces (kind) |
 +----------------+       +-------------------+
```

---

## Quickstart & Installation

### Prerequisites

- Python `>= 3.10`
- [`uv`](https://github.com/dnf0/kubelings/actions) (recommended) or `pip`
- *Optional (for live cluster exercises)*: `kubectl` and a local cluster (`kind`, `minikube`, or `k3d`)

### Running Instantly (No Clone Needed)

You can run Kubelings anywhere using [`uvx`](https://github.com/astral-sh/uv) or [`pipx`](https://pypa.github.io/pipx/):

```bash
# Initialize exercises in your current folder
uvx kubelings init

# Start the interactive watch mode
uvx kubelings watch
```

Or install globally:

```bash
pipx install kubelings
kubelings init
kubelings watch
```

### Local Development Installation

Clone the repository and install dependencies in editable mode:

#### Using `uv` (Fastest)

```bash
git clone https://github.com/dnf0/kubelings.git
cd kubelings
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

#### Using Standard `pip`

```bash
git clone https://github.com/dnf0/kubelings.git
cd kubelings
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Verify your installation:

```bash
kubelings --help
```

---

## Interactive Learning Commands

### 1. Watch Mode (`kubelings watch`)

Start the interactive development loop. Whenever you save a file in `exercises/`, Kubelings immediately evaluates your changes.

```bash
kubelings watch
```

> **Interactive Hotkeys**:
> - `h` : Reveal progressive hint tier
> - `r` : Force rerun current exercise
> - `l` : List curriculum exercises
> - `q` : Exit watcher

### 2. Interactive Terminal TUI Dashboard (`kubelings tui` / `kubelings dashboard`)

Explore the curriculum, browse code, and trigger evaluations inside a split-pane full-screen terminal interface:

```bash
kubelings tui
# or
kubelings dashboard
```

### 3. Resource Relationship Topology Visualizer (`kubelings tree`)

Render an architectural relationship topology tree of Kubernetes workloads, services, endpoints, volumes, and network policies:

```bash
kubelings tree pods01
# or inspect an external manifest
kubelings tree deployment.yaml
```

### 4. Universal Manifest Linter (`kubelings lint`)

Audit any Kubernetes manifest against security standards, reliability probes, and schema best practices:

```bash
kubelings lint exercises/01_pods/pods01.py
# or lint production manifests
kubelings lint manifests/production/
```

### 5. Run a Single Exercise

Execute and evaluate a single exercise directly:

```bash
kubelings run pods01
```

### 6. Progressive Hints

Get step-by-step tips for any exercise:

```bash
kubelings hint pods01
```

### 7. List All Chapters & Exercises

Browse the entire curriculum syllabus, descriptions, and exercise paths:

```bash
kubelings list
```

### 8. Verify Curriculum Progress

Display a rich summary table showing the pass/fail status of all 82 exercises:

```bash
kubelings verify
```

### 9. Test Reference Solutions

Run built-in self-testing across reference solutions:

```bash
kubelings test
```

### 10. Cluster Connectivity Status

Check whether `kubelings` is running in offline validation mode or connected to a live Kubernetes cluster:

```bash
kubelings cluster
```

---

## Curriculum & Syllabus

Kubelings covers 18 structured chapters with **82 practical exercises**:

| Chapter | Title | Topic Overview | Exercises |
| :--- | :--- | :--- | :--- |
| **01** | **Pods & Core Workloads** | Pod specs, multi-container sidecars, init containers, resource requests/limits, Downward API, and Pod Disruption Budgets (PDB). | `pods01` – `pods06` (6) |
| **02** | **Controllers & Replication** | ReplicaSets, label selectors, Deployments, rolling updates, rollbacks, StatefulSets, DaemonSets, and Jobs/CronJobs. | `ctrl01` – `ctrl06` (6) |
| **03** | **Configuration & Secrets** | ConfigMaps, Secrets, environment variable injection, volume mounts, permission modes, and immutable configs. | `config01` – `config05` (5) |
| **04** | **Storage & Persistent Volumes** | Volume types (`emptyDir`, `hostPath`), PVs, PVCs, access modes, reclaim policies, StorageClasses, and volume snapshots. | `storage01` – `storage05` (5) |
| **05** | **Services & Networking** | ClusterIP, Headless services, NodePort, LoadBalancer, CoreDNS resolution, ExternalName, and manual Endpoints. | `net01` – `net05` (5) |
| **06** | **Ingress & Gateway API** | Ingress path routing, TLS termination, URL rewrite annotations, and modern Gateway API (`GatewayClass`, `HTTPRoute`). | `ingress01` – `ingress04` (4) |
| **07** | **Scheduling & Placement** | `nodeSelector`, node affinity (hard/soft), pod affinity/anti-affinity, taints, tolerations, and topology spread constraints. | `sched01` – `sched05` (5) |
| **08** | **Security & RBAC** | ServiceAccounts, token management, Roles, RoleBindings, ClusterRoles, container `securityContext`, and Pod Security Standards (PSS). | `rbac01` – `rbac05` (5) |
| **09** | **Network Policies** | Default Deny isolation, Ingress filtering, Egress filtering, CoreDNS egress rules, named ports, and CIDR IPBlock rules. | `netpol01` – `netpol04` (4) |
| **10** | **Lifecycle & Health Probes** | Liveness probes, readiness probes, startup probes (exec, httpGet, tcpSocket), and container lifecycle shutdown hooks (`preStop`). | `health01` – `health04` (4) |
| **11** | **Workload Autoscaling** | Horizontal Pod Autoscaler (`HPA` v2), custom scale-up/scale-down behaviors, Vertical Pod Autoscaler (`VPA`), and KEDA event autoscaling. | `autoscale01` – `autoscale04` (4) |
| **12** | **CRDs & Custom Operators** | CustomResourceDefinitions (`apiextensions.k8s.io/v1`), status subresources, printer columns, Python operator loops, and admission webhooks. | `crd01` – `crd04` (4) |
| **13** | **Troubleshooting & Incidents** | Diagnosing `CrashLoopBackOff`, OOMKilled, `ImagePullBackOff`, unschedulable pending pods, ResourceQuotas, and ephemeral debug containers. | `troubleshoot01` – `troubleshoot05` (5) |
| **14** | **GitOps & ArgoCD** | ArgoCD Application CRDs, automated sync policies, self-heal drift correction, ApplicationSets, and progressive delivery with Argo Rollouts. | `gitops01` – `gitops04` (4) |
| **15** | **Service Mesh & Cilium** | eBPF Layer 7 HTTP NetworkPolicies, strict mutual TLS (mTLS), clusterwide egress FQDN rules, and Hubble/OpenTelemetry mesh observability. | `mesh01` – `mesh04` (4) |
| **16** | **Policy as Code (Kyverno & Gatekeeper)** | Kyverno ClusterPolicies, mutate & generate rules, OPA Gatekeeper ConstraintTemplates and Rego admission policies. | `policy01` – `policy04` (4) |
| **17** | **Multi-Tenancy & Virtual Clusters** | Hierarchical Namespace Controller (HNC) subnamespaces, ResourceQuota limits, vcluster control planes, and isolation. | `tenant01` – `tenant04` (4) |
| **18** | **Advanced Admission Webhooks** | Dynamic MutatingWebhookConfigurations, ValidatingWebhookConfigurations, sidecar injection, and CRD conversion webhooks. | `webhook01` – `webhook04` (4) |

---

## Contributing

We welcome contributions, new exercises, bug fixes, and documentation improvements! Please check out [CONTRIBUTING.md](CONTRIBUTING.md) for local development setup, exercise authoring guidelines, and test instructions.

---

## License

Kubelings is distributed under the terms of the [Apache-2.0](LICENSE) license.

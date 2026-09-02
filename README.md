# Kubelings ☸️

[![CI](https://github.com/dnf0/kubelings/actions/workflows/ci.yml/badge.svg)](https://github.com/dnf0/kubelings/actions)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Type checker: pyright](https://img.shields.io/badge/types-pyright-green.svg)](https://github.com/microsoft/pyright)
[![Playground](https://img.shields.io/badge/Playground-⚡%20Launch%20Interactive%20IDE-blueviolet)](https://dnf0.github.io/kubelings/playground/)

> **An interactive, client-side WebAssembly learning platform and comprehensive reference manual for Kubernetes.**

---

## ⚡ Interactive WebAssembly Playground

Kubelings runs 100% in your browser using **Pyodide WebAssembly** and **Monaco Editor** (VS Code in the browser):

- 🌐 [**Launch Web Playground**](https://dnf0.github.io/kubelings/playground/)
- 📖 [**Read the 26-Chapter Reference Manual**](https://dnf0.github.io/kubelings/)

```text
┌────────────────────────────────────────────────────────────────────────┐
│                          Web Browser Tab                               │
│  ┌───────────────────────┐             ┌─────────────────────────────┐ │
│  │     Monaco Editor     │  YAML Edit  │  Web Worker (Pyodide Wasm)  │ │
│  │  (VS Code in Browser) ├────────────►│  • PyYAML Manifest Parser   │ │
│  └───────────────────────┘             │  • 26 Schema Validators     │ │
│                                        │  • Progressive Hint Engine  │ │
│  ┌───────────────────────┐             └──────────────┬──────────────┘ │
│  │   Interactive xterm   │◄───────────────────────────┘                │
│  │    Terminal Output    │         Instant Test & Validation Result    │
│  └───────────────────────┘         (< 1ms in WebAssembly)              │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 📚 Curriculum Structure (26 Chapters & 114 Exercises)

### Core Workloads & Storage
- **01. Pods & Core Workloads** (`pods01`–`pods06`): Pod specs, multi-container pods, initContainers, ports
- **02. Controllers & Replication** (`ctrl01`–`ctrl06`): Deployments, ReplicaSets, StatefulSets, DaemonSets, Jobs, CronJobs
- **03. Configuration & Secrets** (`config01`–`config05`): ConfigMaps, Secrets, projected volumes, envFrom
- **04. Storage & Persistent Volumes** (`storage01`–`storage05`): PVs, PVCs, StorageClasses, access modes, volumeMounts

### Networking & Traffic Routing
- **05. Services & Networking** (`net01`–`net05`): ClusterIP, NodePort, LoadBalancer, Headless services, Endpoints
- **06. Ingress & Gateway API** (`ingress01`–`ingress04`): Ingress controllers, path rules, TLS termination, annotations
- **21. Gateway API Deep Dive** (`gateway01`–`gateway04`): GatewayClass, Gateways, HTTPRoute, canary splits, ReferenceGrant
- **09. Network Policies** (`netpol01`–`netpol04`): Default deny, ingress/egress CIDR blocks, port rules

### Scheduling, Security & Scaling
- **07. Scheduling & Advanced Placement** (`sched01`–`sched05`): nodeSelector, node/pod affinity, taints, tolerations, topology spread
- **08. Security, RBAC & ServiceAccounts** (`rbac01`–`rbac05`): Roles, ClusterRoles, RoleBindings, SecurityContext, PSS/PSA
- **10. Health Probes & Lifecycle** (`health01`–`health04`): Liveness, readiness, startup probes, termination grace periods
- **11. Autoscaling (HPA, VPA, KEDA)** (`autoscale01`–`autoscale04`): Horizontal Pod Autoscaler v2, VPA, event-driven KEDA
- **18. Admission Webhooks** (`webhook01`–`webhook04`): Mutating, validating webhooks, sidecar injection, CRD conversion

### CRDs, Troubleshooting & Packaging
- **12. Custom Resources & Operators** (`crd01`–`crd04`): OpenAPI v3 schemas, subresources, reconciliation loops
- **13. Production Troubleshooting** (`troubleshoot01`–`troubleshoot05`): CrashLoopBackOff, ImagePullBackOff, Pending pods, ephemeral debug
- **19. Package Management with Helm** (`helm01`–`helm04`): Chart.yaml, Go templates, _helpers.tpl, values schemas, subcharts
- **20. Declarative Customization with Kustomize** (`kustomize01`–`kustomize04`): Bases, overlays, generators, strategic merge patches

### Modern Cloud Native Ecosystem
- **14. GitOps with ArgoCD** (`gitops01`–`gitops04`): Applications, ApplicationSets, sync policies, Argo Rollouts
- **15. Service Mesh & Cilium eBPF** (`mesh01`–`mesh04`): L7 routing, mTLS, FQDN egress, Hubble observability
- **16. Policy as Code (Kyverno & OPA)** (`policy01`–`policy04`): ClusterPolicies, mutating/generating rules, Gatekeeper constraints
- **17. Multi-Tenancy & Virtual Clusters** (`tenant01`–`tenant04`): HNC anchors, tenant quotas, vcluster control planes
- **22. Infrastructure as Data with Crossplane** (`crossplane01`–`crossplane04`): XRDs, Compositions, Managed Resources, claims
- **23. Kernel Security with eBPF Tetragon** (`tetragon01`–`tetragon04`): sys_execve tracing, credential monitoring, kernel Sigkill
- **24. Distributed AI Orchestration with KubeRay** (`ray01`–`ray04`): RayCluster, RayJob batch tuning, RayService serving
- **25. Batch AI Scheduling (Kueue & Volcano)** (`kueue01`–`volcano02`): ClusterQueue cohorts, gang scheduling, fair-share
- **26. Hardware Acceleration & DRA** (`accel01`–`accel04`): NVIDIA MIG, Apple Silicon GPU, DRA, vLLM serving

---

## 🛠️ Local Development & Contributing

### Setup

```bash
# Clone repository
git clone https://github.com/dnf0/kubelings.git
cd kubelings

# Create virtual environment and install dev dependencies
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

### Running Tests and Linting

```bash
# Run test suite
pytest

# Run linter and formatting
ruff check .
ruff format --check .

# Run type checks
pyright

# Build documentation locally
mkdocs serve
```

---

## 🌐 The *lings Ecosystem

If you enjoy the interactive learning model of **Kubelings**, explore the other platforms in our suite:

- 🏗️ [**Terralings**](https://github.com/dnf0/terralings) – Master Terraform and OpenTofu through interactive infrastructure-as-code exercises.
- 🇪🇸 [**Spanglings**](https://github.com/dnf0/spanglings) – Developer-grade CLI & interactive TUI for learning Spanish (B1–C1).
- ⚡ [**Raylings**](https://github.com/dnf0/raylings) – Learn distributed AI, Ray Core actors, and scalable clusters through hands-on Python exercises.

---

## 📄 License

Kubelings is open-source software licensed under the [Apache License 2.0](LICENSE).

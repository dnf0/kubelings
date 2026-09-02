# Kubelings ☸️

[![CI](https://github.com/dnf0/kubelings/actions/workflows/ci.yml/badge.svg)](https://github.com/dnf0/kubelings/actions)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Type checker: pyright](https://img.shields.io/badge/types-pyright-green.svg)](https://github.com/microsoft/pyright)
[![Playground](https://img.shields.io/badge/Playground-⚡%20Launch%20Interactive%20IDE-blueviolet)](https://dnf0.github.io/kubelings/playground/)

> **An interactive, client-side WebAssembly learning platform, CLI exercise runner, and comprehensive 29-chapter systems reference manual for Kubernetes.**

---

## ⚡ Two Ways to Learn

### 1. In Your Browser: Interactive WebAssembly Playground
Kubelings runs 100% client-side in your browser using **Pyodide WebAssembly** and **Monaco Editor** (VS Code in the browser):

- 🌐 [**Launch Web Playground**](https://dnf0.github.io/kubelings/playground/)
- 📖 [**Read the 29-Chapter Systems Reference Manual**](https://dnf0.github.io/kubelings/)

```text
┌────────────────────────────────────────────────────────────────────────┐
│                          Web Browser Tab                               │
│  ┌───────────────────────┐             ┌─────────────────────────────┐ │
│  │     Monaco Editor     │  YAML Edit  │  Web Worker (Pyodide Wasm)  │ │
│  │  (VS Code in Browser) ├────────────►│  • PyYAML Manifest Parser   │ │
│  └───────────────────────┘             │  • 29 Schema Validators     │ │
│                                        │  • Progressive Hint Engine  │ │
│  ┌───────────────────────┐             └──────────────┬──────────────┘ │
│  │   Interactive xterm   │◄───────────────────────────┘                │
│  │    Terminal Output    │         Instant Test & Validation Result    │
│  └───────────────────────┘         (< 1ms in WebAssembly)              │
└────────────────────────────────────────────────────────────────────────┘
```

### 2. In Your Terminal: Native CLI Runner
Prefer your local editor and terminal? Run exercises locally with instant feedback:

```bash
# Install kubelings
pip install kubelings

# Start interactive watch mode (re-validates whenever you save a YAML file)
kubelings watch

# Verify a single exercise
kubelings verify pods01

# Get progressive hints when stuck
kubelings hint pods01

# List all 29 chapters and 126 exercises
kubelings list
```

---

## 📚 Complete Curriculum Matrix (29 Chapters & 126 Exercises)

### 🧱 Track 1: Core Workloads & Storage
- **01. Pods & Core Workloads** (`pods01`–`pods06`): Pod specs, multi-container pods, initContainers, resource requests/limits, Downward API, PDBs
- **02. Controllers & Replication** (`ctrl01`–`ctrl06`): Deployments, ReplicaSets, StatefulSets, DaemonSets, Jobs, CronJobs
- **03. Configuration & Secrets** (`config01`–`config05`): ConfigMaps, Secrets, projected volume mounts, envFrom, atomic symlink updates
- **04. Storage & Persistent Volumes** (`storage01`–`storage05`): PVs, PVCs, StorageClasses, access modes, CSI volume plugins, volumeMounts

### 🌐 Track 2: Networking, Traffic Routing & Service Mesh
- **05. Services & Networking** (`net01`–`net05`): ClusterIP, NodePort, LoadBalancer, Headless services, EndpointSlices, Netfilter/IPVS
- **06. Ingress & Gateways** (`ingress01`–`ingress04`): Ingress controllers, path rules, TLS termination, annotations, SNI routing
- **21. Gateway API Deep Dive** (`gateway01`–`gateway04`): GatewayClass, Gateways, HTTPRoute, canary splits, xDS dynamic routing
- **09. Network Policies** (`netpol01`–`netpol04`): Default deny, ingress/egress CIDR blocks, port rules, eBPF map filtering
- **15. Service Mesh & Cilium eBPF** (`mesh01`–`mesh04`): L7 routing, sockops socket short-circuiting, WireGuard encryption, Hubble observability

### 🛡️ Track 3: Scheduling, Security & Lifecycle
- **07. Scheduling & Advanced Placement** (`sched01`–`sched05`): nodeSelector, node/pod affinity, taints, tolerations, topology spread
- **08. Security, RBAC & ServiceAccounts** (`rbac01`–`rbac05`): Roles, ClusterRoles, RoleBindings, SecurityContext, Pod Security Standards (PSS/PSA)
- **10. Health Probes & Lifecycle** (`health01`–`health04`): Liveness, readiness, startup probes, termination grace periods, PID 1 signals
- **11. Autoscaling (HPA, VPA, KEDA)** (`autoscale01`–`autoscale04`): Horizontal Pod Autoscaler v2, VPA, event-driven KEDA, Karpenter capacity
- **16. Policy as Code (Kyverno & OPA)** (`policy01`–`policy04`): ClusterPolicies, mutating/generating rules, Gatekeeper constraints, Sigstore Cosign
- **18. Admission Webhooks** (`webhook01`–`webhook04`): Mutating, validating webhooks, JSONPatch RFC 6902, mTLS authentication

### ⚙️ Track 4: Production Operations, GitOps & Packaging
- **12. Custom Resources & Operators** (`crd01`–`crd04`): OpenAPI v3 schemas, subresources, reconciliation loops, finalizers
- **13. Production Troubleshooting** (`troubleshoot01`–`troubleshoot05`): CrashLoopBackOff, ImagePullBackOff, Pending pods, OOMKilled exit 137, ephemeral debug
- **14. GitOps with ArgoCD** (`gitops01`–`gitops04`): Applications, ApplicationSets, sync policies, self-healing drift correction
- **17. Multi-Tenancy & Virtual Clusters** (`tenant01`–`tenant04`): HNC anchors, tenant quotas, vcluster control plane isolation
- **19. Package Management with Helm** (`helm01`–`helm04`): Chart.yaml, Go templates, _helpers.tpl, values schemas, subcharts, release Secrets
- **20. Declarative Customization with Kustomize** (`kustomize01`–`kustomize04`): Bases, overlays, generators, strategic merge patches, hash suffixes

### ☁️ Track 5: Cloud Providers, Distributed AI & Modern Infrastructure
- **22. Infrastructure as Data with Crossplane** (`crossplane01`–`crossplane04`): XRDs, Compositions, Managed Resources, cloud provider SDKs
- **23. Kernel Security with eBPF Tetragon** (`tetragon01`–`tetragon04`): sys_execve tracing, credential monitoring, synchronous in-kernel Sigkill
- **24. Distributed AI Orchestration with KubeRay** (`ray01`–`ray04`): RayCluster, Plasma shared memory object stores, NCCL GPU tensor sync
- **25. Batch AI Scheduling (Kueue & Volcano)** (`kueue01`–`volcano02`): ClusterQueue cohorts, gang all-or-nothing scheduling, fair-share
- **26. Hardware Acceleration & DRA** (`accel01`–`accel04`): NVIDIA MIG, Apple Silicon GPU, Dynamic Resource Allocation (DRA), CDI drivers
- **27. AWS EKS Cloud Architecture** (`eks01`–`eks04`): IRSA, AWS Load Balancer Controller IP-mode, Karpenter node provisioning, EKS Pod Identity
- **28. GCP GKE Cloud Ecosystem** (`gke01`–`gke04`): Workload Identity Federation, GKE Metadata Server, GKE Autopilot, Cloud Armor WAF
- **29. Enterprise Multi-Account Governance & Secrets** (`eso01`, `vault01`, `gov01`, `gov02`): Multi-account landing zones, External Secrets Operator (ESO), HashiCorp Vault Agent sidecars, ArgoCD ApplicationSet Matrix Generators

---

## 🔍 Deep Systems-Level Reference Manual

Every chapter in the [Reference Manual](https://dnf0.github.io/kubelings/) includes an under-the-hood systems engineering walkthrough:

- 🔄 **Lifecycle & Request Paths**: Step-by-step traces from `kubectl apply` to `kube-apiserver` admission, `etcd` MVCC persistence, `kube-scheduler` filters, `kubelet` PLEG sync loops, and container runtime execution.
- ⚡ **Protocols & Serialization**: Low-level wire specifications covering CRI/CSI gRPC over `/run/containerd/containerd.sock`, Protocol Buffers, JSONPatch RFC 6902, OpenAPI v3, and Envoy xDS dynamic streaming.
- 🐧 **Linux Kernel Datapath**: Deep breakdowns of cgroups v2 (`cpu.max`, `memory.max`), Linux namespaces (`CLONE_NEWNET`, `CLONE_NEWPID`), Netfilter conntrack tables, eBPF socket maps (`sockops`), and OOM scoring (`oom_score_adj`).

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
# Run full test suite (1,110+ tests)
pytest

# Run linter and formatting
ruff check .
ruff format --check .

# Run static type checks
pyright

# Build documentation locally
mkdocs serve
```

---

## 🌐 The *lings Ecosystem

If you enjoy the interactive learning model of **Kubelings**, explore the other platforms in our suite:

- 🏗️ [**Terralings**](https://github.com/dnf0/terralings) – Master Terraform and OpenTofu through interactive infrastructure-as-code exercises.
- ⚡ [**Raylings**](https://github.com/dnf0/raylings) – Learn distributed AI, Ray Core actors, and scalable clusters through hands-on Python exercises.
- 🇪🇸 [**Spanglings**](https://github.com/dnf0/spanglings) – Developer-grade CLI & interactive TUI for learning Spanish (B1–C1).

---

## 📄 License

Kubelings is open-source software licensed under the [Apache License 2.0](LICENSE).

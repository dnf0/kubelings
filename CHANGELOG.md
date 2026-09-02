# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Full 114-Exercise Browser WebAssembly Learning Platform (`docs/playground.md`)**: Expanded the Pyodide WebAssembly learning platform to include all 114 exercises across 26 curriculum chapters.
- **Client-Side State Engine (`KubelingsStorage`)**: Implemented debounced `localStorage` auto-saving for user code, progressive hint tracking, exercise completion flags, and global progress calculation (`X / 114 Completed • Y%`).
- **Curriculum Syllabus Sidebar**: Added split-pane UI featuring a collapsible 26-chapter accordion tree, live search filtering, completion badges, and status tabs (All, To Do, Done).
- **Progress Import & Export**: Enabled one-click JSON progress backup export (`kubelings-progress-YYYY-MM-DD.json`) and restoration across browsers/devices.
- **Keyboard Navigation**: Added `Alt+Left` / `Alt+Right` sequential navigation shortcuts and inline Next Exercise advancement upon test pass.

## [0.9.11] - 2026-08-28

### Changed
- **Native YAML Curriculum Architecture**: Converted all 114 exercises across all 26 chapters from Python scripts with embedded string literals into pure `.yaml` manifests. Learners now get full editor syntax highlighting, bracket matching, indentation guides, and Kubernetes JSON schema autocompletion out of the box.
- **Decoupled Core Validator Engine**: Extracted all test assertion logic out of user exercise files into 26 modular chapter validator packages (`src/kubelings/validators/ch01_pods.py` through `ch26_hardware_acceleration_dra.py`) utilizing a decorator-based dynamic discovery registry (`@register_validator`).
- **Human-Friendly YAML Diagnostics**: Replaced confusing Python stack traces with visual, colored YAML syntax diagnostics (`format_yaml_error`) displaying precise line/column coordinates and code pointer snippets on syntax mistakes (e.g. duplicate keys, indentation errors).
- **VS Code Extension Modernization (`dnf0.kubelings-vscode@0.9.11`)**: Updated path resolution engine (`pathUtils.ts`) to prioritize `.yaml` -> `.yml` -> `.py` candidate resolution, contributed `kubelings.openSolution` and `kubelings.resetExercise` commands, and enabled real-time YAML document diagnostics on save.
- **Playground Bundle Streamlining**: Updated `scripts/build_playground_bundle.py` to directly bundle pure YAML starter and solution manifests for the WebAssembly browser playground.

### Added
- **Interactive WebAssembly Browser Playground (`docs/playground.md`)**: Zero-install client-side learning environment powered by Pyodide (Python 3.12 WebAssembly), Monaco Editor, PyYAML, and the in-memory Kubelings schema validator. Features split-pane layout, progressive hints (`💡 Reveal Hint`), side-by-side Monaco diff inspection (`🔍 Compare Solution`), dark/light theme synchronization with MkDocs Material, and 11 flagship showcase exercises across all 6 learning tiers (Pods, Controllers, ConfigMaps, Storage, Scheduling, Network Policies, Autoscaling, GitOps, Gateway API, KubeRay, and Apple Silicon GPU acceleration).
- **Playground Bundle Pipeline & Pytest Suite**: Automated bundle generator (`scripts/build_playground_bundle.py`) compiling validator logic, Pydantic/dataclass models, and 11 flagship exercise specs into `docs/assets/playground/playground-bundle.json`, covered by automated `pytest` tests (`tests/test_playground_bundle.py`).
- **Pyodide Web Worker Background Engine (`docs/assets/playground/playground-worker.js`)**: Dedicated Web Worker offloading Python WebAssembly runtime initialization, virtual `/lib/kubelings` filesystem mounting, and AST code execution off the main UI thread.
- **Tier 6: AI & ML Platform Engineering Track (Chapters 24–26, 12 Exercises)**:
  - **Chapter 24 (Distributed AI & ML with KubeRay)**: RayCluster core architectures, heterogeneous CPU/GPU worker pools, RayJob batch fine-tuning, and RayService LLM serving (`ray01`–`ray04`).
  - **Chapter 25 (AI Batch Scheduling with Kueue & Volcano)**: Kueue ResourceFlavors/ClusterQueues cohort borrowing, LocalQueue suspended job gating, Volcano gang scheduling (`minAvailable`), and fair-share queueing (`kueue01`–`volcano02`).
  - **Chapter 26 (Hardware Acceleration, Apple Silicon & DRA)**: NVIDIA MIG slicing (`mig-3g.40gb`), Apple Silicon GPU & Metal MPS acceleration (`apple.com/gpu`, `PYTORCH_ENABLE_MPS_FALLBACK`), Dynamic Resource Allocation (DRA) ResourceClaimTemplates, and production vLLM inference server (`accel01`–`accel04`).
- **Curriculum Expansion**: Expanded full curriculum to **26 chapters** and **114 exercises** across 6 progressive learning tiers with complete reference solutions, validator test coverage, and IDE integration.
- **Interactive Onboarding Tour (`kubelings tour`)**: Rich 5-step terminal onboarding tour with live runtime/cluster probes, pedagogical philosophy, inner learning loop and hotkeys explanation, guided first exercise (`pods01`) resolution with error inspection and solution diffing, and VS Code extension tooling setup. Supports `--step`, `--non-interactive`, and `--json` flags.
- **VS Code Extension Native Walkthrough**: Declarative welcome walkthrough (`contributes.walkthroughs` in `package.json` with `kubelings.walkthrough`) featuring 5 markdown stages (`welcome.md`, `cluster.md`, `watch.md`, `exercise.md`, `quickfixes.md`), `Kubelings: Open Welcome Walkthrough` command, and `KubelingsCliBridge.tour()` method.
- **Comprehensive Learner's Onboarding Guide (`docs/onboarding-guide.md`)**: In-depth illustrated tutorial covering quickstart zero-install runs (`uvx kubelings tour`), the inner loop workflow, step-by-step resolution of `pods01.py`, VS Code integration, 6-tier curriculum progression roadmap (114 exercises across 26 chapters), and an essential commands cheat sheet.
- **CLI JSON Serialization**: Added `--json` flag support across `kubelings tour`, `kubelings list`, and `kubelings verify` commands for seamless IDE integration.
- **Full 13-Chapter Curriculum (62 Exercises)**:
  - **Chapter 01 (Pods & Core Workloads)**: Pod manifests, multi-container sidecars, init containers, resource requests/limits, Downward API, and Pod Disruption Budgets (`pods01`–`pods06`).
  - **Chapter 02 (Controllers & Replication)**: ReplicaSets, Deployments, rolling updates, rollbacks, StatefulSets, DaemonSets, and Jobs/CronJobs (`ctrl01`–`ctrl06`).
  - **Chapter 03 (Configuration & Secrets)**: ConfigMaps, Secrets, environment injection, volume mounts, permission modes, and immutable configs (`config01`–`config05`).
  - **Chapter 04 (Storage & Persistent Volumes)**: `emptyDir`, `hostPath`, PVs, PVCs, access modes, reclaim policies, StorageClasses, and volume snapshots (`storage01`–`storage05`).
  - **Chapter 05 (Services & Networking)**: ClusterIP, Headless services, NodePort, LoadBalancer, CoreDNS resolution, ExternalName, and manual Endpoints (`net01`–`net05`).
  - **Chapter 06 (Ingress & Gateway API)**: Ingress routing rules, TLS termination, URL rewrite annotations, and Gateway API (`ingress01`–`ingress04`).
  - **Chapter 07 (Scheduling & Placement)**: `nodeSelector`, node affinity (hard/soft), pod affinity/anti-affinity, taints, tolerations, and topology spread constraints (`sched01`–`sched05`).
  - **Chapter 08 (Security & RBAC)**: ServiceAccounts, token management, Roles, RoleBindings, ClusterRoles, `securityContext`, and Pod Security Standards (`rbac01`–`rbac05`).
  - **Chapter 09 (Network Policies)**: Default Deny, Ingress/Egress traffic filtering, DNS policy rules, named ports, and IPBlock CIDR rules (`netpol01`–`netpol04`).
  - **Chapter 10 (Lifecycle & Health Probes)**: Liveness, readiness, startup probes (exec/httpGet/tcpSocket), and graceful termination `preStop` hooks (`health01`–`health04`).
  - **Chapter 11 (Workload Autoscaling)**: Horizontal Pod Autoscaler (HPA v2), custom scaling policies, Vertical Pod Autoscaler (VPA), and KEDA event-driven autoscaling (`autoscale01`–`autoscale04`).
  - **Chapter 12 (CRDs & Custom Operators)**: CustomResourceDefinitions (`apiextensions.k8s.io/v1`), status subresources, printer columns, Python operator reconciliation loops, and admission webhooks (`crd01`–`crd04`).
  - **Chapter 13 (Troubleshooting & Incidents)**: Diagnosing `CrashLoopBackOff`, OOMKilled exit codes, `ImagePullBackOff`, unschedulable pending pods, ResourceQuotas, and ephemeral debug containers (`troubleshoot01`–`troubleshoot05`).
- **Core Engine & Architecture**:
  - Interactive file watcher (`kubelings watch`) powered by `watchdog` with automated exercise advancement upon removal of `# I AM NOT DONE`.
  - Sub-30ms offline schema validation and specification verification engine in `kubelings.validator`.
  - Dual-mode live cluster detection and ephemeral test namespace adapter in `kubelings.cluster`.
  - Rich terminal user interface in `kubelings.ui` and Typer CLI in `kubelings.cli` supporting `watch`, `run`, `hint`, `list`, `verify`, `cluster`, `version`, and `test` commands.
- **Verification & Testing**:
  - Master end-to-end test suite (`tests/test_solutions_and_exercises.py`) verifying all 62 reference solutions pass and all 62 starter exercises fail before completion.
  - Granular chapter test suites covering offline and live reconciliation logic.
  - Complete reference solutions for every exercise in `solutions/`.

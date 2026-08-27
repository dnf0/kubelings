# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- **Pure Test-Driven Validation**: Retired the `# I AM NOT DONE` magic comment requirement across all 102 curriculum exercises. Exercise completion is now purely evaluated via test assertions and schema validation.
- **Interactive Navigation**: Added `[n]` / `[Enter]` to advance to the next exercise and `[p]` to navigate to the previous exercise directly within the terminal watcher.
- **VS Code Extension**: Streamlined on-save diagnostics to emit error squiggles on genuine validation/assertion failures without requiring comment removal.

### Added
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

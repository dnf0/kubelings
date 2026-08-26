# Kubelings ☸️

An interactive, terminal-driven hands-on learning environment for mastering Kubernetes from scratch.

Inspired by the pedagogy and developer experience of `rustlings`, `ziglings`, and `raylings`, **Kubelings** guides learners through hands-on, self-paced exercises. You will fix broken YAML manifests, construct multi-container sidecars, configure persistent storage, write RBAC policies, solve scheduling constraints, build custom Python Kubernetes operators, and troubleshoot production cluster incidents.

---

## Features

- **Interactive File Watcher (`watch`)**: Automatically validates exercises as you edit and save YAML and Python files.
- **Fast Offline Validation**: Sub-30ms in-memory Kubernetes OpenAPI schema and specification verification without requiring a live cluster.
- **Optional Live Cluster Adapter**: Test and reconcile deployments against a local `kind`, `minikube`, or `k3s` cluster in isolated ephemeral namespaces.
- **Progressive Hints (`hint`)**: Tiered hints guide you step-by-step when you get stuck.
- **Structured Curriculum**: 13 comprehensive chapters spanning 55 practical exercises.

---

## Installation

### Prerequisites

- Python `>= 3.10`
- `pip` or [`uv`](https://github.com/astral-sh/uv)
- (Optional) `kubectl` and a local Kubernetes cluster (`kind` / `minikube` / `k3d`) for live reconciliation exercises.

### Install from Source

```bash
git clone https://github.com/dnf0/kubelings.git
cd kubelings
pip install -e .
```

For development:

```bash
pip install -e ".[dev]"
```

---

## Usage

### Watch Mode (Recommended)

Start the interactive watch loop that observes your exercise files and re-runs validation on save:

```bash
kubelings watch
```

Remove the `# I AM NOT DONE` comment from the top of the exercise file once you have solved it, and `kubelings` will automatically advance to the next exercise.

### Run a Single Exercise

```bash
kubelings run exercises/01_pods/pods01.py
```

### Get a Hint

```bash
kubelings hint pods01
```

### List All Exercises and Progress

```bash
kubelings list
```

### Verify All Completed Exercises

```bash
kubelings verify
```

---

## Syllabus & Curriculum

1. **Chapter 1: Pods & Core Workloads (`01_pods`)** — Pod manifests, multi-container sidecars, init containers, resource requests/limits, Downward API, PDBs.
2. **Chapter 2: Controllers & Replication (`02_controllers`)** — ReplicaSets, Deployments, rollbacks, StatefulSets, DaemonSets, Jobs/CronJobs.
3. **Chapter 3: Configuration & Secrets (`03_config_secrets`)** — ConfigMaps, Secrets, volume mounts, immutable configs.
4. **Chapter 4: Storage & Persistent Volumes (`04_storage`)** — `emptyDir`, `hostPath`, PVs, PVCs, StorageClasses, volume expansion.
5. **Chapter 5: Services & Networking (`05_services_networking`)** — ClusterIP, Headless Services, NodePort, LoadBalancer, CoreDNS, Endpoints.
6. **Chapter 6: Ingress & Gateway API (`06_ingress_gateway`)** — Ingress routing rules, TLS termination, URL rewrite annotations, Gateway API.
7. **Chapter 7: Scheduling & Affinity (`07_scheduling`)** — NodeSelector, Node Affinity, Pod Anti-Affinity, Taints/Tolerations, Topology Spread Constraints.
8. **Chapter 8: Security, RBAC & Service Accounts (`08_security_rbac`)** — ServiceAccounts, Roles, RoleBindings, ClusterRoles, SecurityContext, Pod Security Standards.
9. **Chapter 9: Network Policies (`09_network_policies`)** — Default Deny, ingress/egress filtering, IPBlock CIDR rules, named ports.
10. **Chapter 10: Lifecycle & Health Probes (`10_lifecycle_probes`)** — Liveness, readiness, and startup probes, graceful termination hooks.
11. **Chapter 11: Autoscaling & Resource Management (`11_autoscaling`)** — HorizontalPodAutoscaler (HPA), metrics server integration, VPA, cluster limits.
12. **Chapter 12: CRDs & Kubernetes Operators (`12_crds_and_operators`)** — Custom Resource Definitions, OpenAPI v3 validation schemas, Python reconciliation loops.
13. **Chapter 13: Troubleshooting Production Incidents (`13_troubleshooting`)** — Debugging `CrashLoopBackOff`, OOMKilled, ImagePullBackOff, and scheduling deadlocks.

---

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for development workflows, testing guidelines, and conventions.

---

## License

Distributed under the Apache 2.0 License. See [LICENSE](LICENSE) for more information.

# Welcome to Kubelings ☸️

**Kubelings** is an interactive, test-driven learning environment for Kubernetes. Inspired by Rustlings and Ziglings, Kubelings guides you from container fundamentals to production-grade Kubernetes architecture through hands-on micro-exercises.

---

### 🎓 Core Pedagogical Philosophy

1. **Active Debugging**: Every exercise starts in an intentionally broken or incomplete state with `???` placeholders. You learn by diagnosing errors and fixing them.
2. **Sub-30ms Instant Feedback**: Schema assertions and manifest evaluations run locally in-memory with zero cluster latency.
3. **Test-Driven Mastery**: Exercises pass only when genuine Kubernetes OpenAPI schemas and validation rules are satisfied.

---

### 📚 Comprehensive 23-Chapter Curriculum

Kubelings covers 23 comprehensive chapters comprising 100+ micro-exercises:

- **Core Workloads**: Pods, ReplicaSets, Deployments, StatefulSets, DaemonSets, Jobs, CronJobs
- **Networking & Discovery**: Services (ClusterIP, NodePort, LoadBalancer), Ingress, NetworkPolicies, CoreDNS
- **Configuration & Secrets**: ConfigMaps, Secrets, downward API, Environment Variables
- **Storage & State**: Volumes, PersistentVolumes (PV), PersistentVolumeClaims (PVC), StorageClasses
- **Security & Access**: ServiceAccounts, RBAC (Roles, ClusterRoles, RoleBindings), SecurityContexts
- **Reliability & Scaling**: Probes (liveness/readiness/startup), Resource Requests & Limits, HPA, PodDisruptionBudgets
- **Advanced & Operators**: Custom Resource Definitions (CRDs), Custom Controllers, Helm, Kustomize, Multi-tenancy, Incident Troubleshooting

---

[Start Watch Mode](command:kubelings.startWatch)
[Refresh Curriculum](command:kubelings.refresh)

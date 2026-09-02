# Design Specification: 26-Chapter Mermaid.js Architectural Diagrams

## Overview & Goals

Replace all 26 legacy ASCII text boxes in the Kubelings Reference Manual (`docs/guides/*.md`) with production-grade, theme-aware, responsive **Mermaid.js** diagrams (`flowchart TD/LR` and `sequenceDiagram`).

### Key Objectives
1. **Clarity & Depth**: Accurately illustrate Kubernetes control planes, reconciliation loops, Linux kernel/eBPF data paths, CRI/CNI/CSI handoffs, and distributed systems topology.
2. **Theme Integration**: Fully compatible with Material for MkDocs dark (`slate`) and light (`default`) mode palettes.
3. **Structured Subgraphs**: Clearly delineate *Control Plane*, *Node Worker / Kubelet*, *Pod Sandboxes*, and *External Infrastructure*.
4. **Zero Broken Layouts**: Eliminate fixed-width text wrapping issues on mobile and tablet screens.

---

## Technical Configuration

### 1. `mkdocs.yml` Extension Configuration
Configure `pymdownx.superfences` custom fences in `mkdocs.yml`:

```yaml
markdown_extensions:
  - pymdownx.superfences:
      custom_fences:
        - name: mermaid
          class: mermaid
          format: !!python/name:pymdownx.superfences.fence_code_format
```

---

## Chapter-by-Chapter Architectural Diagrams

| Chapter | Topic | Diagram Type | Core Subgraphs / Flow |
| :--- | :--- | :--- | :--- |
| **01** | **Pods & Core Workloads** | `flowchart TD` | API Server → Kubelet → CRI Container Runtime → Init Container sequential barrier → Main & Sidecar containers with shared `emptyDir` |
| **02** | **Controllers & Replication** | `flowchart TD` | `kube-controller-manager` Deployment Controller → ReplicaSets (Revision History) → Desired Pod Replicas → Node Placement |
| **03** | **Config & Secrets** | `flowchart LR` | ConfigMaps & Secrets (Envelope Encryption) → Atomic Symlink Volume Projection (`..data`) vs Env Var Injections → Application Process |
| **04** | **Storage & CSI Volumes** | `flowchart TD` | PVC Claim → CSI External Provisioner → Storage Provider → CSI Attacher → Node CSI Driver Mount → Pod Container Mount |
| **05** | **Services & Networking** | `flowchart TD` | CoreDNS Discovery → Service ClusterIP / NodePort / LB VIP → `kube-proxy` (iptables / IPVS) & EndpointSlice → Backend Pod IPs |
| **06** | **Ingress & Gateway** | `flowchart TD` | Edge Client → Cloud Load Balancer → Ingress Controller (Envoy/NGINX) → L7 Routing Rules (Host/Path) → Service Endpoints |
| **07** | **Scheduling & Placement** | `flowchart TD` | Scheduler Pipeline (Filter → Score → Reserve → Permit → PreBind → Bind) with Node Affinity, Taints/Tolerations, Topology Spread |
| **08** | **Security & RBAC** | `flowchart LR` | Request Authentication (X.509/OIDC) → RBAC Evaluation (`ClusterRoleBinding` → `Role` → Rule Verbs) → Admission SecurityContext |
| **09** | **Network Policies & CNI** | `flowchart TD` | Pod Ingress/Egress packet traversal → CNI Firewall Engine (eBPF / iptables) → CIDR / PodSelector / NamespaceSelector filter rules |
| **10** | **Lifecycle & Health Probes** | `flowchart TD` | Kubelet Probe Manager (Startup → Liveness → Readiness) → Pod Conditions → EndpointSlice traffic gating & container restart policy |
| **11** | **Autoscaling & Capacity** | `flowchart TD` | Metrics Server & Prometheus → HPA Controller PID reconciliation loop → Deployment Replicas → Cluster Autoscaler / Karpenter Node scaling |
| **12** | **CRDs & Python Operators** | `flowchart TD` | CRD OpenAPI Schema → Custom Controller Informer Cache → Event Queue → Reconciler Loop (`kopf` / `kube-rs`) → Status Subresource |
| **13** | **Troubleshooting Triage** | `flowchart TD` | Failure Decision Tree: `Pending` (Resource/Taint) → `CrashLoopBackOff` (Exit Code/Logs) → `OOMKilled` (Memory Limits) → Service 503 |
| **14** | **GitOps & ArgoCD** | `flowchart LR` | Git Repository Source of Truth → ArgoCD Repo Server → Application Controller (Live vs Desired Diff) → Self-Heal / Auto-Prune |
| **15** | **Service Mesh & Cilium eBPF**| `flowchart TD` | Linux Kernel Socket Layer (`sockops` / `tc-bpf`) → Cilium Agent → Envoy L7 Proxy → mTLS SPIFFE Encryption → Hubble Observability |
| **16** | **Policy-as-Code** | `flowchart TD` | API Admission Review → Kyverno / Gatekeeper Engine → Mutate / Validate / Generate / VerifyImage → Allowed or Denied Response |
| **17** | **Multi-Tenancy & vcluster** | `flowchart TD` | Tenant Namespace → Virtual API Server & k3s etcd → Syncer Process → Super-Cluster Physical Worker Nodes & Quotas |
| **18** | **Admission Webhooks** | `flowchart TD` | API Request → Mutating Webhook (TLS Service) → Schema Validation → Validating Webhook → etcd Persistence |
| **19** | **Helm Packaging** | `flowchart LR` | Helm CLI → Template Engine (`values.yaml` + `Chart.yaml`) → Release Secret Version (`sh.helm.release.v1`) → Live Manifests |
| **20** | **Kustomize Overlays** | `flowchart LR` | Base Manifests → Overlay Kustomization (`patchesStrategicMerge`, `namePrefix`, `configMapGenerator`) → Target Env Output |
| **21** | **Gateway API** | `flowchart TD` | `GatewayClass` (Infra) → `Gateway` (Cluster Ops) → `HTTPRoute` / `GRPCRoute` (App Dev) → Multi-Service Backend Routing |
| **22** | **Crossplane Infrastructure** | `flowchart TD` | Composite Resource Claim (`XRC`) → Composite Resource (`XR`) → `Composition` Engine → Managed Resources (AWS/GCP/Azure Cloud APIs) |
| **23** | **Tetragon eBPF Security** | `flowchart TD` | Linux Kernel Tracepoints & Kprobes → Tetragon BPF Sensor → Filtering & Enforcement (Kill / Block) → Real-Time Security Stream |
| **24** | **KubeRay Distributed ML** | `flowchart TD` | `RayCluster` CR → KubeRay Operator → Ray Head (GCS / Dashboard) & Ray Workers (Plasma Shared Memory) → Distributed Training |
| **25** | **Batch (Kueue & Volcano)** | `flowchart TD` | Volcano Scheduler (Gang Scheduling, PodGroup, Binpacking) + Kueue ResourceFlavor & Cohort Workload Queue Admission |
| **26** | **Hardware Acceleration & DRA**| `flowchart TD` | Dynamic Resource Allocation (DRA) Controller → `ResourceClaim` → CDI Device Plugin → GPU / TPU / FPGA Hardware Sandbox |

---

## Verification & Quality Gates

1. **Strict Build**: `uv run mkdocs build --strict` (0 errors, 0 warnings).
2. **Automated Tests**: Update `tests/test_reference_guides.py` to verify that all 26 guides contain valid Mermaid diagrams (````mermaid ... ````) and 0 unformatted ASCII blocks in Section 1.
3. **Pytest Suite**: All 969 unit and schema tests passing.
4. **Linter & Types**: `uv run ruff check .` and `uv run pyright` passing cleanly.

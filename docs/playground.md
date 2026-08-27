# ☸️ Interactive WebAssembly Playground

> **Zero installation, 100% client-side execution.** Practice and debug Kubernetes manifests directly in your browser.

The **Kubelings WebAssembly Playground** compiles Python 3.12, PyYAML, and the full Kubelings AST and schema validation engine into WebAssembly via **[Pyodide](https://pyodide.org/)**. Everything runs entirely inside your browser tab using an isolated Web Worker—no remote servers, backend APIs, or local Docker/Kubernetes installations required.

---

<div id="kubelings-playground" class="kubelings-playground"></div>

<link rel="stylesheet" href="../assets/playground/playground.css" />
<script src="../assets/playground/playground.js"></script>

---

## 🚀 Playground Quick Tips & Features

### ⌨️ Keyboard Shortcuts
- **`Ctrl+Enter`** / **`Cmd+Enter`**: Instantly execute in-memory validation against the current manifest.
- **`Tab`** / **`Shift+Tab`**: Indent / outdent YAML blocks cleanly inside the Monaco Editor.
- **`Esc`**: Dismiss hint banners or diff mode overlays.

### 💡 Progressive Hinting
Click **`💡 Reveal Hint`** to cycle through multi-tiered progressive clues. Hints provide conceptual guidance, syntax pointers, and spec references without giving away the full answer.

### 🔍 Reference Solution Comparison
Click **`🔍 Compare Solution`** to toggle an interactive side-by-side **Monaco Diff Editor**. Inspect exact additions, deletions, and structural differences between your working code and the official reference solution.

### 🌐 Showcase Range & Flagship Exercises
Switch exercises using the dropdown menu above. The playground showcases 11 flagship exercises spanning all 6 learning tiers:

| Exercise ID | Tier | Topic | Key Concepts Covered |
| :--- | :--- | :--- | :--- |
| `pods01` | **Tier 1: Core Workloads** | First Pod Manifest & Spec | Container ports, labels, image spec |
| `ctrl01` | **Tier 1: Core Workloads** | Deployments & ReplicaSets | Rolling update strategy, matchLabels selector |
| `config01` | **Tier 1: Core Workloads** | ConfigMaps & Environment Injection | `valueFrom.configMapKeyRef`, env vars |
| `storage01` | **Tier 1: Core Workloads** | PersistentVolumes & PVCs | Storage classes, access modes, capacity |
| `sched01` | **Tier 2: Scheduling & NetPol** | Node Affinity & Taints | `nodeSelector`, `requiredDuringSchedulingIgnoredDuringExecution` |
| `netpol01` | **Tier 2: Scheduling & NetPol** | Network Policies & Default Deny | Ingress/Egress CIDR, podSelector |
| `autoscale01` | **Tier 3: Operations & Scale** | Horizontal Pod Autoscaler (HPA v2)| Target CPU/Memory metric utilization |
| `gitops01` | **Tier 4: GitOps & CRDs** | GitOps Sync with Flux / ArgoCD | GitRepository, Kustomization reconciliation |
| `gateway01` | **Tier 5: Cloud Native Ingress** | Gateway API HTTPRoutes | Gateway listeners, HTTPRoute rules |
| `ray01` | **Tier 6: AI & GPU Acceleration** | KubeRay Distributed AI Cluster | RayCluster head/worker pods, rayVersion |
| `accel02` | **Tier 6: AI & GPU Acceleration** | Apple Silicon & Metal MPS Acceleration | `apple.com/gpu`, Metal MPS fallback |

---

## 💻 Ready for the Full Experience?

The playground is a browser preview of the Kubelings learning engine. For the complete curriculum of **114 exercises across 26 chapters**, terminal watch mode, live cluster verification, and the official VS Code / Cursor extension:

```bash
# Launch the interactive terminal onboarding tour
uvx kubelings tour

# Initialize exercises locally and start watch mode
uvx kubelings init
uvx kubelings watch
```

Check out the [**Learner's Onboarding Guide**](onboarding-guide.md) or explore the [**Curriculum Syllabus**](syllabus.md).

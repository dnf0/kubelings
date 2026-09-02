# Design Document: Kubelings Pure Web Platform & 26-Chapter Kubernetes Reference Guides

- **Date:** 2026-09-02
- **Author:** Daniel Fisher & Antigravity
- **Status:** Approved
- **Repository:** `dnf0/kubelings`

---

## 1. Executive Summary & Vision

**Kubelings** is transitioning into a **100% client-side WebAssembly Kubernetes learning platform and comprehensive reference manual**.

By sunsetting the legacy CLI runner and local cluster dependencies, Kubelings eliminates all installation friction (no Python, pip, virtual environments, kubectl, or local container clusters required). Users can immediately explore, understand, and practice Kubernetes concepts directly in any modern browser on desktop, tablet, or mobile.

The accompanying documentation site is transformed into an **in-depth 26-chapter Kubernetes Reference Guide & Field Manual**, pairing detailed architectural concepts and annotated YAML schemas with instant deep links into interactive WebAssembly playground challenges.

---

## 2. Architecture & Scope

```
                               ┌────────────────────────────────────────────────────────┐
                               │                    dnf0.github.io                      │
                               └───────────────────────────┬────────────────────────────┘
                                                           │
                                ┌──────────────────────────┴───────────────────────────┐
                                │                                                      │
                                ▼                                                      ▼
    ┌───────────────────────────────────────────────────────┐      ┌────────────────────────────────────────────────────────┐
    │          MkDocs Reference Guide & Field Manual        │      │          Standalone WebAssembly IDE Playground         │
    │         (https://dnf0.github.io/kubelings/)           │      │    (https://dnf0.github.io/kubelings/playground/)      │
    │                                                       │      │                                                        │
    │  • 26 In-Depth Topic Reference Guides (01 - 26)       │◄────►│  • 100vw × 100vh Dedicated Learning Workspace          │
    │  • Architecture Diagrams & Control Plane Mechanics    │      │  • Monaco Editor + Diff Solution Comparator            │
    │  • Annotated YAML Schemas & Field Anatomies           │      │  • Pyodide Python 3.12 Wasm Background Web Worker      │
    │  • Production Best Practices & Common Gotchas         │      │  • 114 Micro-Exercises across 26 Chapters             │
    │  • Deep-Link CTAs: [⚡ Practice Exercise in Wasm →]   │      │  • URL Query Parameter Deep-Linking (?exercise=...)   │
    └───────────────────────────────────────────────────────┘      └────────────────────────────────────────────────────────┘
```

---

## 3. Detailed Component Specifications

### 3.1 Codebase Simplification & Dependency Pruning

1. **Retire CLI Runtime & Watch Daemon**:
   - Prune terminal-only modules (`src/kubelings/cli.py`, `src/kubelings/runner.py`, cluster runner scripts) and tests that validate CLI subprocesses.
   - Retain the core data models and validation engine:
     - `src/kubelings/models.py`: Data structures (`Exercise`, `Chapter`, `Manifest`).
     - `src/kubelings/validator.py`: Core Kubernetes manifest schema validation engine.
     - `src/kubelings/validators/*.py`: All 26 chapter validation suites (114 exercise validators).
     - `src/kubelings/manifest.py`: Exercise registry and chapter manifest definitions.
   - Clean up `pyproject.toml` dependencies:
     - Remove `typer`, `click`, `rich`, `watchfiles`, `kubernetes`.
     - Retain `pyyaml`, `pydantic`, `jsonschema` for schema compilation, plus development tools (`pytest`, `ruff`, `pyright`, `mkdocs-material`).

2. **Single Source of Truth Bundler**:
   - `scripts/build_playground_bundle.py` reads `src/kubelings/models.py`, `src/kubelings/validator.py`, `src/kubelings/validators/*.py`, and `exercises/` to produce `docs/assets/playground/playground-bundle.json`.

---

### 3.2 Web Playground Deep-Linking & State Enhancements

1. **URL Parameter Routing**:
   - Support `?exercise=<id>` (e.g. `?exercise=pods01`, `?exercise=rbac03`, `?exercise=gateway02`) and `?chapter=<num>`.
   - On page load, `docs/assets/playground/playground.js` checks `window.location.search`. If an exercise ID or chapter number is present, it automatically expands the relevant chapter accordion, selects the exercise, and loads it into Monaco.
2. **Top Navigation Sync**:
   - Header provides clean bidirectional links between `📖 Documentation`, `📚 Syllabus`, and the standalone learning IDE.

---

### 3.3 26-Chapter Kubernetes Reference Guide

The MkDocs site is reorganized into 26 comprehensive, topic-focused reference guides:

| Chapter | Topic | Reference Guide Path | Focus & Key Concepts |
| :--- | :--- | :--- | :--- |
| **01** | Core Workloads & Pods | `docs/guides/01-pods.md` | Pod lifecycle, containers, initContainers, sidecars, resource requests/limits, Downward API. |
| **02** | Controllers & Replication | `docs/guides/02-controllers.md` | Deployments, ReplicaSets, StatefulSets, DaemonSets, Jobs, CronJobs, rollback strategies. |
| **03** | Configuration & Secrets | `docs/guides/03-config-secrets.md` | ConfigMaps, Secrets, volume mounts, envFrom, immutable configurations, projection. |
| **04** | Storage & Persistent Volumes | `docs/guides/04-storage.md` | Volumes, PersistentVolumes, PersistentVolumeClaims, StorageClasses, access modes, reclaim policies. |
| **05** | Services & Networking | `docs/guides/05-services-networking.md` | ClusterIP, NodePort, LoadBalancer, Headless Services, Endpoints, kube-dns / CoreDNS. |
| **06** | Ingress & Ingress Controllers | `docs/guides/06-ingress-gateway.md` | Ingress rules, host routing, path matching (Exact/Prefix), TLS termination, annotations. |
| **07** | Scheduling & Node Placement | `docs/guides/07-scheduling.md` | nodeSelector, nodeAffinity, podAffinity / podAntiAffinity, taints & tolerations, topologySpreadConstraints. |
| **08** | Security, RBAC & ServiceAccounts | `docs/guides/08-security-rbac.md` | ServiceAccounts, Roles, RoleBindings, ClusterRoles, ClusterRoleBindings, SecurityContext, runAsNonRoot. |
| **09** | Network Policies | `docs/guides/09-network-policies.md` | Ingress & egress traffic filtering, podSelector, namespaceSelector, default-deny security patterns. |
| **10** | Lifecycle, Probes & Health Checks | `docs/guides/10-lifecycle-probes.md` | startupProbe, livenessProbe, readinessProbe (HTTP, TCP, gRPC, exec), postStart/preStop hooks. |
| **11** | Autoscaling (HPA, VPA, KEDA) | `docs/guides/11-autoscaling.md` | HorizontalPodAutoscaler (metrics v2), VerticalPodAutoscaler, KEDA event-driven triggers. |
| **12** | CRDs & Operator Pattern | `docs/guides/12-crds-and-operators.md` | CustomResourceDefinitions, OpenAPI v3 validation, status subresources, operator reconciliation loop. |
| **13** | Troubleshooting & Debugging | `docs/guides/13-troubleshooting.md` | Diagnosing CrashLoopBackOff, OOMKilled, ImagePullBackOff, Pending pods, ephemeral debug containers. |
| **14** | GitOps & Continuous Delivery (ArgoCD) | `docs/guides/14-gitops-argocd.md` | ArgoCD Application CRDs, syncPolicies, automated self-heal & pruning, App-of-Apps architectural pattern. |
| **15** | Service Mesh & eBPF (Cilium) | `docs/guides/15-service-mesh-cilium.md` | CiliumNetworkPolicy, Layer 7 visibility, mTLS transparent encryption, eBPF data path. |
| **16** | Policy as Code (Kyverno & Gatekeeper) | `docs/guides/16-policy-as-code.md` | Kyverno ClusterPolicies (validate, mutate, generate), OPA Gatekeeper ConstraintTemplates. |
| **17** | Multi-Tenancy & Virtual Clusters | `docs/guides/17-multitenancy-vcluster.md` | Namespace tenancy, ResourceQuotas, LimitRanges, vCluster virtual control plane architecture. |
| **18** | Admission Webhooks | `docs/guides/18-admission-webhooks.md` | MutatingAdmissionWebhook, ValidatingAdmissionWebhook, dynamic admission controllers, TLS certs. |
| **19** | Package Management with Helm | `docs/guides/19-helm-packaging.md` | Chart.yaml structure, values.yaml, Go templates, template functions, release lifecycle. |
| **20** | Configuration Management with Kustomize | `docs/guides/20-kustomize-overlays.md` | Bases & overlays, patchesStrategicMerge, namePrefix, configMapGenerator, secretGenerator. |
| **21** | Kubernetes Gateway API | `docs/guides/21-gateway-api.md` | GatewayClass, Gateway, HTTPRoute, GRPCRoute, TLSRoute, cross-namespace route attachment. |
| **22** | Infrastructure as Code with Crossplane | `docs/guides/22-crossplane-iac.md` | CompositeResourceDefinitions (XRDs), Compositions, Managed Resources, claim patterns. |
| **23** | Kernel Security Observability (Tetragon) | `docs/guides/23-ebpf-tetragon.md` | eBPF TracingPolicies, kernel hookpoints (kprobes, tracepoints), namespace security enforcement. |
| **24** | Machine Learning Workloads (KubeRay) | `docs/guides/24-kuberay-ml.md` | RayCluster, head pod and worker group configurations, distributed AI training & inference. |
| **25** | Batch & Queue Scheduling (Kueue/Volcano)| `docs/guides/25-batch-kueue-volcano.md` | Kueue ResourceFlavors, ClusterQueues, LocalQueues, Volcano gang scheduling for batch compute. |
| **26** | Dynamic Resource Allocation (DRA) | `docs/guides/26-hardware-acceleration-dra.md` | ResourceClass, ResourceClaim, ResourceClaimTemplate, GPU/TPU device scheduling. |

Each Reference Guide follows a consistent, high-utility structure:
1. **Concept Overview & Control Plane Mechanics**: Architectural context and diagram explaining why this primitive exists.
2. **Complete Annotated YAML Anatomy**: Syntax breakdown with line-by-line field documentation.
3. **Production Best Practices & Pitfalls**: Hardened configuration rules and common failure modes.
4. **Interactive Practice Callout**: Interactive banner with deep link to the WebAssembly playground.

---

## 4. Verification & Testing Strategy

1. **Automated Bundle & Validation Suite**:
   - `pytest tests/test_playground_bundle.py` verifying that all 114 exercises in the bundle validate cleanly against their solution code.
2. **Documentation Build**:
   - `mkdocs build --strict` ensuring zero broken links, invalid navigation entries, or missing assets.
3. **Deep-Linking Test**:
   - Verify that loading `playground/index.html?exercise=<id>` selects and activates the correct exercise in the browser.

---

## 5. Implementation Stages

1. **Phase 1: Codebase Pruning & Dependency Cleanup**:
   - Remove legacy CLI and cluster runner code.
   - Clean `pyproject.toml`.
2. **Phase 2: Playground URL Deep-Linking**:
   - Add query parameter parsing to `playground.js`.
3. **Phase 3: Comprehensive 26-Chapter Reference Documentation**:
   - Create all 26 reference guides in `docs/guides/`.
   - Update `mkdocs.yml` navigation and site landing page `docs/index.md`.
4. **Phase 4: Verification & Deployment**:
   - Build bundle, verify tests, build docs, and deploy to GitHub Pages.

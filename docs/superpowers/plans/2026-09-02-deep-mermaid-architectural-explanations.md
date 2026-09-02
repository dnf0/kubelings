# Deep Mermaid Architectural Walkthroughs Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Choose an execution mode:
> 1. `superpowers:subagent-driven-development` (recommended for multi-agent reviews, backed by `SKILL.state` / `.agent-state/state.json`)
> 2. `agent-rules:stateful-execution` (SKILL.state) (recommended for deterministic single-agent linear execution)
> 3. `superpowers:executing-plans` (batch execution with manual checkpoints)
> Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Provide comprehensive, under-the-hood systems explanations (gRPC streaming, Protobuf/JSON serialization, kernel datapath, cgroups, Linux namespaces, OIDC/STS token projection) for all 29 Mermaid diagrams in the Kubelings reference guides.

**Architecture:** 
1. Create `scripts/reference_guide_explanations.py` defining deep technical walkthroughs for all 29 chapters across 4 standardized subsections: Architectural Flow, Serialization & Protocols, Component Breakdown, and Under-The-Hood Mechanics.
2. Update `scripts/generate_reference_guides.py` to integrate and render these explanations under Section 1 of every reference guide.
3. Update `tests/test_reference_guides.py` to enforce that all 29 guides include detailed technical explanations and no boilerplate placeholders.
4. Regenerate all guides, verify with strict MkDocs build and pytest suite, and commit.

**Tech Stack:** Python 3.12, MkDocs Material, Mermaid.js, Pytest, Ruff, Pyright.

---

## Tasks

### Task 1: Scaffolding Explanation Engine & Chapters 01-10 Explanations
- Create `scripts/reference_guide_explanations.py`.
- Define deep systems explanations for:
  - Chapter 01 (Pods: CRI gRPC, Protobuf serialization, pause container namespaces, cgroups v2 limits).
  - Chapter 02 (Controllers: Informer Reflector List-Watch, WorkQueue rate-limiting, ReplicaSet rolling update math).
  - Chapter 03 (Config & Secrets: KMS envelope decryption, `..data` atomic symlink swap vs static env injection).
  - Chapter 04 (Storage: Dynamic CSI gRPC `CreateVolume`/`NodePublishVolume`, Linux ext4/xfs bind-mounting).
  - Chapter 05 (Services: CoreDNS A-records, `kube-proxy` iptables/IPVS DNAT tables, EndpointSlice controller).
  - Chapter 06 (Ingress: L4 Cloud LB SNI pass-through, Envoy/NGINX reverse proxy, upstream HTTP keep-alive pools).
  - Chapter 07 (Scheduling: Two-phase scheduling queue, Filter predicates, Score priorities, Reserve/PreBind/Bind).
  - Chapter 08 (RBAC: X.509/OIDC Bearer AuthN, RBAC AuthZ engine, SubjectAccessReview, Restricted PSA).
  - Chapter 09 (Network Policies: CNI eBPF/iptables packet filtering, conntrack table state, default-deny isolation).
  - Chapter 10 (Probes: Kubelet prober goroutines, HTTP/TCP/Exec socket checks, EndpointSlice Ready gating).

### Task 2: Chapters 11-20 Explanations
- Add deep systems explanations for:
  - Chapter 11 (Autoscaling: Metrics Server aggregation, HPA algorithm math, Karpenter EC2 Fleet API).
  - Chapter 12 (CRDs & Operators: OpenAPI v3 validation, CustomResourceDefinition schema, Kopf/Kube-rs controllers).
  - Chapter 13 (Troubleshooting: Kernel OOM-killer SIGKILL 137, CrashLoopBackOff exponential backoff, readiness probe timeouts).
  - Chapter 14 (GitOps ArgoCD: Git tree diffing, 3m polling/webhooks, self-healing drift reconciliation).
  - Chapter 15 (Service Mesh Cilium: eBPF `sockops` bypassing TCP stack, WireGuard node-to-node crypto, Hubble L7 flow).
  - Chapter 16 (Policy as Code: AdmissionReview JSON webhooks, Kyverno/OPA Gatekeeper mutation & Sigstore Cosign verification).
  - Chapter 17 (vcluster: Virtual control plane SQLite/k3s, syncer translating virtual Pods to physical host namespace).
  - Chapter 18 (Admission Webhooks: Sequential Mutating Webhooks with JSONPatch RFC 6902, Parallel Validating Webhooks).
  - Chapter 19 (Helm: Go template Sprig execution, values hierarchy, compressed release secrets in `sh.helm.release.v1`).
  - Chapter 20 (Kustomize: Strategic merge patches, JSON 6902 patches, ConfigMap hash generator).

### Task 3: Chapters 21-29 Explanations
- Add deep systems explanations for:
  - Chapter 21 (Gateway API: Envoy xDS dynamic control plane, GatewayClass, Gateway listener ports, HTTPRoute traffic weights).
  - Chapter 22 (Crossplane: XRC claim, XRD schema, XR composite, Managed Resource reconciliation loops via Cloud SDKs).
  - Chapter 23 (Tetragon eBPF: In-kernel kprobes, tracepoints, LSM hooks, real-time SIGKILL process termination).
  - Chapter 24 (KubeRay: Ray Head GCS Redis/Protobuf, Raylet task scheduler, NCCL direct peer-to-peer GPU memory transport).
  - Chapter 25 (Batch Kueue & Volcano: Cohort borrowing, ClusterQueue admission, PodGroup minMember gang scheduling).
  - Chapter 26 (Hardware Acceleration & DRA: ResourceClaimTemplate, CEL device query, NVIDIA CDI driver plugin, PCIe DMA).
  - Chapter 27 (AWS EKS: OIDC projected serviceaccount token, EKS webhook injection, STS AssumeRoleWithWebIdentity, ALB IP mode, Karpenter).
  - Chapter 28 (GCP GKE: Workload Identity Federation, GKE Metadata Server token exchange, Autopilot compute classes, Cloud Armor WAF).
  - Chapter 29 (Enterprise Governance: ArgoCD ApplicationSet Matrix Generator, External Secrets Operator AWS sync, Vault agent sidecar).

### Task 4: Template Integration & Test Enhancements
- Update `scripts/generate_reference_guides.py` to import `CHAPTER_EXPLANATIONS` from `scripts/reference_guide_explanations.py` and render structured Section 1 subsections.
- Update `tests/test_reference_guides.py` to assert that all 29 guides contain detailed subsections `1.1`, `1.2`, `1.3`, and `1.4` and verify minimum explanation length (>500 characters per section).

### Task 5: Regeneration, Strict Build & Full Test Verification
- Run `uv run python scripts/generate_reference_guides.py`.
- Run `uv run python scripts/build_playground_bundle.py`.
- Run `uv run pytest -q`.
- Run `uv run ruff check .` and `uv run pyright`.
- Run `uv run mkdocs build --strict`.
- Commit, merge, and push to remote.

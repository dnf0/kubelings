# Deep Mermaid Architectural Walkthroughs & Systems Mechanics Design

- **Date:** 2026-09-02
- **Topic:** In-depth, systems-level descriptions for all 29 reference guide Mermaid diagrams (gRPC, serialization/deserialization, kernel datapath, cgroups, controllers, cloud STS/OAuth2).
- **Target:** Kubelings Reference Guides (`docs/guides/*.md` & `scripts/generate_reference_guides.py`).

---

## 1. Objectives & Motivation
While the Mermaid.js diagrams provide high-level visual topology for each chapter, learners need deep, low-level technical context to understand **what is actually happening under the hood**:
- **Protocols & Inter-Process Communication**: Unix domain sockets (`/run/containerd/containerd.sock`, CSI sockets), gRPC streaming (CRI, CSI, DRA, Envoy xDS), HTTPS mTLS.
- **Serialization & Deserialization**: YAML/JSON to Go struct decoding, OpenAPI v3 validation, Protobuf encoding for `etcd` persistence, JSONPatch RFC 6902 mutations in admission webhooks, BPF bytecode compilation and ELF loading.
- **Kernel & OS Primitives**: Linux namespaces (`CLONE_NEWNET`, `CLONE_NEWPID`), cgroups v2 (`cpu.max`, `memory.max`), `iptables`/IPVS DNAT translation, eBPF socket maps (`BPF_MAP_TYPE_SOCKHASH`), atomic symlink swapping (`..data` pointer swap).
- **Cloud & Enterprise Identity**: OIDC federated trust, JWT token projection (`AWS_WEB_IDENTITY_TOKEN_FILE`), AWS STS `AssumeRoleWithWebIdentity`, GCP Metadata Server OAuth2 exchange, Vault ephemeral token leasing.

---

## 2. Structural Schema for Guide Section 1

Every reference guide's **Section 1: Architectural Overview & Control Plane Mechanics** will follow a standardized 4-part structure:

```markdown
## 1. Architectural Overview & Control Plane Mechanics

```mermaid
<diagram>
```

### 1.1 Architectural Flow & Lifecycle Walkthrough
A sequential, step-by-step narration tracking requests, reconciliation loops, and data plane packets through the diagram.

### 1.2 Serialization, Protocols & Communication Pathways
- **API & Wire Protocols**: Exact transport protocols (gRPC, HTTP/2, Protobuf, Unix Domain Sockets).
- **Data Serialization**: How manifests and objects are encoded/decoded across boundaries.

### 1.3 Deep-Dive Component Breakdown
Detailed analysis of each node/subgraph in the diagram:
- What software/binary runs it (e.g., `kubelet`, `containerd`, `tetragon-agent`).
- State tracking and caching (e.g., `SharedIndexInformer`, `Reflector`, `etcd` MVCC revision).
- Linux kernel and container runtime integration.

### 1.4 Under-The-Hood Mechanics & Failure Modes
- Critical low-level invariants (e.g., PID 1 signal forwarding, OOM scoring, TCP connection reuse, kernel socket bypass).
- Common failure vectors and how to identify them.
```

---

## 3. Modular Architecture

To maintain maintainability and avoid a monolithic script:
- Create `scripts/reference_guide_explanations.py` containing rich, multi-paragraph technical walkthroughs for Chapters 01 through 29.
- Update `scripts/generate_reference_guides.py` to import and render these comprehensive explanations in Section 1.
- Update tests in `tests/test_reference_guides.py` to verify that every guide contains all 4 subsections (`1.1`, `1.2`, `1.3`, `1.4`) with deep technical content.

---

## 4. Verification & Success Criteria
1. `uv run python scripts/generate_reference_guides.py` builds all 29 guides cleanly.
2. `uv run pytest tests/test_reference_guides.py` validates structure, links, diagrams, and explanation depth.
3. `uv run mkdocs build --strict` completes with 0 warnings.
4. `uv run pytest -q` passes all 1,088+ tests.

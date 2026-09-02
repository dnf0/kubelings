# Kubelings ☸️

**An interactive, client-side WebAssembly learning platform and comprehensive reference manual for Kubernetes.**

[![Playground](https://img.shields.io/badge/Playground-⚡%20Launch%20Interactive%20IDE-blueviolet)](playground/index.html)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Curriculum](https://img.shields.io/badge/Curriculum-26%20Chapters%20%7C%20114%20Exercises-brightgreen)](syllabus.md)

---

## ⚡ The Modern Way to Master Kubernetes

Kubelings combines a **zero-install, 100% client-side WebAssembly interactive playground** with **26 comprehensive architectural reference guides** spanning the entire cloud-native ecosystem.

<div class="grid cards" markdown>

-   :material-play-circle-outline: **Zero-Install Web IDE**
    ---
    Run Monaco Editor, Pyodide WebAssembly, and real-time schema validation 100% in your browser. No Docker, no minikube, and no cluster setup required.
    
    [**Launch Playground →**](playground/index.html){ .md-button .md-button--primary }

-   :material-book-open-page-variant-outline: **26-Chapter Reference Manual**
    ---
    Deep architectural documentation, annotated YAML specs, production best practices, and diagnostic workflows for modern Kubernetes.

    [**Explore Reference Guides →**](#-comprehensive-26-chapter-reference-guides){ .md-button }

</div>

---

## 📚 Comprehensive 26-Chapter Reference Guides

Explore in-depth architectural guides and launch linked practice exercises directly into the playground:

<div class="grid cards" markdown>

-   ### Core Workloads & Storage
    ---
    - [**01. Pods & Core Workloads**](guides/01-pods.md) &bull; Pod specs, multi-container pods, initContainers, ports
    - [**02. Controllers & Replication**](guides/02-controllers.md) &bull; Deployments, ReplicaSets, StatefulSets, DaemonSets, Jobs, CronJobs
    - [**03. Configuration & Secrets**](guides/03-config-secrets.md) &bull; ConfigMaps, Secrets, projected volumes, envFrom
    - [**04. Storage & Persistent Volumes**](guides/04-storage.md) &bull; PVs, PVCs, StorageClasses, access modes, volumeMounts

-   ### Networking & Traffic Routing
    ---
    - [**05. Services & Networking**](guides/05-services-networking.md) &bull; ClusterIP, NodePort, LoadBalancer, Headless services, Endpoints
    - [**06. Ingress & Gateway API**](guides/06-ingress-gateway.md) &bull; Ingress controllers, path rules, TLS termination, annotations
    - [**21. Gateway API Deep Dive**](guides/21-gateway-api.md) &bull; GatewayClass, Gateways, HTTPRoute, canary splits, ReferenceGrant
    - [**09. Network Policies**](guides/09-network-policies.md) &bull; Default deny, ingress/egress CIDR blocks, port rules

-   ### Scheduling, Security & Scaling
    ---
    - [**07. Scheduling & Advanced Placement**](guides/07-scheduling.md) &bull; nodeSelector, node/pod affinity, taints, tolerations, topology spread
    - [**08. Security, RBAC & ServiceAccounts**](guides/08-security-rbac.md) &bull; Roles, ClusterRoles, RoleBindings, SecurityContext, PSS/PSA
    - [**10. Health Probes & Lifecycle**](guides/10-lifecycle-probes.md) &bull; Liveness, readiness, startup probes, termination grace periods
    - [**11. Autoscaling (HPA, VPA, KEDA)**](guides/11-autoscaling.md) &bull; Horizontal Pod Autoscaler v2, VPA, event-driven KEDA
    - [**18. Admission Webhooks**](guides/18-admission-webhooks.md) &bull; Mutating, validating webhooks, sidecar injection, CRD conversion

-   ### CRDs, Troubleshooting & Packaging
    ---
    - [**12. Custom Resources & Operators**](guides/12-crds-and-operators.md) &bull; OpenAPI v3 schemas, subresources, reconciliation loops
    - [**13. Production Troubleshooting**](guides/13-troubleshooting.md) &bull; CrashLoopBackOff, ImagePullBackOff, Pending pods, ephemeral debug
    - [**19. Package Management with Helm**](guides/19-helm-packaging.md) &bull; Chart.yaml, Go templates, _helpers.tpl, values schemas, subcharts
    - [**20. Declarative Customization with Kustomize**](guides/20-kustomize-overlays.md) &bull; Bases, overlays, generators, strategic merge patches

-   ### Modern Cloud Native Ecosystem
    ---
    - [**14. GitOps with ArgoCD**](guides/14-gitops-argocd.md) &bull; Applications, ApplicationSets, sync policies, Argo Rollouts
    - [**15. Service Mesh & Cilium eBPF**](guides/15-service-mesh-cilium.md) &bull; L7 routing, mTLS, FQDN egress, Hubble observability
    - [**16. Policy as Code (Kyverno & OPA)**](guides/16-policy-as-code.md) &bull; ClusterPolicies, mutating/generating rules, Gatekeeper constraints
    - [**17. Multi-Tenancy & Virtual Clusters**](guides/17-multitenancy-vcluster.md) &bull; HNC anchors, tenant quotas, vcluster control planes
    - [**22. Infrastructure as Data with Crossplane**](guides/22-crossplane-iac.md) &bull; XRDs, Compositions, Managed Resources, claims
    - [**23. Kernel Security with eBPF Tetragon**](guides/23-ebpf-tetragon.md) &bull; sys_execve tracing, credential monitoring, kernel Sigkill
    - [**24. Distributed AI Orchestration with KubeRay**](guides/24-kuberay-ml.md) &bull; RayCluster, RayJob batch tuning, RayService serving
    - [**25. Batch AI Scheduling (Kueue & Volcano)**](guides/25-batch-kueue-volcano.md) &bull; ClusterQueue cohorts, gang scheduling, fair-share
    - [**26. Hardware Acceleration & DRA**](guides/26-hardware-acceleration-dra.md) &bull; NVIDIA MIG, Apple Silicon GPU, DRA, vLLM serving

</div>

---

## 💡 How the Playground Works

The Kubelings web playground runs entirely on client-side WebAssembly technology:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                          Web Browser Tab                               │
│  ┌───────────────────────┐             ┌─────────────────────────────┐ │
│  │     Monaco Editor     │  YAML Edit  │  Web Worker (Pyodide Wasm)  │ │
│  │  (VS Code in Browser) ├────────────►│  • PyYAML Manifest Parser   │ │
│  └───────────────────────┘             │  • 26 Schema Validators     │ │
│                                        │  • Progressive Hint Engine  │ │
│  ┌───────────────────────┐             └──────────────┬──────────────┘ │
│  │   Interactive xterm   │◄───────────────────────────┘                │
│  │    Terminal Output    │         Instant Test & Validation Result    │
│  └───────────────────────┘         (< 1ms in WebAssembly)              │
└────────────────────────────────────────────────────────────────────────┘
```

1. **Monaco Code Editor**: Full syntax highlighting, error diagnostics, and side-by-side solution diffing.
2. **Pyodide WebAssembly Engine**: Executes the exact Python schema validation engine in an isolated Web Worker thread.
3. **Local Progress Persistence**: Tracks completed exercises and user edits in `localStorage` with JSON export/import support.

---

## 🌐 The *lings Ecosystem

If you enjoy the hands-on learning model of **Kubelings**, check out the other interactive projects in the suite:

- 🏗️ [**Terralings**](https://github.com/dnf0/terralings) – Master Terraform and OpenTofu through interactive infrastructure-as-code exercises.
- 🇪🇸 [**Spanglings**](https://github.com/dnf0/spanglings) – Developer-grade interactive TUI for learning Spanish (B1–C1).
- ⚡ [**Raylings**](https://github.com/dnf0/raylings) – Learn distributed AI, Ray Core actors, and scalable clusters through hands-on Python exercises.

---

## 📄 License

Kubelings is open-source software licensed under the [Apache License 2.0](https://github.com/dnf0/kubelings/blob/main/LICENSE).

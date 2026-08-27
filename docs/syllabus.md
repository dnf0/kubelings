# Curriculum Syllabus

Kubelings features **23 chapters** covering **102 real-world exercises**:

---

### Chapter 01: Pods & Core Workloads
- `pods01`: First Pod Manifest & Spec (API syntax, container structure).
- `pods02`: Multi-Container Pods & Sidecar Pattern (`emptyDir` shared volume).
- `pods03`: Init Containers for Pre-Flight Checks & Data Population.
- `pods04`: Resource Requests, Limits & Quality of Service (Guaranteed, Burstable).
- `pods05`: Downward API & Pod Metadata Injection via Env Variables.
- `pods06`: Pod Disruption Budgets (PDB) & High Availability.

### Chapter 02: Controllers & Replication
- `ctrl01`: ReplicaSets & MatchLabels Selectors.
- `ctrl02`: Deployments & Zero-Downtime Rolling Update Strategy.
- `ctrl03`: Deployment Rollbacks & Revision History.
- `ctrl04`: StatefulSets & Stable Network Identifiers / PersistentVolumeClaims.
- `ctrl05`: DaemonSets for Cluster Node Daemons (fluentd/prom-node-exporter).
- `ctrl06`: Jobs & CronJobs for Batch Processing.

### Chapter 03: Configuration & Secrets
- `config01`: ConfigMaps & Direct Key-Value Pair Ingestion.
- `config02`: Secret Creation & Base64 Decoding.
- `config03`: Mounting ConfigMaps as Volume Directories.
- `config04`: Mounting Secrets with Restricted File Permissions (`defaultMode`).
- `config05`: Immutable ConfigMaps & Secrets for Performance & Safety.

### Chapter 04: Storage & Persistent Volumes
- `storage01`: Ephemeral Storage with `emptyDir` & Host Volumes.
- `storage02`: PersistentVolumes (PV) with Static Provisioning.
- `storage03`: PersistentVolumeClaims (PVC) Binding & AccessModes (`ReadWriteOnce`, `ReadOnlyMany`).
- `storage04`: StorageClasses & Dynamic Volume Provisioning.
- `storage05`: Volume Snapshots & Restore Workflows.

### Chapter 05: Services & Networking
- `net01`: ClusterIP Services & Label Selector Target Routing.
- `net02`: Headless Services for Stateful Discovery.
- `net03`: NodePort Services for External Edge Ingress.
- `net04`: CoreDNS Resolution & SRV Records.
- `net05`: ExternalName Services for Third-Party Endpoints.

### Chapter 06: Ingress & Traffic Management
- `ingress01`: Ingress Resources & Multi-Path Routing Rules.
- `ingress02`: TLS Termination & Secret References.
- `ingress03`: Custom Ingress Annotations & URL Rewriting.
- `ingress04`: Gateway API Architecture.

### Chapter 07: Scheduling & Placement
- `sched01`: Node Selection with `nodeSelector`.
- `sched02`: Node Affinity & Anti-Affinity (Required vs Preferred).
- `sched03`: Pod Anti-Affinity for Multi-Zone Redundancy.
- `sched04`: Taints & Tolerations for Dedicated Workloads.
- `sched05`: Topology Spread Constraints for Max-Skew Balancing.

### Chapter 08: Security & RBAC
- `rbac01`: ServiceAccounts & IAM Tokens.
- `rbac02`: Roles & RoleBindings (Namespace Scoped).
- `rbac03`: ClusterRoles & ClusterRoleBindings (Cluster Scoped).
- `rbac04`: SecurityContext (RunAsNonRoot, ReadOnlyRootFilesystem, Drop Capabilities).
- `rbac05`: Pod Security Standards (Privileged, Baseline, Restricted).

### Chapter 09: Network Policies
- `netpol01`: Default Deny All Traffic Policy.
- `netpol02`: Ingress Traffic Filtering by Namespace & Pod Selector.
- `netpol03`: Egress Traffic Allow-Listing & DNS Port 53 Egress.
- `netpol04`: Named Ports & CIDR IPBlock Exceptions.

### Chapter 10: Lifecycle & Probes
- `health01`: HTTP & TCP Liveness Probes.
- `health02`: Readiness Probes for Traffic Shedding.
- `health03`: Startup Probes for Slow Bootstrapping Workloads.
- `health04`: PostStart & PreStop Lifecycle Hooks.

### Chapter 11: Autoscaling
- `autoscale01`: Horizontal Pod Autoscaler (HPA v2) CPU/Memory Scaling.
- `autoscale02`: HPA Scaling Policies & Stabilization Windows.
- `autoscale03`: Vertical Pod Autoscaler (VPA) Resource Recommendations.
- `autoscale04`: Event-Driven Autoscaling (KEDA ScaledObjects).

### Chapter 12: CRDs & Operators
- `crd01`: CustomResourceDefinition (CRD) OpenAPI v3 Schemas.
- `crd02`: CRD Subresources (`/status`, `/scale`) & Custom Columns.
- `crd03`: Kubernetes Operator Reconciliation Loops in Python.
- `crd04`: Dynamic Admission Controller Architecture.

### Chapter 13: Troubleshooting & Diagnostics
- `troubleshoot01`: CrashLoopBackOff & Container Exit Code Analysis.
- `troubleshoot02`: ImagePullBackOff & Registry Authentication.
- `troubleshoot03`: Pending Pods & Insufficient Capacity Diagnosis.
- `troubleshoot04`: ResourceQuota & LimitRange Bottlenecks.
- `troubleshoot05`: Ephemeral Debug Containers (`kubectl debug`).

### Chapter 14: GitOps with ArgoCD
- `gitops01`: ArgoCD Application CRD & Automated Sync Policies.
- `gitops02`: ArgoCD ApplicationSet Matrix & Directory Generators.
- `gitops03`: Sync Windows, ServerSideApply & Retry Backoff.
- `gitops04`: Progressive Delivery with Argo Rollouts (Canary Analysis).

### Chapter 15: Service Mesh with Cilium
- `mesh01`: Cilium L7 HTTP Filtering & Path-Based Routing.
- `mesh02`: Strict Mutual TLS (mTLS) & PeerAuthentication.
- `mesh03`: CiliumClusterwideNetworkPolicy with DNS FQDN Egress.
- `mesh04`: Hubble Observability & OpenTelemetry Tracing.

### Chapter 16: Policy as Code
- `policy01`: Kyverno ClusterPolicy for Required Labels Validation.
- `policy02`: Kyverno Mutating Policy for Security Defaults (`runAsNonRoot`).
- `policy03`: Kyverno Generate Policy for Default Deny NetworkPolicy.
- `policy04`: OPA Gatekeeper ConstraintTemplate & Constraint with Rego logic.

### Chapter 17: Multi-Tenancy & Virtual Clusters
- `tenant01`: Hierarchical Namespace Controller (HNC) Subnamespace Anchors.
- `tenant02`: Multi-Document Tenant ResourceQuotas and LimitRanges.
- `tenant03`: Virtual Cluster (`vcluster`) Control Plane Specification.
- `tenant04`: Multi-Tenant Network Isolation & Egress Filtering.

### Chapter 18: Advanced Admission Webhooks
- `webhook01`: MutatingWebhookConfiguration Manifest & CABundle Routing.
- `webhook02`: ValidatingWebhookConfiguration Manifest & Scope Filters.
- `webhook03`: Dynamic Sidecar Injection AdmissionReview JSON Patch.
- `webhook04`: CRD Webhook Conversion Strategy for Multi-Version APIs.

### Chapter 19: Package Management with Helm
- `helm01`: Helm `Chart.yaml` Metadata & Dependencies (Helm v3, SemVer, Subcharts).
- `helm02`: Helm Go Templating & Named Helpers (`_helpers.tpl`, `chart_fullname`, Template Injection).
- `helm03`: Helm `values.schema.json` Validation Schema (JSONSchema Draft-7 structure).
- `helm04`: Helm Subcharts & Global Values Propagation (`global`, dependency overrides).

### Chapter 20: Declarative Customization with Kustomize
- `kustomize01`: Kustomize Base Manifests & Metadata Transformations (`resources`, `namespace`, `namePrefix`, `commonLabels`, `commonAnnotations`).
- `kustomize02`: Kustomize ConfigMap & Secret Generators (`configMapGenerator`, `secretGenerator`, `generatorOptions`).
- `kustomize03`: Kustomize Strategic Merge & JSON6902 Target Patches (`patches` with JSON6902 replace/add operations).
- `kustomize04`: Kustomize Multi-Environment Overlays & Image Transforms (`overlays/prod`, `images`, `replicas`).

### Chapter 21: Next-Gen Traffic Routing with Kubernetes Gateway API
- `gateway01`: GatewayClass and Gateway Declaration (`gateway.networking.k8s.io/v1`, HTTP listener configuration).
- `gateway02`: HTTPRoute Path & Header-Based Routing (parentRefs, path prefix matching, request header conditions).
- `gateway03`: Canary Traffic Splitting & URL Rewriting (weighted backendRefs, `URLRewrite` filters, header injection).
- `gateway04`: Cross-Namespace Security with ReferenceGrant (`ReferenceGrant` authorization for cross-namespace services).

### Chapter 22: Infrastructure as Data with Crossplane
- `crossplane01`: CompositeResourceDefinition (XRD) Schema (`apiextensions.crossplane.io/v1`, custom infrastructure schemas).
- `crossplane02`: Composition and Field Path Transforms (`Composition` mapping XRD fields to managed cloud resources).
- `crossplane03`: ProviderConfig and Resource Deletion Policies (`ProviderConfig` secret credentials and deletion policies).
- `crossplane04`: Developer Self-Service Claims & Connection Secrets (namespaced claims and secret propagation).

### Chapter 23: Kernel-Level Security & Observability with eBPF Tetragon
- `tetragon01`: Process Execution Tracing with sys_execve (`cilium.io/v1alpha1` `TracingPolicy` for kernel process auditing).
- `tetragon02`: Sensitive File & Credential Access Auditing (`sys_openat` monitoring on `/etc/shadow` and service account tokens).
- `tetragon03`: Real-Time Kernel Sigkill Enforcement (synchronous `Sigkill` actions on unauthorized root binaries).
- `tetragon04`: eBPF TCP Socket & Network Egress Observability (`tcp_connect` kernel socket probes and event streaming).

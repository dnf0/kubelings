# Curriculum Syllabus

Kubelings features **20 chapters** covering **90 real-world exercises**:

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
- `net04`: LoadBalancer Services & External Cloud Integration.
- `net05`: CoreDNS Service Discovery & FQDN Name Resolution.

### Chapter 06: Ingress & Gateway API
- `ingress01`: Ingress Resources & Path-Based Routing Rules.
- `ingress02`: Ingress TLS Termination with Kubernetes Secrets.
- `ingress03`: Ingress Annotations & URL Rewrite Modifiers.
- `ingress04`: Gateway API Fundamentals (`GatewayClass`, `Gateway`, `HTTPRoute`).

### Chapter 07: Scheduling & Placement
- `sched01`: Node Selection with `nodeSelector`.
- `sched02`: Node Affinity (`requiredDuringScheduling`, `preferredDuringScheduling`).
- `sched03`: Pod Affinity and Anti-Affinity Rules.
- `sched04`: Node Taints and Pod Tolerations.
- `sched05`: Topology Spread Constraints across Failure Domains.

### Chapter 08: Security & RBAC
- `rbac01`: ServiceAccounts & IAM Binding.
- `rbac02`: Roles & RoleBindings in Local Namespaces.
- `rbac03`: ClusterRoles & ClusterRoleBindings across Cluster Scopes.
- `rbac04`: Pod & Container `securityContext` Hardening (non-root, read-only FS).
- `rbac05`: Pod Security Standards (PSS/PSA Admission).

### Chapter 09: Network Policies
- `netpol01`: Default Deny Ingress & Egress Isolation.
- `netpol02`: Ingress Traffic Filtering across Namespaces.
- `netpol03`: Egress Traffic Filtering & CoreDNS Rules.
- `netpol04`: Named Ports & IPBlock CIDR Exceptions.

### Chapter 10: Lifecycle & Health Probes
- `health01`: HTTP GET Liveness Probes.
- `health02`: TCP Socket Readiness Probes.
- `health03`: Startup Probes for Slow-Starting Workloads.
- `health04`: Container Lifecycle Hooks (`preStop` graceful shutdown).

### Chapter 11: Workload Autoscaling
- `autoscale01`: Horizontal Pod Autoscaler (HPA v2) CPU/Memory Targets.
- `autoscale02`: Advanced HPA Scaling Behaviors & Stabilization Windows.
- `autoscale03`: Vertical Pod Autoscaler (VPA) Resource Recommendations.
- `autoscale04`: KEDA Event-Driven Autoscaling (Queue/Kafka triggers).

### Chapter 12: CRDs & Custom Operators
- `crd01`: CustomResourceDefinition (`apiextensions.k8s.io/v1`) OpenAPIv3 Schemas.
- `crd02`: Custom Resource Status Subresource & Additional Printer Columns.
- `crd03`: Python Reconciliation Loop for Custom Resources.
- `crd04`: Admission Webhook Manifests (Mutating & Validating Webhooks).

### Chapter 13: Troubleshooting & Incidents
- `troubleshoot01`: Diagnosing & Resolving `CrashLoopBackOff` Failures.
- `troubleshoot02`: Resolving `ImagePullBackOff` & Private Registry Credentials.
- `troubleshoot03`: Triaging `Pending` Pods & Node Resource Saturation.
- `troubleshoot04`: Namespace ResourceQuotas & LimitRanges Enforcement.
- `troubleshoot05`: Ephemeral Debug Containers & Live Event Triage.

### Chapter 14: GitOps & ArgoCD
- `gitops01`: ArgoCD Application CRD & Automated Sync Policies (`prune`, `selfHeal`).
- `gitops02`: ArgoCD ApplicationSet Matrix & Git Directory Discovery.
- `gitops03`: Sync Windows, ServerSideApply & Exponential Retry Backoff.
- `gitops04`: Progressive Delivery with Argo Rollouts Canary Releases.

### Chapter 15: Service Mesh & Cilium
- `mesh01`: Cilium Layer 7 HTTP NetworkPolicy Filtering.
- `mesh02`: Strict Mutual TLS (mTLS) with PeerAuthentication.
- `mesh03`: CiliumClusterwideNetworkPolicy with DNS FQDN Egress Rules.
- `mesh04`: Hubble Observability & OpenTelemetry Tracing Instrumentation.

### Chapter 16: Policy as Code (Kyverno & Gatekeeper)
- `policy01`: Kyverno ClusterPolicy for Required Labels.
- `policy02`: Kyverno Mutating Policy for Security Defaults.
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


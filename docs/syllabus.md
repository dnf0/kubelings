# Curriculum Syllabus

Kubelings features **29 chapters** covering **126 real-world exercises** with bidirectional reference guides and WebAssembly playground integration:

---

### [Chapter 01: Kubernetes Core Workloads & Pods](guides/01-pods.md)
- [**`pods01`**](playground/index.html?exercise=pods01): First Pod Manifest & Spec
- [**`pods02`**](playground/index.html?exercise=pods02): Multi-Container Pods & Sidecar Pattern
- [**`pods03`**](playground/index.html?exercise=pods03): Init Containers for Initialization
- [**`pods04`**](playground/index.html?exercise=pods04): Resource Requests, Limits & QoS
- [**`pods05`**](playground/index.html?exercise=pods05): Downward API & Env Variables
- [**`pods06`**](playground/index.html?exercise=pods06): Pod Disruption Budgets & Static Pods

### [Chapter 02: Controllers & Replication](guides/02-controllers.md)
- [**`ctrl01`**](playground/index.html?exercise=ctrl01): ReplicaSets & Label Selectors
- [**`ctrl02`**](playground/index.html?exercise=ctrl02): Deployments & Rolling Updates
- [**`ctrl03`**](playground/index.html?exercise=ctrl03): Deployment Rollbacks & Revision History
- [**`ctrl04`**](playground/index.html?exercise=ctrl04): StatefulSets & Stable Network IDs
- [**`ctrl05`**](playground/index.html?exercise=ctrl05): DaemonSets for Node-Level Daemons
- [**`ctrl06`**](playground/index.html?exercise=ctrl06): Jobs & CronJobs

### [Chapter 03: Configuration & Secret Management](guides/03-config-secrets.md)
- [**`config01`**](playground/index.html?exercise=config01): ConfigMaps as Environment Variables
- [**`config02`**](playground/index.html?exercise=config02): ConfigMaps Mounted as Volumes
- [**`config03`**](playground/index.html?exercise=config03): Secrets & Base64 Encoding
- [**`config04`**](playground/index.html?exercise=config04): Secret Volume Mounts & Permissions
- [**`config05`**](playground/index.html?exercise=config05): Immutable ConfigMaps and Secrets

### [Chapter 04: Storage & Persistent Volumes](guides/04-storage.md)
- [**`storage01`**](playground/index.html?exercise=storage01): Volume Types (emptyDir & hostPath)
- [**`storage02`**](playground/index.html?exercise=storage02): PersistentVolumes & PersistentVolumeClaims
- [**`storage03`**](playground/index.html?exercise=storage03): Access Modes & Reclaim Policies
- [**`storage04`**](playground/index.html?exercise=storage04): StorageClasses & Dynamic Provisioning
- [**`storage05`**](playground/index.html?exercise=storage05): Volume Snapshots & Volume Expansion

### [Chapter 05: Services & Networking](guides/05-services-networking.md)
- [**`net01`**](playground/index.html?exercise=net01): ClusterIP Services & Port Mapping
- [**`net02`**](playground/index.html?exercise=net02): Headless Services & Stateful Addressing
- [**`net03`**](playground/index.html?exercise=net03): NodePort & LoadBalancer Service Types
- [**`net04`**](playground/index.html?exercise=net04): CoreDNS Internal Service Resolution
- [**`net05`**](playground/index.html?exercise=net05): ExternalName Services & Manual Endpoints

### [Chapter 06: Ingress & Gateway API](guides/06-ingress-gateway.md)
- [**`ingress01`**](playground/index.html?exercise=ingress01): Ingress Host & Path Routing
- [**`ingress02`**](playground/index.html?exercise=ingress02): Ingress TLS Termination
- [**`ingress03`**](playground/index.html?exercise=ingress03): Ingress Annotations & Rewrites
- [**`ingress04`**](playground/index.html?exercise=ingress04): Gateway API Fundamentals

### [Chapter 07: Scheduling, Affinity & Advanced Placement](guides/07-scheduling.md)
- [**`sched01`**](playground/index.html?exercise=sched01): Node Placement (nodeName & nodeSelector)
- [**`sched02`**](playground/index.html?exercise=sched02): Node Affinity & Constraints
- [**`sched03`**](playground/index.html?exercise=sched03): Pod Affinity & Pod Anti-Affinity
- [**`sched04`**](playground/index.html?exercise=sched04): Taints and Tolerations
- [**`sched05`**](playground/index.html?exercise=sched05): Topology Spread Constraints

### [Chapter 08: Security, RBAC & Service Accounts](guides/08-security-rbac.md)
- [**`rbac01`**](playground/index.html?exercise=rbac01): ServiceAccounts & Token Management
- [**`rbac02`**](playground/index.html?exercise=rbac02): Roles & RoleBindings
- [**`rbac03`**](playground/index.html?exercise=rbac03): ClusterRoles & ClusterRoleBindings
- [**`rbac04`**](playground/index.html?exercise=rbac04): Pod & Container SecurityContext
- [**`rbac05`**](playground/index.html?exercise=rbac05): Pod Security Standards (PSS/PSA)

### [Chapter 09: Network Policies & Traffic Segmentation](guides/09-network-policies.md)
- [**`netpol01`**](playground/index.html?exercise=netpol01): Default Deny Network Policy
- [**`netpol02`**](playground/index.html?exercise=netpol02): Ingress Traffic Filtering
- [**`netpol03`**](playground/index.html?exercise=netpol03): Egress Traffic & DNS Access
- [**`netpol04`**](playground/index.html?exercise=netpol04): Named Ports & IPBlock CIDR Exceptions

### [Chapter 10: Health Checking, Probes & Lifecycle](guides/10-lifecycle-probes.md)
- [**`health01`**](playground/index.html?exercise=health01): Liveness Probes
- [**`health02`**](playground/index.html?exercise=health02): Readiness Probes
- [**`health03`**](playground/index.html?exercise=health03): Startup Probes
- [**`health04`**](playground/index.html?exercise=health04): Lifecycle Hooks & Graceful Shutdown

### [Chapter 11: Autoscaling (HPA, VPA, KEDA)](guides/11-autoscaling.md)
- [**`autoscale01`**](playground/index.html?exercise=autoscale01): Horizontal Pod Autoscaler (HPA v2)
- [**`autoscale02`**](playground/index.html?exercise=autoscale02): HPA Custom Scaling Behavior
- [**`autoscale03`**](playground/index.html?exercise=autoscale03): Vertical Pod Autoscaler (VPA)
- [**`autoscale04`**](playground/index.html?exercise=autoscale04): Event-Driven Autoscaling (KEDA)

### [Chapter 12: Custom Resources, CRDs & Operators](guides/12-crds-and-operators.md)
- [**`crd01`**](playground/index.html?exercise=crd01): CustomResourceDefinition (CRD) Schema
- [**`crd02`**](playground/index.html?exercise=crd02): CRD Subresources & Printer Columns
- [**`crd03`**](playground/index.html?exercise=crd03): Python Kubernetes Operator Loop
- [**`crd04`**](playground/index.html?exercise=crd04): Dynamic Admission Webhooks

### [Chapter 13: Observability, Debugging & Production Troubleshooting](guides/13-troubleshooting.md)
- [**`troubleshoot01`**](playground/index.html?exercise=troubleshoot01): Debugging CrashLoopBackOff & Exit Codes
- [**`troubleshoot02`**](playground/index.html?exercise=troubleshoot02): Debugging ImagePullBackOff
- [**`troubleshoot03`**](playground/index.html?exercise=troubleshoot03): Debugging Pending Pods & Scheduling Failures
- [**`troubleshoot04`**](playground/index.html?exercise=troubleshoot04): ResourceQuotas & LimitRanges
- [**`troubleshoot05`**](playground/index.html?exercise=troubleshoot05): Ephemeral Debug Containers & Event Triage

### [Chapter 14: GitOps Continuous Delivery with ArgoCD](guides/14-gitops-argocd.md)
- [**`gitops01`**](playground/index.html?exercise=gitops01): ArgoCD Application CRD & Sync Policies
- [**`gitops02`**](playground/index.html?exercise=gitops02): ArgoCD ApplicationSet Matrix Generator
- [**`gitops03`**](playground/index.html?exercise=gitops03): Sync Windows, ServerSideApply & Retry Backoff
- [**`gitops04`**](playground/index.html?exercise=gitops04): Progressive Delivery with Argo Rollouts

### [Chapter 15: Service Mesh, eBPF & Cilium](guides/15-service-mesh-cilium.md)
- [**`mesh01`**](playground/index.html?exercise=mesh01): Cilium L7 HTTP Filtering & Routing
- [**`mesh02`**](playground/index.html?exercise=mesh02): Strict Mutual TLS & PeerAuthentication
- [**`mesh03`**](playground/index.html?exercise=mesh03): CiliumClusterwideNetworkPolicy with DNS FQDN Egress
- [**`mesh04`**](playground/index.html?exercise=mesh04): Hubble Observability & OpenTelemetry Tracing

### [Chapter 16: Policy as Code (Kyverno & Gatekeeper)](guides/16-policy-as-code.md)
- [**`policy01`**](playground/index.html?exercise=policy01): Kyverno ClusterPolicy for Required Labels
- [**`policy02`**](playground/index.html?exercise=policy02): Kyverno Mutating Policy for Security Defaults
- [**`policy03`**](playground/index.html?exercise=policy03): Kyverno Generate Policy for Default Deny NetworkPolicy
- [**`policy04`**](playground/index.html?exercise=policy04): OPA Gatekeeper ConstraintTemplate & Constraint

### [Chapter 17: Multi-Tenancy & Virtual Clusters](guides/17-multitenancy-vcluster.md)
- [**`tenant01`**](playground/index.html?exercise=tenant01): HNC Hierarchical Subnamespace Anchor
- [**`tenant02`**](playground/index.html?exercise=tenant02): Tenant ResourceQuotas and LimitRanges
- [**`tenant03`**](playground/index.html?exercise=tenant03): Virtual Cluster (vcluster) Control Plane
- [**`tenant04`**](playground/index.html?exercise=tenant04): Multi-Tenant Network Isolation & Egress Filtering

### [Chapter 18: Advanced Admission Webhooks](guides/18-admission-webhooks.md)
- [**`webhook01`**](playground/index.html?exercise=webhook01): MutatingWebhookConfiguration Manifest
- [**`webhook02`**](playground/index.html?exercise=webhook02): ValidatingWebhookConfiguration Manifest
- [**`webhook03`**](playground/index.html?exercise=webhook03): Dynamic Sidecar Injection AdmissionReview Response
- [**`webhook04`**](playground/index.html?exercise=webhook04): CRD Webhook Conversion Strategy

### [Chapter 19: Package Management with Helm](guides/19-helm-packaging.md)
- [**`helm01`**](playground/index.html?exercise=helm01): Helm Chart.yaml Metadata & Dependencies
- [**`helm02`**](playground/index.html?exercise=helm02): Helm Go Templating & Named Helpers (_helpers.tpl)
- [**`helm03`**](playground/index.html?exercise=helm03): Helm values.schema.json Validation Schema
- [**`helm04`**](playground/index.html?exercise=helm04): Helm Subcharts & Global Values

### [Chapter 20: Declarative Customization with Kustomize](guides/20-kustomize-overlays.md)
- [**`kustomize01`**](playground/index.html?exercise=kustomize01): Kustomize Base Manifests & Metadata Transformations
- [**`kustomize02`**](playground/index.html?exercise=kustomize02): Kustomize ConfigMap & Secret Generators
- [**`kustomize03`**](playground/index.html?exercise=kustomize03): Kustomize Strategic Merge & JSON6902 Target Patches
- [**`kustomize04`**](playground/index.html?exercise=kustomize04): Kustomize Multi-Environment Overlays & Image Transforms

### [Chapter 21: Next-Gen Traffic Routing with Kubernetes Gateway API](guides/21-gateway-api.md)
- [**`gateway01`**](playground/index.html?exercise=gateway01): GatewayClass and Gateway Declaration
- [**`gateway02`**](playground/index.html?exercise=gateway02): HTTPRoute Path & Header-Based Routing
- [**`gateway03`**](playground/index.html?exercise=gateway03): Canary Traffic Splitting & URL Rewriting
- [**`gateway04`**](playground/index.html?exercise=gateway04): Cross-Namespace Security with ReferenceGrant

### [Chapter 22: Infrastructure as Data with Crossplane](guides/22-crossplane-iac.md)
- [**`crossplane01`**](playground/index.html?exercise=crossplane01): CompositeResourceDefinition (XRD) Schema
- [**`crossplane02`**](playground/index.html?exercise=crossplane02): Composition and Field Path Transforms
- [**`crossplane03`**](playground/index.html?exercise=crossplane03): ProviderConfig and Resource Deletion Policies
- [**`crossplane04`**](playground/index.html?exercise=crossplane04): Developer Self-Service Claims & Connection Secrets

### [Chapter 23: Kernel-Level Security & Observability with eBPF Tetragon](guides/23-ebpf-tetragon.md)
- [**`tetragon01`**](playground/index.html?exercise=tetragon01): Process Execution Tracing with sys_execve
- [**`tetragon02`**](playground/index.html?exercise=tetragon02): Sensitive File & Credential Access Auditing
- [**`tetragon03`**](playground/index.html?exercise=tetragon03): Real-Time Kernel Sigkill Enforcement
- [**`tetragon04`**](playground/index.html?exercise=tetragon04): eBPF TCP Socket & Network Egress Observability

### [Chapter 24: Distributed AI & ML Orchestration with KubeRay](guides/24-kuberay-ml.md)
- [**`ray01`**](playground/index.html?exercise=ray01): RayCluster Core Architecture & Head Node
- [**`ray02`**](playground/index.html?exercise=ray02): Heterogeneous Worker Pools & Autoscaling
- [**`ray03`**](playground/index.html?exercise=ray03): RayJob for Distributed Batch Fine-Tuning
- [**`ray04`**](playground/index.html?exercise=ray04): RayService for Production LLM Serving

### [Chapter 25: AI Batch Scheduling & Queuing with Kueue and Volcano](guides/25-batch-kueue-volcano.md)
- [**`kueue01`**](playground/index.html?exercise=kueue01): Kueue ResourceFlavor & ClusterQueue Cohort Borrowing
- [**`kueue02`**](playground/index.html?exercise=kueue02): Kueue LocalQueue & Suspended Workload Gating
- [**`volcano01`**](playground/index.html?exercise=volcano01): Volcano Gang Scheduling & Deadlock Prevention
- [**`volcano02`**](playground/index.html?exercise=volcano02): Volcano Queue & Fair-Share Scheduling

### [Chapter 26: Hardware Acceleration: NVIDIA MIG, Apple Silicon GPU & DRA](guides/26-hardware-acceleration-dra.md)
- [**`accel01`**](playground/index.html?exercise=accel01): NVIDIA MIG Slicing & Partitioning
- [**`accel02`**](playground/index.html?exercise=accel02): Apple Silicon GPU & Metal MPS Acceleration
- [**`accel03`**](playground/index.html?exercise=accel03): Dynamic Resource Allocation (DRA) Standard
- [**`accel04`**](playground/index.html?exercise=accel04): Production vLLM LLM Inference Server

### [Chapter 27: AWS EKS & Cloud Architecture](guides/27-aws-eks.md)
- [**`eks01`**](playground/index.html?exercise=eks01): EKS Pod Identity & IRSA ServiceAccounts
- [**`eks02`**](playground/index.html?exercise=eks02): AWS Load Balancer Controller & ALB Ingress
- [**`eks03`**](playground/index.html?exercise=eks03): AWS VPC CNI Security Groups for Pods
- [**`eks04`**](playground/index.html?exercise=eks04): Karpenter NodePool & EC2NodeClass

### [Chapter 28: Google Cloud GKE & Ecosystem](guides/28-gcp-gke.md)
- [**`gke01`**](playground/index.html?exercise=gke01): GKE Workload Identity Federation
- [**`gke02`**](playground/index.html?exercise=gke02): GKE Autopilot Workload Sizing & Compute Classes
- [**`gke03`**](playground/index.html?exercise=gke03): GKE Gateway API & Cloud Armor Policies
- [**`gke04`**](playground/index.html?exercise=gke04): Google Config Connector Cloud Resources

### [Chapter 29: Enterprise Multi-Account Governance & Secrets](guides/29-enterprise-governance.md)
- [**`eso01`**](playground/index.html?exercise=eso01): External Secrets Operator SecretStore & ExternalSecret
- [**`vault01`**](playground/index.html?exercise=vault01): HashiCorp Vault Agent Sidecar Injector
- [**`gov01`**](playground/index.html?exercise=gov01): ArgoCD ApplicationSet Multi-Cluster Matrix Generator
- [**`gov02`**](playground/index.html?exercise=gov02): Multi-Tenant Namespace Quotas & Security Policies

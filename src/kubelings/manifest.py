"""Curriculum manifest definition and lookup engine for Kubelings."""

from typing import Optional

from kubelings.models import Chapter, Exercise, Manifest


def build_manifest() -> Manifest:
    """Build and return the complete Kubelings curriculum manifest."""
    chapters = [
        Chapter(
            number=1,
            name="01_pods",
            title="Kubernetes Core Workloads & Pods",
            description="Pod Specifications, Multi-Container Sidecars, and Lifecycle",
            exercises=[
                Exercise(
                    name="pods01",
                    title="First Pod Manifest & Spec",
                    path="exercises/01_pods/pods01.yaml",
                    chapter_name="01_pods",
                    hints=[
                        "Set metadata.name to 'nginx-web'",
                        "Specify spec.containers[0].image as 'nginx:alpine'",
                        "Add containerPort 80 under ports",
                    ],
                ),
                Exercise(
                    name="pods02",
                    title="Multi-Container Pods & Sidecar Pattern",
                    path="exercises/01_pods/pods02.yaml",
                    chapter_name="01_pods",
                    hints=[
                        "Define an emptyDir volume under spec.volumes",
                        "Mount the shared volume into both app and sidecar container volumeMounts",
                        "Ensure both container names are distinct",
                    ],
                ),
                Exercise(
                    name="pods03",
                    title="Init Containers for Initialization",
                    path="exercises/01_pods/pods03.yaml",
                    chapter_name="01_pods",
                    hints=[
                        "Define an initContainers block in the pod spec",
                        "Configure init container to run before app containers",
                        "Init containers must exit successfully before main containers start",
                    ],
                ),
                Exercise(
                    name="pods04",
                    title="Resource Requests, Limits & QoS",
                    path="exercises/01_pods/pods04.yaml",
                    chapter_name="01_pods",
                    hints=[
                        "Set resources.requests and resources.limits for cpu and memory",
                        "Equal requests and limits yield Guaranteed QoS class",
                        "Burstable QoS occurs when requests are set less than limits",
                    ],
                ),
                Exercise(
                    name="pods05",
                    title="Downward API & Env Variables",
                    path="exercises/01_pods/pods05.yaml",
                    chapter_name="01_pods",
                    hints=[
                        "Use valueFrom.fieldRef.fieldPath to inject pod metadata",
                        "Set fieldPath to 'metadata.name' or 'status.podIP'",
                        "Map environment variables under spec.containers[].env",
                    ],
                ),
                Exercise(
                    name="pods06",
                    title="Pod Disruption Budgets & Static Pods",
                    path="exercises/01_pods/pods06.yaml",
                    chapter_name="01_pods",
                    hints=[
                        "Define a PodDisruptionBudget manifest with policy/v1",
                        "Set minAvailable or maxUnavailable in spec",
                        "Match target pod labels with spec.selector.matchLabels",
                    ],
                ),
            ],
        ),
        Chapter(
            number=2,
            name="02_controllers",
            title="Controllers & Replication",
            description="ReplicaSets, Deployments, StatefulSets, DaemonSets, and Jobs",
            exercises=[
                Exercise(
                    name="ctrl01",
                    title="ReplicaSets & Label Selectors",
                    path="exercises/02_controllers/ctrl01.yaml",
                    chapter_name="02_controllers",
                    hints=[
                        "Set apiVersion to 'apps/v1' and kind to 'ReplicaSet'",
                        "Ensure spec.selector.matchLabels matches spec.template.metadata.labels",
                        "Set spec.replicas to desired replica count",
                    ],
                ),
                Exercise(
                    name="ctrl02",
                    title="Deployments & Rolling Updates",
                    path="exercises/02_controllers/ctrl02.yaml",
                    chapter_name="02_controllers",
                    hints=[
                        "Set strategy.type to 'RollingUpdate'",
                        "Configure maxSurge and maxUnavailable in rollingUpdate strategy",
                        "Ensure template labels match selector labels",
                    ],
                ),
                Exercise(
                    name="ctrl03",
                    title="Deployment Rollbacks & Revision History",
                    path="exercises/02_controllers/ctrl03.yaml",
                    chapter_name="02_controllers",
                    hints=[
                        "Configure spec.revisionHistoryLimit to retain deployment revisions",
                        "Updating pod template container image triggers a new revision rollout",
                        "Rollout can be undone or rolled back to previous revisions",
                    ],
                ),
                Exercise(
                    name="ctrl04",
                    title="StatefulSets & Stable Network IDs",
                    path="exercises/02_controllers/ctrl04.yaml",
                    chapter_name="02_controllers",
                    hints=[
                        "StatefulSets require serviceName pointing to a headless Service",
                        "Define volumeClaimTemplates for persistent ordinal storage",
                        "Pod names follow ordinal indexing pattern <name>-0, <name>-1",
                    ],
                ),
                Exercise(
                    name="ctrl05",
                    title="DaemonSets for Node-Level Daemons",
                    path="exercises/02_controllers/ctrl05.yaml",
                    chapter_name="02_controllers",
                    hints=[
                        "DaemonSets run exactly one pod per eligible node",
                        "Use nodeSelector or tolerations to target specific node pools",
                        "Do not specify a replicas count on DaemonSets",
                    ],
                ),
                Exercise(
                    name="ctrl06",
                    title="Jobs & CronJobs",
                    path="exercises/02_controllers/ctrl06.yaml",
                    chapter_name="02_controllers",
                    hints=[
                        "Set completions and parallelism in Job spec",
                        "Use standard 5-part cron syntax for CronJob schedule (e.g. '0 0 * * *')",
                        "Set restartPolicy to 'OnFailure' or 'Never' in job pod template",
                    ],
                ),
            ],
        ),
        Chapter(
            number=3,
            name="03_config_secrets",
            title="Configuration & Secret Management",
            description="ConfigMaps, Secrets, In-Memory Mounts, and Immutability",
            exercises=[
                Exercise(
                    name="config01",
                    title="ConfigMaps as Environment Variables",
                    path="exercises/03_config_secrets/config01.yaml",
                    chapter_name="03_config_secrets",
                    hints=[
                        "Define ConfigMap with data key-value pairs",
                        "Use envFrom.configMapRef to inject all keys as environment variables",
                        "Use valueFrom.configMapKeyRef to inject specific keys",
                    ],
                ),
                Exercise(
                    name="config02",
                    title="ConfigMaps Mounted as Volumes",
                    path="exercises/03_config_secrets/config02.yaml",
                    chapter_name="03_config_secrets",
                    hints=[
                        "Define a volume with configMap source in pod spec",
                        "Mount volume under container volumeMounts",
                        "Use subPath to mount individual configuration files without masking directory contents",
                    ],
                ),
                Exercise(
                    name="config03",
                    title="Secrets & Base64 Encoding",
                    path="exercises/03_config_secrets/config03.yaml",
                    chapter_name="03_config_secrets",
                    hints=[
                        "Set kind to 'Secret' and type to 'Opaque'",
                        "Base64 encode values in data or provide raw strings in stringData",
                        "Reference secret keys in container env or volume mounts",
                    ],
                ),
                Exercise(
                    name="config04",
                    title="Secret Volume Mounts & Permissions",
                    path="exercises/03_config_secrets/config04.yaml",
                    chapter_name="03_config_secrets",
                    hints=[
                        "Mount secret as a volume with defaultMode set to octal permissions (e.g. 0400)",
                        "Secret volumes are backed by memory tmpfs by default",
                        "Ensure sensitive files have restricted read-only permissions",
                    ],
                ),
                Exercise(
                    name="config05",
                    title="Immutable ConfigMaps and Secrets",
                    path="exercises/03_config_secrets/config05.yaml",
                    chapter_name="03_config_secrets",
                    hints=[
                        "Set immutable: true at the top level of ConfigMap or Secret manifest",
                        "Immutable resources reduce kube-apiserver load by disabling watches",
                        "Modifications require creating a new resource with a distinct name",
                    ],
                ),
            ],
        ),
        Chapter(
            number=4,
            name="04_storage",
            title="Storage & Persistent Volumes",
            description="PVs, PVCs, Access Modes, StorageClasses, and Snapshots",
            exercises=[
                Exercise(
                    name="storage01",
                    title="Volume Types (emptyDir & hostPath)",
                    path="exercises/04_storage/storage01.yaml",
                    chapter_name="04_storage",
                    hints=[
                        "emptyDir provides scratch space tied to the pod lifecycle",
                        "hostPath mounts a file or directory from the host node filesystem",
                        "Specify hostPath path and type (e.g. DirectoryOrCreate)",
                    ],
                ),
                Exercise(
                    name="storage02",
                    title="PersistentVolumes & PersistentVolumeClaims",
                    path="exercises/04_storage/storage02.yaml",
                    chapter_name="04_storage",
                    hints=[
                        "PV represents cluster-wide storage provisioned by admin or dynamically",
                        "PVC requests storage matching capacity, access modes, and storageClassName",
                        "PVC binds to PV when storage requirements and access modes match",
                    ],
                ),
                Exercise(
                    name="storage03",
                    title="Access Modes & Reclaim Policies",
                    path="exercises/04_storage/storage03.yaml",
                    chapter_name="04_storage",
                    hints=[
                        "Access modes include ReadWriteOnce, ReadOnlyMany, ReadWriteMany",
                        "Reclaim policies include Retain, Delete, and Recycle",
                        "Retain preserves PV data for manual recovery after PVC deletion",
                    ],
                ),
                Exercise(
                    name="storage04",
                    title="StorageClasses & Dynamic Provisioning",
                    path="exercises/04_storage/storage04.yaml",
                    chapter_name="04_storage",
                    hints=[
                        "StorageClass defines volume provisioner and parameters",
                        "Set volumeBindingMode to WaitForFirstConsumer to delay binding until pod scheduling",
                        "Set reclaimPolicy to Delete or Retain on StorageClass",
                    ],
                ),
                Exercise(
                    name="storage05",
                    title="Volume Snapshots & Volume Expansion",
                    path="exercises/04_storage/storage05.yaml",
                    chapter_name="04_storage",
                    hints=[
                        "Set allowVolumeExpansion: true on StorageClass to enable PVC resizing",
                        "VolumeSnapshot captures a point-in-time state of a volume claim",
                        "VolumeSnapshotClass configures snapshot driver and parameters",
                    ],
                ),
            ],
        ),
        Chapter(
            number=5,
            name="05_services_networking",
            title="Services & Networking",
            description="ClusterIP, Headless, NodePort, LoadBalancer, and CoreDNS",
            exercises=[
                Exercise(
                    name="net01",
                    title="ClusterIP Services & Port Mapping",
                    path="exercises/05_services_networking/net01.yaml",
                    chapter_name="05_services_networking",
                    hints=[
                        "ClusterIP provides stable internal IP and DNS name",
                        "spec.ports: port is service port, targetPort is container port",
                        "spec.selector matches backend pod labels",
                    ],
                ),
                Exercise(
                    name="net02",
                    title="Headless Services & Stateful Addressing",
                    path="exercises/05_services_networking/net02.yaml",
                    chapter_name="05_services_networking",
                    hints=[
                        "Set spec.clusterIP to 'None' to create a headless service",
                        "DNS returns direct A/AAAA records for individual pod IPs",
                        "Used with StatefulSets for stable network identity and direct addressing",
                    ],
                ),
                Exercise(
                    name="net03",
                    title="NodePort & LoadBalancer Service Types",
                    path="exercises/05_services_networking/net03.yaml",
                    chapter_name="05_services_networking",
                    hints=[
                        "NodePort exposes service on static port (30000-32767) across all node IPs",
                        "LoadBalancer provisions cloud external load balancer pointing to NodePort",
                        "NodePort is automatically allocated if omitted",
                    ],
                ),
                Exercise(
                    name="net04",
                    title="CoreDNS Internal Service Resolution",
                    path="exercises/05_services_networking/net04.yaml",
                    chapter_name="05_services_networking",
                    hints=[
                        "FQDN format: <service-name>.<namespace>.svc.cluster.local",
                        "Same-namespace services are reachable by short name <service-name>",
                        "Cross-namespace queries use <service-name>.<namespace>",
                    ],
                ),
                Exercise(
                    name="net05",
                    title="ExternalName Services & Manual Endpoints",
                    path="exercises/05_services_networking/net05.yaml",
                    chapter_name="05_services_networking",
                    hints=[
                        "ExternalName maps service to external CNAME without proxying",
                        "Manual Endpoints/EndpointSlices map service without selector to custom IP addresses",
                        "Endpoint resource name must match Service name",
                    ],
                ),
            ],
        ),
        Chapter(
            number=6,
            name="06_ingress_gateway",
            title="Ingress & Gateway API",
            description="Ingress Controllers, Path Routing, TLS, and Gateway API",
            exercises=[
                Exercise(
                    name="ingress01",
                    title="Ingress Host & Path Routing",
                    path="exercises/06_ingress_gateway/ingress01.yaml",
                    chapter_name="06_ingress_gateway",
                    hints=[
                        "Define Ingress with networking.k8s.io/v1",
                        "Configure spec.rules with host and http.paths",
                        "Specify pathType as Prefix or Exact with backend service name and port",
                    ],
                ),
                Exercise(
                    name="ingress02",
                    title="Ingress TLS Termination",
                    path="exercises/06_ingress_gateway/ingress02.yaml",
                    chapter_name="06_ingress_gateway",
                    hints=[
                        "Add spec.tls array to Ingress resource",
                        "Specify hosts list and secretName containing TLS certificate and private key",
                        "Secret must be type kubernetes.io/tls in the same namespace",
                    ],
                ),
                Exercise(
                    name="ingress03",
                    title="Ingress Annotations & Rewrites",
                    path="exercises/06_ingress_gateway/ingress03.yaml",
                    chapter_name="06_ingress_gateway",
                    hints=[
                        "Use ingressClassName or kubernetes.io/ingress.class annotation",
                        "Set nginx.ingress.kubernetes.io/rewrite-target annotation for URL rewriting",
                        "Configure custom headers, SSL redirects, or timeouts via annotations",
                    ],
                ),
                Exercise(
                    name="ingress04",
                    title="Gateway API Fundamentals",
                    path="exercises/06_ingress_gateway/ingress04.yaml",
                    chapter_name="06_ingress_gateway",
                    hints=[
                        "Gateway API separates GatewayClass, Gateway, and HTTPRoute",
                        "HTTPRoute attaches to parent Gateway via parentRefs",
                        "Configure route rules, matches, and backendRefs to direct traffic",
                    ],
                ),
            ],
        ),
        Chapter(
            number=7,
            name="07_scheduling",
            title="Scheduling, Affinity & Advanced Placement",
            description="Node Placement, Affinity, Taints, Tolerations, and Topology Spread",
            exercises=[
                Exercise(
                    name="sched01",
                    title="Node Placement (nodeName & nodeSelector)",
                    path="exercises/07_scheduling/sched01.yaml",
                    chapter_name="07_scheduling",
                    hints=[
                        "spec.nodeName bypasses scheduler and assigns pod directly to a node",
                        "spec.nodeSelector matches key-value pairs against node labels",
                        "Node labels can be inspected with kubectl get nodes --show-labels",
                    ],
                ),
                Exercise(
                    name="sched02",
                    title="Node Affinity & Constraints",
                    path="exercises/07_scheduling/sched02.yaml",
                    chapter_name="07_scheduling",
                    hints=[
                        "requiredDuringSchedulingIgnoredDuringExecution is a hard requirement",
                        "preferredDuringSchedulingIgnoredDuringExecution specifies soft preference weights",
                        "Use matchExpressions with operators like In, NotIn, Exists, DoesNotExist",
                    ],
                ),
                Exercise(
                    name="sched03",
                    title="Pod Affinity & Pod Anti-Affinity",
                    path="exercises/07_scheduling/sched03.yaml",
                    chapter_name="07_scheduling",
                    hints=[
                        "topologyKey determines failure domain (e.g., kubernetes.io/hostname)",
                        "podAntiAffinity prevents co-locating pods with matching labels",
                        "podAffinity co-locates related pods with service dependencies",
                    ],
                ),
                Exercise(
                    name="sched04",
                    title="Taints and Tolerations",
                    path="exercises/07_scheduling/sched04.yaml",
                    chapter_name="07_scheduling",
                    hints=[
                        "Nodes have taints with key, value, and effect (NoSchedule, PreferNoSchedule, NoExecute)",
                        "Pods specify tolerations matching taint key, operator, value, and effect",
                        "tolerationSeconds configures eviction grace period for NoExecute taints",
                    ],
                ),
                Exercise(
                    name="sched05",
                    title="Topology Spread Constraints",
                    path="exercises/07_scheduling/sched05.yaml",
                    chapter_name="07_scheduling",
                    hints=[
                        "spec.topologySpreadConstraints evens distribution across zones or hosts",
                        "maxSkew defines maximum allowable difference in pod counts across domains",
                        "whenUnsatisfiable can be DoNotSchedule (hard) or ScheduleAnyway (soft)",
                    ],
                ),
            ],
        ),
        Chapter(
            number=8,
            name="08_security_rbac",
            title="Security, RBAC & Service Accounts",
            description="ServiceAccounts, Roles, ClusterRoles, SecurityContext, and PSS",
            exercises=[
                Exercise(
                    name="rbac01",
                    title="ServiceAccounts & Token Management",
                    path="exercises/08_security_rbac/rbac01.yaml",
                    chapter_name="08_security_rbac",
                    hints=[
                        "Define ServiceAccount with apiVersion: v1",
                        "Set automountServiceAccountToken: false to disable default token injection",
                        "Reference serviceAccountName in pod spec",
                    ],
                ),
                Exercise(
                    name="rbac02",
                    title="Roles & RoleBindings",
                    path="exercises/08_security_rbac/rbac02.yaml",
                    chapter_name="08_security_rbac",
                    hints=[
                        "Role defines namespace-scoped permissions (apiGroups, resources, verbs)",
                        "RoleBinding binds Role to Subjects (Users, Groups, ServiceAccounts)",
                        "Verbs include get, list, watch, create, update, patch, delete",
                    ],
                ),
                Exercise(
                    name="rbac03",
                    title="ClusterRoles & ClusterRoleBindings",
                    path="exercises/08_security_rbac/rbac03.yaml",
                    chapter_name="08_security_rbac",
                    hints=[
                        "ClusterRole grants cluster-wide permissions or non-resource URLs (/healthz)",
                        "ClusterRoleBinding grants permissions across all namespaces",
                        "ClusterRole can also be bound namespace-locally using standard RoleBinding",
                    ],
                ),
                Exercise(
                    name="rbac04",
                    title="Pod & Container SecurityContext",
                    path="exercises/08_security_rbac/rbac04.yaml",
                    chapter_name="08_security_rbac",
                    hints=[
                        "Set runAsNonRoot: true and runAsUser to a non-zero UID",
                        "Configure readOnlyRootFilesystem: true for immutability",
                        "Drop all capabilities and add only required ones (e.g. drop: ['ALL'])",
                    ],
                ),
                Exercise(
                    name="rbac05",
                    title="Pod Security Standards (PSS/PSA)",
                    path="exercises/08_security_rbac/rbac05.yaml",
                    chapter_name="08_security_rbac",
                    hints=[
                        "Namespace labels configure Pod Security Admission",
                        "pod-security.kubernetes.io/enforce: restricted",
                        "Modes include enforce, audit, and warn at levels privileged, baseline, restricted",
                    ],
                ),
            ],
        ),
        Chapter(
            number=9,
            name="09_network_policies",
            title="Network Policies & Traffic Segmentation",
            description="Default Deny, Ingress/Egress Isolation, and IPBlock Rules",
            exercises=[
                Exercise(
                    name="netpol01",
                    title="Default Deny Network Policy",
                    path="exercises/09_network_policies/netpol01.yaml",
                    chapter_name="09_network_policies",
                    hints=[
                        "Set policyTypes to ['Ingress', 'Egress'] with empty ingress and egress arrays",
                        "spec.podSelector: {} selects all pods in the namespace",
                        "Isolates namespace completely until explicit allow rules are defined",
                    ],
                ),
                Exercise(
                    name="netpol02",
                    title="Ingress Traffic Filtering",
                    path="exercises/09_network_policies/netpol02.yaml",
                    chapter_name="09_network_policies",
                    hints=[
                        "Define spec.ingress with 'from' selectors and 'ports'",
                        "from items can combine podSelector and namespaceSelector",
                        "Each from item in the list is evaluated as an OR condition",
                    ],
                ),
                Exercise(
                    name="netpol03",
                    title="Egress Traffic & DNS Access",
                    path="exercises/09_network_policies/netpol03.yaml",
                    chapter_name="09_network_policies",
                    hints=[
                        "Define spec.egress rules allowing specific destinations",
                        "Allow UDP/TCP port 53 to kube-system namespace for CoreDNS",
                        "Restrict external CIDRs with ipBlock",
                    ],
                ),
                Exercise(
                    name="netpol04",
                    title="Named Ports & IPBlock CIDR Exceptions",
                    path="exercises/09_network_policies/netpol04.yaml",
                    chapter_name="09_network_policies",
                    hints=[
                        "Use named ports in NetworkPolicy rules matching container port names",
                        "ipBlock.cidr defines allowed IP network range",
                        "ipBlock.except defines exclusions within the allowed CIDR",
                    ],
                ),
            ],
        ),
        Chapter(
            number=10,
            name="10_lifecycle_probes",
            title="Health Checking, Probes & Lifecycle",
            description="Liveness, Readiness, Startup Probes, and Termination Hooks",
            exercises=[
                Exercise(
                    name="health01",
                    title="Liveness Probes",
                    path="exercises/10_lifecycle_probes/health01.yaml",
                    chapter_name="10_lifecycle_probes",
                    hints=[
                        "Liveness probe restarts container if health check fails",
                        "Configurable mechanisms: httpGet, tcpSocket, exec.command",
                        "Set initialDelaySeconds, periodSeconds, and failureThreshold",
                    ],
                ),
                Exercise(
                    name="health02",
                    title="Readiness Probes",
                    path="exercises/10_lifecycle_probes/health02.yaml",
                    chapter_name="10_lifecycle_probes",
                    hints=[
                        "Readiness probe gates traffic from Service endpoints",
                        "Failed readiness probe removes pod IP from Service endpoints without restarting",
                        "Configured similarly to livenessProbe in container spec",
                    ],
                ),
                Exercise(
                    name="health03",
                    title="Startup Probes",
                    path="exercises/10_lifecycle_probes/health03.yaml",
                    chapter_name="10_lifecycle_probes",
                    hints=[
                        "Startup probe disables liveness and readiness checks until it succeeds",
                        "Prevents slow-starting legacy applications from being killed prematurely",
                        "Configure higher failureThreshold * periodSeconds to allow initialization time",
                    ],
                ),
                Exercise(
                    name="health04",
                    title="Lifecycle Hooks & Graceful Shutdown",
                    path="exercises/10_lifecycle_probes/health04.yaml",
                    chapter_name="10_lifecycle_probes",
                    hints=[
                        "lifecycle.preStop executes command or HTTP request before SIGTERM",
                        "terminationGracePeriodSeconds allows time for graceful connection draining",
                        "lifecycle.postStart executes asynchronously right after container creation",
                    ],
                ),
            ],
        ),
        Chapter(
            number=11,
            name="11_autoscaling",
            title="Autoscaling (HPA, VPA, KEDA)",
            description="Horizontal, Vertical, and Event-Driven Workload Autoscaling",
            exercises=[
                Exercise(
                    name="autoscale01",
                    title="Horizontal Pod Autoscaler (HPA v2)",
                    path="exercises/11_autoscaling/autoscale01.yaml",
                    chapter_name="11_autoscaling",
                    hints=[
                        "apiVersion: autoscaling/v2, kind: HorizontalPodAutoscaler",
                        "spec.scaleTargetRef points to Deployment or StatefulSet",
                        "Define metrics array with Resource (CPU/Memory) averageUtilization",
                    ],
                ),
                Exercise(
                    name="autoscale02",
                    title="HPA Custom Scaling Behavior",
                    path="exercises/11_autoscaling/autoscale02.yaml",
                    chapter_name="11_autoscaling",
                    hints=[
                        "spec.behavior allows configuring scaleUp and scaleDown policies independently",
                        "stabilizationWindowSeconds prevents rapid flapping (thrashing)",
                        "Define selectPolicy (Max, Min, Disabled) and step percentage/pods policies",
                    ],
                ),
                Exercise(
                    name="autoscale03",
                    title="Vertical Pod Autoscaler (VPA)",
                    path="exercises/11_autoscaling/autoscale03.yaml",
                    chapter_name="11_autoscaling",
                    hints=[
                        "VPA adjusts CPU/memory requests and limits automatically",
                        "spec.updatePolicy.updateMode can be Off (recommendation only), Initial, Auto",
                        "spec.resourcePolicy allows setting minAllowed and maxAllowed bounds",
                    ],
                ),
                Exercise(
                    name="autoscale04",
                    title="Event-Driven Autoscaling (KEDA)",
                    path="exercises/11_autoscaling/autoscale04.yaml",
                    chapter_name="11_autoscaling",
                    hints=[
                        "KEDA ScaledObject maps event triggers (Kafka, RabbitMQ, SQS, Prometheus) to workloads",
                        "Can scale workloads to zero replicas when no work is pending",
                        "spec.triggers defines trigger authentication and threshold metadata",
                    ],
                ),
            ],
        ),
        Chapter(
            number=12,
            name="12_crds_and_operators",
            title="Custom Resources, CRDs & Operators",
            description="CRD Schemas, Subresources, Python Operator Loops, and Webhooks",
            exercises=[
                Exercise(
                    name="crd01",
                    title="CustomResourceDefinition (CRD) Schema",
                    path="exercises/12_crds_and_operators/crd01.yaml",
                    chapter_name="12_crds_and_operators",
                    hints=[
                        "apiVersion: apiextensions.k8s.io/v1, kind: CustomResourceDefinition",
                        "spec.group, spec.names (kind, plural, singular), spec.scope (Namespaced/Cluster)",
                        "spec.versions[].schema.openAPIV3Schema defines JSON Schema properties",
                    ],
                ),
                Exercise(
                    name="crd02",
                    title="CRD Subresources & Printer Columns",
                    path="exercises/12_crds_and_operators/crd02.yaml",
                    chapter_name="12_crds_and_operators",
                    hints=[
                        "spec.versions[].subresources.status: {} enables /status subresource",
                        "spec.versions[].subresources.scale enables kubectl scale integration",
                        "additionalPrinterColumns customizes columns shown in kubectl get",
                    ],
                ),
                Exercise(
                    name="crd03",
                    title="Python Kubernetes Operator Loop",
                    path="exercises/12_crds_and_operators/crd03.yaml",
                    chapter_name="12_crds_and_operators",
                    hints=[
                        "Operator watches Custom Resource events using watch.Watch stream",
                        "Reconciliation loop compares desired spec vs observed state and reconciles",
                        "Updates status subresource with observed condition and phase",
                    ],
                ),
                Exercise(
                    name="crd04",
                    title="Dynamic Admission Webhooks",
                    path="exercises/12_crds_and_operators/crd04.yaml",
                    chapter_name="12_crds_and_operators",
                    hints=[
                        "MutatingWebhookConfiguration modifies objects before admission",
                        "ValidatingWebhookConfiguration accepts or rejects objects based on custom policy",
                        "Webhooks receive AdmissionReview JSON and return AdmissionResponse with patch/allowed",
                    ],
                ),
            ],
        ),
        Chapter(
            number=13,
            name="13_troubleshooting",
            title="Observability, Debugging & Production Troubleshooting",
            description="CrashLoopBackOff, ImagePullBackOff, Pending Pods, Quotas, and kubectl debug",
            exercises=[
                Exercise(
                    name="troubleshoot01",
                    title="Debugging CrashLoopBackOff & Exit Codes",
                    path="exercises/13_troubleshooting/troubleshoot01.yaml",
                    chapter_name="13_troubleshooting",
                    hints=[
                        "Exit code 137 indicates container was OOMKilled by Linux kernel",
                        "Exit code 1 indicates general application exception or missing configuration",
                        "Exit code 143 indicates graceful SIGTERM termination; inspect logs and exitCode",
                    ],
                ),
                Exercise(
                    name="troubleshoot02",
                    title="Debugging ImagePullBackOff",
                    path="exercises/13_troubleshooting/troubleshoot02.yaml",
                    chapter_name="13_troubleshooting",
                    hints=[
                        "ImagePullBackOff indicates failure to fetch container image",
                        "Check image repository URL, tag typo, and imagePullSecrets for private registries",
                        "Verify container registry network reachability",
                    ],
                ),
                Exercise(
                    name="troubleshoot03",
                    title="Debugging Pending Pods & Scheduling Failures",
                    path="exercises/13_troubleshooting/troubleshoot03.yaml",
                    chapter_name="13_troubleshooting",
                    hints=[
                        "Pending status usually means no node can satisfy resource requests or affinity/taints",
                        "Check kubectl describe pod events for FailedScheduling messages",
                        "Verify PVC binding status if pod mounts persistent volumes",
                    ],
                ),
                Exercise(
                    name="troubleshoot04",
                    title="ResourceQuotas & LimitRanges",
                    path="exercises/13_troubleshooting/troubleshoot04.yaml",
                    chapter_name="13_troubleshooting",
                    hints=[
                        "ResourceQuota limits total resource consumption (CPU, Memory, Pods) in a namespace",
                        "LimitRange sets default/min/max resource requests per container",
                        "Exceeding ResourceQuota causes apiserver to reject pod creation with 403 Forbidden",
                    ],
                ),
                Exercise(
                    name="troubleshoot05",
                    title="Ephemeral Debug Containers & Event Triage",
                    path="exercises/13_troubleshooting/troubleshoot05.yaml",
                    chapter_name="13_troubleshooting",
                    hints=[
                        "kubectl debug attaches ephemeral container to running pod for live diagnostics",
                        "Ephemeral containers share process namespace when shareProcessNamespace: true",
                        "Inspect Warning events across namespace to identify failure sequence",
                    ],
                ),
            ],
        ),
        Chapter(
            number=14,
            name="14_gitops_argocd",
            title="GitOps Continuous Delivery with ArgoCD",
            description="Application CRDs, ApplicationSets, Sync Policies, and Progressive Delivery Rollouts",
            exercises=[
                Exercise(
                    name="gitops01",
                    title="ArgoCD Application CRD & Sync Policies",
                    path="exercises/14_gitops_argocd/gitops01.yaml",
                    chapter_name="14_gitops_argocd",
                    hints=[
                        "Set apiVersion to argoproj.io/v1alpha1 and kind to Application",
                        "Configure source repoURL, targetRevision, and path",
                        "Enable automated.prune: true and automated.selfHeal: true under syncPolicy",
                    ],
                ),
                Exercise(
                    name="gitops02",
                    title="ArgoCD ApplicationSet Matrix Generator",
                    path="exercises/14_gitops_argocd/gitops02.yaml",
                    chapter_name="14_gitops_argocd",
                    hints=[
                        "ApplicationSets generate multiple Applications across clusters and folders",
                        "Use git directory generator under spec.generators",
                        "Reference {{path.basename}} in the template metadata and destination namespace",
                    ],
                ),
                Exercise(
                    name="gitops03",
                    title="Sync Windows, ServerSideApply & Retry Backoff",
                    path="exercises/14_gitops_argocd/gitops03.yaml",
                    chapter_name="14_gitops_argocd",
                    hints=[
                        "Include 'CreateNamespace=true' and 'ServerSideApply=true' in syncOptions",
                        "Configure exponential retry backoff with duration and factor",
                        "Automated sync policies ensure drift correction",
                    ],
                ),
                Exercise(
                    name="gitops04",
                    title="Progressive Delivery with Argo Rollouts",
                    path="exercises/14_gitops_argocd/gitops04.yaml",
                    chapter_name="14_gitops_argocd",
                    hints=[
                        "Argo Rollouts replaces Deployment with advanced canary and blue-green strategies",
                        "Define spec.strategy.canary.steps with setWeight and pause durations",
                        "Canary steps shift traffic gradually before full promotion",
                    ],
                ),
            ],
        ),
        Chapter(
            number=15,
            name="15_service_mesh_cilium",
            title="Service Mesh, eBPF & Cilium",
            description="CiliumNetworkPolicies, L7 HTTP Routing, Mutual TLS, and Hubble Observability",
            exercises=[
                Exercise(
                    name="mesh01",
                    title="Cilium L7 HTTP Filtering & Routing",
                    path="exercises/15_service_mesh_cilium/mesh01.yaml",
                    chapter_name="15_service_mesh_cilium",
                    hints=[
                        "Set apiVersion to cilium.io/v2 and kind to CiliumNetworkPolicy",
                        "Define endpointSelector to match target workload pods",
                        "Configure toPorts rules with http methods and paths under ingress",
                    ],
                ),
                Exercise(
                    name="mesh02",
                    title="Strict Mutual TLS & PeerAuthentication",
                    path="exercises/15_service_mesh_cilium/mesh02.yaml",
                    chapter_name="15_service_mesh_cilium",
                    hints=[
                        "PeerAuthentication configures namespace-wide mTLS encryption",
                        "Set spec.mtls.mode to 'STRICT'",
                        "Ensures all inter-service traffic is cryptographically authenticated",
                    ],
                ),
                Exercise(
                    name="mesh03",
                    title="CiliumClusterwideNetworkPolicy with DNS FQDN Egress",
                    path="exercises/15_service_mesh_cilium/mesh03.yaml",
                    chapter_name="15_service_mesh_cilium",
                    hints=[
                        "CiliumClusterwideNetworkPolicy applies across all cluster namespaces",
                        "Use toFQDNs with matchName and matchPattern for domain filtering",
                        "Intercept DNS traffic via port 53 / 443 rules",
                    ],
                ),
                Exercise(
                    name="mesh04",
                    title="Hubble Observability & OpenTelemetry Tracing",
                    path="exercises/15_service_mesh_cilium/mesh04.yaml",
                    chapter_name="15_service_mesh_cilium",
                    hints=[
                        "Attach prometheus.io/scrape and telemetry annotations to Pod metadata",
                        "Hubble extracts L4/L7 flow metrics via eBPF without code modification",
                        "Trace headers propagate distributed context across mesh services",
                    ],
                ),
            ],
        ),
        Chapter(
            number=16,
            name="16_policy_as_code",
            title="Policy as Code (Kyverno & Gatekeeper)",
            description="Kyverno ClusterPolicies, Mutating & Generate rules, and OPA Gatekeeper Constraints",
            exercises=[
                Exercise(
                    name="policy01",
                    title="Kyverno ClusterPolicy for Required Labels",
                    path="exercises/16_policy_as_code/policy01.yaml",
                    chapter_name="16_policy_as_code",
                    hints=[
                        "Set apiVersion to kyverno.io/v1 and kind to ClusterPolicy",
                        "Define validationFailureAction: Enforce under spec",
                        "Use pattern to validate metadata.labels keys and wildcards",
                    ],
                ),
                Exercise(
                    name="policy02",
                    title="Kyverno Mutating Policy for Security Defaults",
                    path="exercises/16_policy_as_code/policy02.yaml",
                    chapter_name="16_policy_as_code",
                    hints=[
                        "Use mutate.patchStrategicMerge under the rule definition",
                        "Inject securityContext.runAsNonRoot: true into pod specifications",
                        "Leading '+' in +(securityContext) ensures key is added if missing",
                    ],
                ),
                Exercise(
                    name="policy03",
                    title="Kyverno Generate Policy for Default Deny NetworkPolicy",
                    path="exercises/16_policy_as_code/policy03.yaml",
                    chapter_name="16_policy_as_code",
                    hints=[
                        "Define rule matching Namespace resource creation",
                        "Configure generate block with kind: NetworkPolicy and synchronize: true",
                        "Sets up automatic multi-tenant network isolation on new namespace creation",
                    ],
                ),
                Exercise(
                    name="policy04",
                    title="OPA Gatekeeper ConstraintTemplate & Constraint",
                    path="exercises/16_policy_as_code/policy04.yaml",
                    chapter_name="16_policy_as_code",
                    hints=[
                        "ConstraintTemplate defines custom CRD and Rego evaluation logic",
                        "Rego rule checks missing required labels against input.parameters",
                        "Violations yield actionable messages in admission decisions",
                    ],
                ),
            ],
        ),
        Chapter(
            number=17,
            name="17_multitenancy_vcluster",
            title="Multi-Tenancy & Virtual Clusters",
            description="Hierarchical Namespace Controller (HNC), Quotas, vcluster, and Tenant Isolation",
            exercises=[
                Exercise(
                    name="tenant01",
                    title="HNC Hierarchical Subnamespace Anchor",
                    path="exercises/17_multitenancy_vcluster/tenant01.yaml",
                    chapter_name="17_multitenancy_vcluster",
                    hints=[
                        "Set apiVersion to hnc.x-k8s.io/v1alpha2 and kind to SubnamespaceAnchor",
                        "Declare child subnamespace name and parent namespace in metadata",
                        "HNC automatically propagates RBAC and policies to child namespaces",
                    ],
                ),
                Exercise(
                    name="tenant02",
                    title="Tenant ResourceQuotas and LimitRanges",
                    path="exercises/17_multitenancy_vcluster/tenant02.yaml",
                    chapter_name="17_multitenancy_vcluster",
                    hints=[
                        "Combine ResourceQuota and LimitRange across multi-document YAML (---)",
                        "Quota limits total aggregate CPU/memory/pods per namespace",
                        "LimitRange sets default min/max container resource bounds",
                    ],
                ),
                Exercise(
                    name="tenant03",
                    title="Virtual Cluster (vcluster) Control Plane",
                    path="exercises/17_multitenancy_vcluster/tenant03.yaml",
                    chapter_name="17_multitenancy_vcluster",
                    hints=[
                        "Set kind to VirtualCluster and apiVersion to vcluster.loft.sh/v1alpha1",
                        "Configures lightweight k3s control plane inside a host namespace",
                        "Syncer syncs pods, services, and ingresses between virtual and host clusters",
                    ],
                ),
                Exercise(
                    name="tenant04",
                    title="Multi-Tenant Network Isolation & Egress Filtering",
                    path="exercises/17_multitenancy_vcluster/tenant04.yaml",
                    chapter_name="17_multitenancy_vcluster",
                    hints=[
                        "Define NetworkPolicy with ingress and egress policyTypes",
                        "Isolate pod traffic strictly within tenant namespace",
                        "Allow UDP port 53 egress to kube-system for cluster DNS",
                    ],
                ),
            ],
        ),
        Chapter(
            number=18,
            name="18_admission_webhooks",
            title="Advanced Admission Webhooks",
            description="Mutating & Validating Webhooks, Sidecar Injection, and CRD Conversion",
            exercises=[
                Exercise(
                    name="webhook01",
                    title="MutatingWebhookConfiguration Manifest",
                    path="exercises/18_admission_webhooks/webhook01.yaml",
                    chapter_name="18_admission_webhooks",
                    hints=[
                        "Set kind to MutatingWebhookConfiguration under admissionregistration.k8s.io/v1",
                        "Configure clientConfig with service name, namespace, path and caBundle",
                        "Define failurePolicy (Fail or Ignore) and timeoutSeconds",
                    ],
                ),
                Exercise(
                    name="webhook02",
                    title="ValidatingWebhookConfiguration Manifest",
                    path="exercises/18_admission_webhooks/webhook02.yaml",
                    chapter_name="18_admission_webhooks",
                    hints=[
                        "Set kind to ValidatingWebhookConfiguration",
                        "Filter targeted namespaces with namespaceSelector matchExpressions",
                        "Blocks invalid workloads before persistence in etcd",
                    ],
                ),
                Exercise(
                    name="webhook03",
                    title="Dynamic Sidecar Injection AdmissionReview Response",
                    path="exercises/18_admission_webhooks/webhook03.yaml",
                    chapter_name="18_admission_webhooks",
                    hints=[
                        "Return AdmissionReview payload with uid, allowed=True, patchType=JSONPatch",
                        "JSONPatch must be base64-encoded bytes",
                        "Injects telemetry/logging containers into targeted pods dynamically",
                    ],
                ),
                Exercise(
                    name="webhook04",
                    title="CRD Webhook Conversion Strategy",
                    path="exercises/18_admission_webhooks/webhook04.yaml",
                    chapter_name="18_admission_webhooks",
                    hints=[
                        "Set spec.conversion.strategy to 'Webhook'",
                        "Configure webhook.clientConfig and supported conversionReviewVersions",
                        "Allows seamless schema migration across CRD API versions",
                    ],
                ),
            ],
        ),
        Chapter(
            number=19,
            name="19_helm_packaging",
            title="Package Management with Helm",
            description="Chart Specifications, Go Templating, Values Schemas, and Subcharts",
            exercises=[
                Exercise(
                    name="helm01",
                    title="Helm Chart.yaml Metadata & Dependencies",
                    path="exercises/19_helm_packaging/helm01.yaml",
                    chapter_name="19_helm_packaging",
                    hints=[
                        "Set apiVersion to 'v2' for Helm v3 chart standard",
                        "Define version (chart version) and appVersion (application version)",
                        "Configure dependencies array with subchart name, version, and repository",
                    ],
                ),
                Exercise(
                    name="helm02",
                    title="Helm Go Templating & Named Helpers (_helpers.tpl)",
                    path="exercises/19_helm_packaging/helm02.yaml",
                    chapter_name="19_helm_packaging",
                    hints=[
                        "Implement fullname helper formatting release-chart naming",
                        "Truncate rendered resource names to 63 characters max",
                        "Render deployment manifest with dynamic release labels and image tags",
                    ],
                ),
                Exercise(
                    name="helm03",
                    title="Helm values.schema.json Validation Schema",
                    path="exercises/19_helm_packaging/helm03.yaml",
                    chapter_name="19_helm_packaging",
                    hints=[
                        "Use JSONSchema Draft-7 with $schema declaration",
                        "Define required array for replicaCount, image, and service",
                        "Set integer bounds for replicaCount and ports, and enum types for service.type",
                    ],
                ),
                Exercise(
                    name="helm04",
                    title="Helm Subcharts & Global Values",
                    path="exercises/19_helm_packaging/helm04.yaml",
                    chapter_name="19_helm_packaging",
                    hints=[
                        "Define global dictionary for cross-chart shared configuration",
                        "Override subchart parameters under top-level subchart keys (e.g. redis)",
                        "Pass configuration like architecture, auth, and persistence to dependencies",
                    ],
                ),
            ],
        ),
        Chapter(
            number=20,
            name="20_kustomize_overlays",
            title="Declarative Customization with Kustomize",
            description="Base Manifests, ConfigMap/Secret Generators, Patches, and Multi-Environment Overlays",
            exercises=[
                Exercise(
                    name="kustomize01",
                    title="Kustomize Base Manifests & Metadata Transformations",
                    path="exercises/20_kustomize_overlays/kustomize01.yaml",
                    chapter_name="20_kustomize_overlays",
                    hints=[
                        "Set apiVersion to kustomize.config.k8s.io/v1beta1 and kind to Kustomization",
                        "Specify base resources list and namespace",
                        "Apply namePrefix, commonLabels, and commonAnnotations across resources",
                    ],
                ),
                Exercise(
                    name="kustomize02",
                    title="Kustomize ConfigMap & Secret Generators",
                    path="exercises/20_kustomize_overlays/kustomize02.yaml",
                    chapter_name="20_kustomize_overlays",
                    hints=[
                        "Define configMapGenerator and secretGenerator lists with literals",
                        "generatorOptions controls name suffix hashing and default labels",
                        "Generators create immutable content hashes triggering seamless rollouts",
                    ],
                ),
                Exercise(
                    name="kustomize03",
                    title="Kustomize Strategic Merge & JSON6902 Target Patches",
                    path="exercises/20_kustomize_overlays/kustomize03.yaml",
                    chapter_name="20_kustomize_overlays",
                    hints=[
                        "Target specific resources by group, version, kind, and name",
                        "Apply JSON 6902 operations (replace, add, remove)",
                        "Modify replicas and container resource limits without altering bases",
                    ],
                ),
                Exercise(
                    name="kustomize04",
                    title="Kustomize Multi-Environment Overlays & Image Transforms",
                    path="exercises/20_kustomize_overlays/kustomize04.yaml",
                    chapter_name="20_kustomize_overlays",
                    hints=[
                        "Reference base manifests via resources path",
                        "Apply environment-specific namespaces and name prefixes",
                        "Use images and replicas lists to override image registries, tags, and scaling",
                    ],
                ),
            ],
        ),
        Chapter(
            number=21,
            name="21_gateway_api",
            title="Next-Gen Traffic Routing with Kubernetes Gateway API",
            description="GatewayClass, Gateway Listeners, HTTPRoute, Canary Traffic Splitting, and ReferenceGrant",
            exercises=[
                Exercise(
                    name="gateway01",
                    title="GatewayClass and Gateway Declaration",
                    path="exercises/21_gateway_api/gateway01.yaml",
                    chapter_name="21_gateway_api",
                    hints=[
                        "Set apiVersion to gateway.networking.k8s.io/v1 and kind to GatewayClass or Gateway",
                        "Configure controllerName in GatewayClass and gatewayClassName in Gateway",
                        "Define HTTP listener on port 80 with allowedRoutes namespace policy",
                    ],
                ),
                Exercise(
                    name="gateway02",
                    title="HTTPRoute Path & Header-Based Routing",
                    path="exercises/21_gateway_api/gateway02.yaml",
                    chapter_name="21_gateway_api",
                    hints=[
                        "Attach HTTPRoute to Gateway using parentRefs with name and namespace",
                        "Match path prefixes using PathPrefix type in rules",
                        "Add header matches under rules.matches to route traffic based on custom headers",
                    ],
                ),
                Exercise(
                    name="gateway03",
                    title="Canary Traffic Splitting & URL Rewriting",
                    path="exercises/21_gateway_api/gateway03.yaml",
                    chapter_name="21_gateway_api",
                    hints=[
                        "Specify multiple backendRefs with integer weight values summing to 100",
                        "Apply URLRewrite filter to rewrite URL prefixes before forwarding to backends",
                        "Use RequestHeaderModifier filter to inject custom tracing headers",
                    ],
                ),
                Exercise(
                    name="gateway04",
                    title="Cross-Namespace Security with ReferenceGrant",
                    path="exercises/21_gateway_api/gateway04.yaml",
                    chapter_name="21_gateway_api",
                    hints=[
                        "Create ReferenceGrant in target backend namespace to authorize cross-namespace references",
                        "Specify source HTTPRoute namespace in spec.from list",
                        "Grant access to specific Service resource names in spec.to list",
                    ],
                ),
            ],
        ),
        Chapter(
            number=22,
            name="22_crossplane_iac",
            title="Infrastructure as Data with Crossplane",
            description="CompositeResourceDefinitions (XRDs), Compositions, Managed Resources, and Developer Claims",
            exercises=[
                Exercise(
                    name="crossplane01",
                    title="CompositeResourceDefinition (XRD) Schema",
                    path="exercises/22_crossplane_iac/crossplane01.yaml",
                    chapter_name="22_crossplane_iac",
                    hints=[
                        "Define XRD under apiextensions.crossplane.io/v1 with group and names",
                        "Specify claimNames to allow developers to create namespaced claims",
                        "Define OpenAPI v3 schema validation rules for custom parameters",
                    ],
                ),
                Exercise(
                    name="crossplane02",
                    title="Composition and Field Path Transforms",
                    path="exercises/22_crossplane_iac/crossplane02.yaml",
                    chapter_name="22_crossplane_iac",
                    hints=[
                        "Link Composition to XRD via compositeTypeRef",
                        "Define base managed resources under spec.resources",
                        "Use FromCompositeFieldPath patches to map claim parameters to cloud resource fields",
                    ],
                ),
                Exercise(
                    name="crossplane03",
                    title="ProviderConfig and Resource Deletion Policies",
                    path="exercises/22_crossplane_iac/crossplane03.yaml",
                    chapter_name="22_crossplane_iac",
                    hints=[
                        "Configure ProviderConfig with credentials secret reference",
                        "Set providerConfigRef on managed cloud resources",
                        "Set deletionPolicy to Delete or Orphan depending on lifecycle needs",
                    ],
                ),
                Exercise(
                    name="crossplane04",
                    title="Developer Self-Service Claims & Connection Secrets",
                    path="exercises/22_crossplane_iac/crossplane04.yaml",
                    chapter_name="22_crossplane_iac",
                    hints=[
                        "Instantiate namespaced claim matching XRD claimNames.kind",
                        "Use compositionSelector to choose cloud provider or environment composition",
                        "Set writeConnectionSecretToRef to securely output generated credentials into a Secret",
                    ],
                ),
            ],
        ),
        Chapter(
            number=23,
            name="23_ebpf_tetragon",
            title="Kernel-Level Security & Observability with eBPF Tetragon",
            description="Process Execution Auditing, Sensitive File Tracing, Kernel Sigkill Actions, and Socket Probes",
            exercises=[
                Exercise(
                    name="tetragon01",
                    title="Process Execution Tracing with sys_execve",
                    path="exercises/23_ebpf_tetragon/tetragon01.yaml",
                    chapter_name="23_ebpf_tetragon",
                    hints=[
                        "Set apiVersion to cilium.io/v1alpha1 and kind to TracingPolicy",
                        "Trace sys_execve kprobe to capture all binary execution events in the kernel",
                        "Filter by namespace and binary prefix in matchNamespaces and matchArgs",
                    ],
                ),
                Exercise(
                    name="tetragon02",
                    title="Sensitive File & Credential Access Auditing",
                    path="exercises/23_ebpf_tetragon/tetragon02.yaml",
                    chapter_name="23_ebpf_tetragon",
                    hints=[
                        "Trace sys_openat syscall with path argument inspection at index 1",
                        "Specify sensitive paths like /etc/shadow or service account token directories",
                        "Monitor read and write attempts across container boundaries",
                    ],
                ),
                Exercise(
                    name="tetragon03",
                    title="Real-Time Kernel Sigkill Enforcement",
                    path="exercises/23_ebpf_tetragon/tetragon03.yaml",
                    chapter_name="23_ebpf_tetragon",
                    hints=[
                        "Match prohibited binaries such as sudo or nsenter with Exact operator",
                        "Configure matchActions with Sigkill to immediately terminate unauthorized processes in kernel space",
                        "Provides synchronous runtime prevention before syscall execution completes",
                    ],
                ),
                Exercise(
                    name="tetragon04",
                    title="eBPF TCP Socket & Network Egress Observability",
                    path="exercises/23_ebpf_tetragon/tetragon04.yaml",
                    chapter_name="23_ebpf_tetragon",
                    hints=[
                        "Attach kprobe to kernel tcp_connect function with sock argument type",
                        "Filter by workload namespaces requiring strict network auditing",
                        "Emit events via Post action to Tetragon gRPC stream for zero-overhead egress logging",
                    ],
                ),
            ],
        ),
        Chapter(
            number=24,
            name="24_kuberay_ml",
            title="Distributed AI & ML Orchestration with KubeRay",
            description="RayCluster Architectures, Heterogeneous Worker Pools, RayJob Batch Fine-Tuning, and RayService Serving",
            exercises=[
                Exercise(
                    name="ray01",
                    title="RayCluster Core Architecture & Head Node",
                    path="exercises/24_kuberay_ml/ray01.yaml",
                    chapter_name="24_kuberay_ml",
                    hints=[
                        "Set apiVersion to ray.io/v1 and kind to RayCluster with metadata.name ray-cluster-ml",
                        "In spec.headGroupSpec.rayStartParams, configure dashboard-host: '0.0.0.0' and block: 'true'",
                        "Expose container ports for GCS (6379) and Dashboard (8265) on the ray-head container",
                        "In spec.workerGroupSpecs, define worker-group with replicas: 2, minReplicas: 1, maxReplicas: 5, and 2 CPU / 4Gi memory limits",
                    ],
                ),
                Exercise(
                    name="ray02",
                    title="Heterogeneous Worker Pools & Autoscaling",
                    path="exercises/24_kuberay_ml/ray02.yaml",
                    chapter_name="24_kuberay_ml",
                    hints=[
                        "In spec.workerGroupSpecs, create two separate worker groups: cpu-workers and gpu-workers",
                        "Configure cpu-workers with 2 replicas, minReplicas: 2, maxReplicas: 10, and image rayproject/ray:2.35.0",
                        "Configure gpu-workers with 1 replica, minReplicas: 0, maxReplicas: 4, and resource limit nvidia.com/gpu: 1",
                    ],
                ),
                Exercise(
                    name="ray03",
                    title="RayJob for Distributed Batch Fine-Tuning",
                    path="exercises/24_kuberay_ml/ray03.yaml",
                    chapter_name="24_kuberay_ml",
                    hints=[
                        "Set apiVersion to ray.io/v1 and kind to RayJob with metadata.name ray-finetune-job",
                        "Set spec.entrypoint to 'python fine_tune.py --epochs 3'",
                        "Set spec.shutdownAfterJobFinishes to True and spec.ttlSecondsAfterFinished to 300",
                        "Define spec.rayClusterSpec with rayVersion '2.35.0' and ray-head container",
                    ],
                ),
                Exercise(
                    name="ray04",
                    title="RayService for Production LLM Serving",
                    path="exercises/24_kuberay_ml/ray04.yaml",
                    chapter_name="24_kuberay_ml",
                    hints=[
                        "Set apiVersion to ray.io/v1 and kind to RayService with metadata.name ray-llm-service",
                        "Set spec.serviceUnhealthyThreshold to 300",
                        "Configure spec.serveConfigV2 with application 'llm_app', route_prefix '/v1', and import_path 'llm_serve:model'",
                    ],
                ),
            ],
        ),
        Chapter(
            number=25,
            name="25_batch_kueue_volcano",
            title="AI Batch Scheduling & Queuing with Kueue and Volcano",
            description="Kueue Cohort Borrowing, Suspended Workloads, Volcano Gang Scheduling, and Fair-Share Queues",
            exercises=[
                Exercise(
                    name="kueue01",
                    title="Kueue ResourceFlavor & ClusterQueue Cohort Borrowing",
                    path="exercises/25_batch_kueue_volcano/kueue01.yaml",
                    chapter_name="25_batch_kueue_volcano",
                    hints=[
                        "Define ResourceFlavor 'default-flavor' and ClusterQueue 'cluster-queue-ai' with apiVersion kueue.x-k8s.io/v1beta1",
                        "Assign ClusterQueue to cohort 'ai-research-cohort'",
                        "Cover cpu (64 nominal, 32 borrowing), memory (256Gi), and nvidia.com/gpu (8 nominal, 4 borrowing) under default-flavor",
                    ],
                ),
                Exercise(
                    name="kueue02",
                    title="Kueue LocalQueue & Suspended Workload Gating",
                    path="exercises/25_batch_kueue_volcano/kueue02.yaml",
                    chapter_name="25_batch_kueue_volcano",
                    hints=[
                        "Define LocalQueue 'team-a-queue' in namespace team-a pointing to clusterQueue 'cluster-queue-ai'",
                        "Define batch/v1 Job 'train-job' in namespace team-a with label 'kueue.x-k8s.io/queue-name: team-a-queue'",
                        "Set Job spec.suspend to true so Kueue can gate admission until capacity is available",
                    ],
                ),
                Exercise(
                    name="volcano01",
                    title="Volcano Gang Scheduling & Deadlock Prevention",
                    path="exercises/25_batch_kueue_volcano/volcano01.yaml",
                    chapter_name="25_batch_kueue_volcano",
                    hints=[
                        "Set apiVersion to batch.volcano.sh/v1alpha1 and kind to Job with metadata.name distributed-training-gang",
                        "Set spec.minAvailable to 4 and spec.schedulerName to volcano for all-or-nothing gang scheduling",
                        "Define master task (1 replica, train-master) and worker task (3 replicas, train-worker) summing to minAvailable",
                    ],
                ),
                Exercise(
                    name="volcano02",
                    title="Volcano Queue & Fair-Share Scheduling",
                    path="exercises/25_batch_kueue_volcano/volcano02.yaml",
                    chapter_name="25_batch_kueue_volcano",
                    hints=[
                        "Set apiVersion to scheduling.volcano.sh/v1beta1 and kind to Queue with metadata.name ai-research-queue",
                        "Set spec.weight to 1 and spec.reclaimable to true",
                        "Define capability limits for cpu (64), memory (256Gi), and nvidia.com/gpu (8)",
                    ],
                ),
            ],
        ),
        Chapter(
            number=26,
            name="26_hardware_acceleration_dra",
            title="Hardware Acceleration: NVIDIA MIG, Apple Silicon GPU & DRA",
            description="NVIDIA MIG Slicing, Apple Silicon GPU / MPS Acceleration, Dynamic Resource Allocation (DRA), and Production vLLM LLM Serving",
            exercises=[
                Exercise(
                    name="accel01",
                    title="NVIDIA MIG Slicing & Partitioning",
                    path="exercises/26_hardware_acceleration_dra/accel01.yaml",
                    chapter_name="26_hardware_acceleration_dra",
                    hints=[
                        "Set spec.nodeSelector to 'nvidia.com/gpu.product: NVIDIA-A100-SXM4-80GB'",
                        "Set container resources limits and requests to 'nvidia.com/mig-3g.40gb: 1'",
                        "Configure environment variable NVIDIA_VISIBLE_DEVICES with value 'all'",
                    ],
                ),
                Exercise(
                    name="accel02",
                    title="Apple Silicon GPU & Metal MPS Acceleration",
                    path="exercises/26_hardware_acceleration_dra/accel02.yaml",
                    chapter_name="26_hardware_acceleration_dra",
                    hints=[
                        "Set spec.nodeSelector to 'kubernetes.io/arch: arm64'",
                        "Allocate Apple Silicon GPU with resource limit 'apple.com/gpu: 1'",
                        "Set env variables PYTORCH_ENABLE_MPS_FALLBACK to '1' and DEVICE to 'mps'",
                    ],
                ),
                Exercise(
                    name="accel03",
                    title="Dynamic Resource Allocation (DRA) Standard",
                    path="exercises/26_hardware_acceleration_dra/accel03.yaml",
                    chapter_name="26_hardware_acceleration_dra",
                    hints=[
                        "Define ResourceClaimTemplate gpu-dra-claim-template with apiVersion resource.k8s.io/v1alpha3",
                        "Specify device request dedicated-gpu with deviceClassName gpu.example.com and count 1",
                        "In Pod dra-workload-pod, define resourceClaim referencing the template and bind it under container resources.claims",
                    ],
                ),
                Exercise(
                    name="accel04",
                    title="Production vLLM LLM Inference Server",
                    path="exercises/26_hardware_acceleration_dra/accel04.yaml",
                    chapter_name="26_hardware_acceleration_dra",
                    hints=[
                        "Define Deployment vllm-openai-server with image vllm/vllm-openai:latest and matchLabels app: vllm-server",
                        "Configure args with --model meta-llama/Llama-3-8B-Instruct, --gpu-memory-utilization 0.90, and --port 8000",
                        "Allocate 1 GPU with nvidia.com/gpu: 1, configure readiness probe on /health:8000, and mount model-weights-pvc",
                    ],
                ),
            ],
        ),
        Chapter(
            number=27,
            name="27_aws_eks",
            title="AWS EKS & Cloud Architecture",
            description="IRSA, EKS Pod Identity, AWS Load Balancer Controller, VPC CNI, and Karpenter",
            exercises=[
                Exercise(
                    name="eks01",
                    title="EKS Pod Identity & IRSA ServiceAccounts",
                    path="exercises/27_aws_eks/eks01.yaml",
                    chapter_name="27_aws_eks",
                    hints=[
                        "Annotate ServiceAccount with eks.amazonaws.com/role-arn: arn:aws:iam::123456789012:role/my-app-role",
                        "Configure projected serviceAccountToken with audience sts.amazonaws.com",
                        "Mount AWS web identity token volume at /var/run/secrets/eks.amazonaws.com/serviceaccount",
                    ],
                ),
                Exercise(
                    name="eks02",
                    title="AWS Load Balancer Controller & ALB Ingress",
                    path="exercises/27_aws_eks/eks02.yaml",
                    chapter_name="27_aws_eks",
                    hints=[
                        "Set ingressClassName: alb or annotate kubernetes.io/ingress.class: alb",
                        "Add annotation alb.ingress.kubernetes.io/scheme: internet-facing",
                        "Set alb.ingress.kubernetes.io/target-type: ip for direct pod IP routing",
                    ],
                ),
                Exercise(
                    name="eks03",
                    title="AWS VPC CNI Security Groups for Pods",
                    path="exercises/27_aws_eks/eks03.yaml",
                    chapter_name="27_aws_eks",
                    hints=[
                        "Define SecurityGroupPolicy with apiVersion vpcresources.k8s.aws/v1alpha1",
                        "Configure podSelector matching target application labels",
                        "Specify securityGroups.groups with AWS security group IDs (e.g. sg-0123456789abcdef0)",
                    ],
                ),
                Exercise(
                    name="eks04",
                    title="Karpenter NodePool & EC2NodeClass",
                    path="exercises/27_aws_eks/eks04.yaml",
                    chapter_name="27_aws_eks",
                    hints=[
                        "Define NodePool with apiVersion karpenter.sh/v1 referencing template spec",
                        "Configure requirements for node.kubernetes.io/instance-type or karpenter.k8s.aws/instance-family",
                        "Specify EC2NodeClass with amiFamily AL2023 and subnetSelectorTerms",
                    ],
                ),
            ],
        ),
        Chapter(
            number=28,
            name="28_gcp_gke",
            title="Google Cloud GKE & Ecosystem",
            description="Workload Identity Federation, GKE Autopilot, GKE Gateway API, and Config Connector",
            exercises=[
                Exercise(
                    name="gke01",
                    title="GKE Workload Identity Federation",
                    path="exercises/28_gcp_gke/gke01.yaml",
                    chapter_name="28_gcp_gke",
                    hints=[
                        "Annotate ServiceAccount with iam.gke.io/gcp-service-account: app-gsa@project.iam.gserviceaccount.com",
                        "Ensure Pod specifies serviceAccountName referencing the annotated ServiceAccount",
                        "Configure nodeSelector with iam.gke.io/gke-metadata-server-enabled: 'true'",
                    ],
                ),
                Exercise(
                    name="gke02",
                    title="GKE Autopilot Workload Sizing & Compute Classes",
                    path="exercises/28_gcp_gke/gke02.yaml",
                    chapter_name="28_gcp_gke",
                    hints=[
                        "In GKE Autopilot, resource requests equal resource limits if limits are omitted",
                        "Add annotation autopilot.gke.io/compute-class: Performance or Scale-Out",
                        "Specify resources.requests with valid Autopilot CPU/memory increments",
                    ],
                ),
                Exercise(
                    name="gke03",
                    title="GKE Gateway API & Cloud Armor Policies",
                    path="exercises/28_gcp_gke/gke03.yaml",
                    chapter_name="28_gcp_gke",
                    hints=[
                        "Define GCPBackendPolicy with apiVersion networking.gke.io/v1",
                        "Target HTTPRoute or Service under spec.targetRef",
                        "Attach Cloud Armor security policy under spec.default.securityPolicy",
                    ],
                ),
                Exercise(
                    name="gke04",
                    title="Google Config Connector Cloud Resources",
                    path="exercises/28_gcp_gke/gke04.yaml",
                    chapter_name="28_gcp_gke",
                    hints=[
                        "Define StorageBucket with apiVersion storage.cnrm.cloud.google.com/v1beta1",
                        "Set uniformBucketLevelAccess: true and storageClass: STANDARD",
                        "Configure cnrm.cloud.google.com/deletion-policy: abandon annotation",
                    ],
                ),
            ],
        ),
        Chapter(
            number=29,
            name="29_enterprise_governance",
            title="Enterprise Multi-Account Governance & Secrets",
            description="AWS Control Tower, External Secrets Operator, HashiCorp Vault, and ArgoCD ApplicationSets",
            exercises=[
                Exercise(
                    name="eso01",
                    title="External Secrets Operator SecretStore & ExternalSecret",
                    path="exercises/29_enterprise_governance/eso01.yaml",
                    chapter_name="29_enterprise_governance",
                    hints=[
                        "Define SecretStore with apiVersion external-secrets.io/v1beta1 provider aws/secretsManager or gcp/secretManager",
                        "Define ExternalSecret referencing secretStoreRef",
                        "Specify target.name for the materialized Kubernetes Secret and data.remoteRef.key",
                    ],
                ),
                Exercise(
                    name="vault01",
                    title="HashiCorp Vault Agent Sidecar Injector",
                    path="exercises/29_enterprise_governance/vault01.yaml",
                    chapter_name="29_enterprise_governance",
                    hints=[
                        "Add annotation vault.hashicorp.com/agent-inject: 'true'",
                        "Specify vault.hashicorp.com/role with Kubernetes auth role name",
                        "Define vault.hashicorp.com/agent-inject-secret-<filename> with secret engine path",
                    ],
                ),
                Exercise(
                    name="gov01",
                    title="ArgoCD ApplicationSet Multi-Cluster Matrix Generator",
                    path="exercises/29_enterprise_governance/gov01.yaml",
                    chapter_name="29_enterprise_governance",
                    hints=[
                        "Define ApplicationSet with apiVersion argoproj.io/v1alpha1",
                        "Configure spec.generators with matrix combining clusters and git directories",
                        "Set spec.template.destination.server: '{{server}}' and path: '{{path}}'",
                    ],
                ),
                Exercise(
                    name="gov02",
                    title="Multi-Tenant Namespace Quotas & Security Policies",
                    path="exercises/29_enterprise_governance/gov02.yaml",
                    chapter_name="29_enterprise_governance",
                    hints=[
                        "Define ResourceQuota limiting requests.cpu, requests.memory, and persistentvolumeclaims",
                        "Define LimitRange specifying default container request and limit boundaries",
                        "Enforce pod-security.kubernetes.io/enforce: restricted label on tenant namespace",
                    ],
                ),
            ],
        ),
    ]
    return Manifest(chapters=chapters)


_MANIFEST: Optional[Manifest] = None


def get_manifest() -> Manifest:
    """Return the cached singleton Manifest instance."""
    global _MANIFEST
    if _MANIFEST is None:
        _MANIFEST = build_manifest()
    return _MANIFEST


def get_exercise_by_name(name: str) -> Optional[Exercise]:
    """Find an exercise by name, exact path, or ending path/filename."""
    for ex in get_manifest().all_exercises:
        if ex.name == name or ex.path == name or ex.path.endswith(f"/{name}"):
            return ex
    return None


def get_next_exercise(current_name: str) -> Optional[Exercise]:
    """Return the next sequential exercise after current_name across all chapters."""
    exercises = get_manifest().all_exercises
    for i, ex in enumerate(exercises):
        if (
            ex.name == current_name
            or ex.path == current_name
            or ex.path.endswith(f"/{current_name}")
        ):
            if i + 1 < len(exercises):
                return exercises[i + 1]
    return None

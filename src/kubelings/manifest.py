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
                    path="exercises/01_pods/pods01.py",
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
                    path="exercises/01_pods/pods02.py",
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
                    path="exercises/01_pods/pods03.py",
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
                    path="exercises/01_pods/pods04.py",
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
                    path="exercises/01_pods/pods05.py",
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
                    path="exercises/01_pods/pods06.py",
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
                    path="exercises/02_controllers/ctrl01.py",
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
                    path="exercises/02_controllers/ctrl02.py",
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
                    path="exercises/02_controllers/ctrl03.py",
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
                    path="exercises/02_controllers/ctrl04.py",
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
                    path="exercises/02_controllers/ctrl05.py",
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
                    path="exercises/02_controllers/ctrl06.py",
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
                    path="exercises/03_config_secrets/config01.py",
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
                    path="exercises/03_config_secrets/config02.py",
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
                    path="exercises/03_config_secrets/config03.py",
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
                    path="exercises/03_config_secrets/config04.py",
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
                    path="exercises/03_config_secrets/config05.py",
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
                    path="exercises/04_storage/storage01.py",
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
                    path="exercises/04_storage/storage02.py",
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
                    path="exercises/04_storage/storage03.py",
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
                    path="exercises/04_storage/storage04.py",
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
                    path="exercises/04_storage/storage05.py",
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
                    path="exercises/05_services_networking/net01.py",
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
                    path="exercises/05_services_networking/net02.py",
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
                    path="exercises/05_services_networking/net03.py",
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
                    path="exercises/05_services_networking/net04.py",
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
                    path="exercises/05_services_networking/net05.py",
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
                    path="exercises/06_ingress_gateway/ingress01.py",
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
                    path="exercises/06_ingress_gateway/ingress02.py",
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
                    path="exercises/06_ingress_gateway/ingress03.py",
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
                    path="exercises/06_ingress_gateway/ingress04.py",
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
                    path="exercises/07_scheduling/sched01.py",
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
                    path="exercises/07_scheduling/sched02.py",
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
                    path="exercises/07_scheduling/sched03.py",
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
                    path="exercises/07_scheduling/sched04.py",
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
                    path="exercises/07_scheduling/sched05.py",
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
                    path="exercises/08_security_rbac/rbac01.py",
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
                    path="exercises/08_security_rbac/rbac02.py",
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
                    path="exercises/08_security_rbac/rbac03.py",
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
                    path="exercises/08_security_rbac/rbac04.py",
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
                    path="exercises/08_security_rbac/rbac05.py",
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
                    path="exercises/09_network_policies/netpol01.py",
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
                    path="exercises/09_network_policies/netpol02.py",
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
                    path="exercises/09_network_policies/netpol03.py",
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
                    path="exercises/09_network_policies/netpol04.py",
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
                    path="exercises/10_lifecycle_probes/health01.py",
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
                    path="exercises/10_lifecycle_probes/health02.py",
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
                    path="exercises/10_lifecycle_probes/health03.py",
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
                    path="exercises/10_lifecycle_probes/health04.py",
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
                    path="exercises/11_autoscaling/autoscale01.py",
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
                    path="exercises/11_autoscaling/autoscale02.py",
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
                    path="exercises/11_autoscaling/autoscale03.py",
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
                    path="exercises/11_autoscaling/autoscale04.py",
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
                    path="exercises/12_crds_and_operators/crd01.py",
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
                    path="exercises/12_crds_and_operators/crd02.py",
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
                    path="exercises/12_crds_and_operators/crd03.py",
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
                    path="exercises/12_crds_and_operators/crd04.py",
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
                    path="exercises/13_troubleshooting/troubleshoot01.py",
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
                    path="exercises/13_troubleshooting/troubleshoot02.py",
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
                    path="exercises/13_troubleshooting/troubleshoot03.py",
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
                    path="exercises/13_troubleshooting/troubleshoot04.py",
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
                    path="exercises/13_troubleshooting/troubleshoot05.py",
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
                    path="exercises/14_gitops_argocd/gitops01.py",
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
                    path="exercises/14_gitops_argocd/gitops02.py",
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
                    path="exercises/14_gitops_argocd/gitops03.py",
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
                    path="exercises/14_gitops_argocd/gitops04.py",
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
                    path="exercises/15_service_mesh_cilium/mesh01.py",
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
                    path="exercises/15_service_mesh_cilium/mesh02.py",
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
                    path="exercises/15_service_mesh_cilium/mesh03.py",
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
                    path="exercises/15_service_mesh_cilium/mesh04.py",
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
                    path="exercises/16_policy_as_code/policy01.py",
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
                    path="exercises/16_policy_as_code/policy02.py",
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
                    path="exercises/16_policy_as_code/policy03.py",
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
                    path="exercises/16_policy_as_code/policy04.py",
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
                    path="exercises/17_multitenancy_vcluster/tenant01.py",
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
                    path="exercises/17_multitenancy_vcluster/tenant02.py",
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
                    path="exercises/17_multitenancy_vcluster/tenant03.py",
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
                    path="exercises/17_multitenancy_vcluster/tenant04.py",
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
                    path="exercises/18_admission_webhooks/webhook01.py",
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
                    path="exercises/18_admission_webhooks/webhook02.py",
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
                    path="exercises/18_admission_webhooks/webhook03.py",
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
                    path="exercises/18_admission_webhooks/webhook04.py",
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
                    path="exercises/19_helm_packaging/helm01.py",
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
                    path="exercises/19_helm_packaging/helm02.py",
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
                    path="exercises/19_helm_packaging/helm03.py",
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
                    path="exercises/19_helm_packaging/helm04.py",
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
                    path="exercises/20_kustomize_overlays/kustomize01.py",
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
                    path="exercises/20_kustomize_overlays/kustomize02.py",
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
                    path="exercises/20_kustomize_overlays/kustomize03.py",
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
                    path="exercises/20_kustomize_overlays/kustomize04.py",
                    chapter_name="20_kustomize_overlays",
                    hints=[
                        "Reference base manifests via resources path",
                        "Apply environment-specific namespaces and name prefixes",
                        "Use images and replicas lists to override image registries, tags, and scaling",
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

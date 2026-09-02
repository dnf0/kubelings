"""Generate 26 in-depth Kubernetes Reference Guides for MkDocs with full manifests, diagrams, and bidirectional links."""

import textwrap
from pathlib import Path

from kubelings.manifest import build_manifest

REPO_ROOT = Path(__file__).resolve().parent.parent
GUIDES_DIR = REPO_ROOT / "docs" / "guides"
GUIDES_DIR.mkdir(parents=True, exist_ok=True)

manifest = build_manifest()

CHAPTER_DATA = {
    1: {
        "slug": "01-pods",
        "api_groups": "`v1` &bull; `Pod`, `PodDisruptionBudget`",
        "diagram": """
    ┌─────────────────────────────────────────────────────────────┐
    │                         Kubelet                             │
    │  ┌─────────────────┐             ┌───────────────────────┐  │
    │  │  Init Container │             │  Main App Container   │  │
    │  │  (runs to exit) │ ──(Shared)─►│  (nginx / python)     │  │
    │  └────────┬────────┘   Volumes   └───────────┬───────────┘  │
    │           │                                  │              │
    │           ▼                                  ▼              │
    │     [ emptyDir / ]                     [ emptyDir / ]       │
    │     [ ConfigMap  ]                     [ Secret     ]       │
    │                                              ▲              │
    │                                  ┌───────────┴───────────┐  │
    │                                  │   Sidecar Container   │  │
    │                                  │   (fluent-bit / proxy)│  │
    │                                  └───────────────────────┘  │
    └─────────────────────────────────────────────────────────────┘
""",
        "primary_manifest": """apiVersion: v1
kind: Pod
metadata:
  name: production-web-service
  namespace: default
  labels:
    app.kubernetes.io/name: web-service
    app.kubernetes.io/component: frontend
    app.kubernetes.io/part-of: e-commerce
spec:
  restartPolicy: Always
  terminationGracePeriodSeconds: 30
  initContainers:
  - name: init-db-check
    image: busybox:1.36
    command: ['sh', '-c', 'echo "Waiting for database ready..."; sleep 2;']
    resources:
      limits:
        cpu: "100m"
        memory: "64Mi"
      requests:
        cpu: "50m"
        memory: "32Mi"
  containers:
  - name: web-app
    image: nginx:1.27-alpine
    ports:
    - name: http
      containerPort: 80
      protocol: TCP
    resources:
      limits:
        cpu: "500m"
        memory: "256Mi"
      requests:
        cpu: "250m"
        memory: "128Mi"
    volumeMounts:
    - name: shared-logs
      mountPath: /var/log/nginx
  - name: log-collector
    image: busybox:1.36
    command: ['sh', '-c', 'tail -F /var/log/nginx/access.log 2>/dev/null || true']
    volumeMounts:
    - name: shared-logs
      mountPath: /var/log/nginx
  volumes:
  - name: shared-logs
    emptyDir: {}
""",
        "fields": [
            (
                "`spec.initContainers`",
                "Array",
                "Containers executed sequentially before app containers start. Must exit with code 0.",
            ),
            (
                "`spec.containers[*].resources`",
                "Object",
                "Compute requests (scheduler quota) and limits (cgroup enforcement).",
            ),
            (
                "`spec.volumes`",
                "Array",
                "Shared storage abstractions mounted into container filesystems.",
            ),
            (
                "`spec.terminationGracePeriodSeconds`",
                "Integer (Default: 30)",
                "Duration given for SIGTERM handling before SIGKILL is dispatched.",
            ),
        ],
        "patterns": [
            (
                "Sidecar Logging Pattern",
                """apiVersion: v1
kind: Pod
metadata:
  name: sidecar-log-processor
spec:
  containers:
  - name: app
    image: alpine:3.20
    command: ["sh", "-c", "while true; do date >> /logs/app.log; sleep 1; done"]
    volumeMounts:
    - name: log-volume
      mountPath: /logs
  - name: shipper
    image: busybox:1.36
    command: ["sh", "-c", "tail -f /logs/app.log"]
    volumeMounts:
    - name: log-volume
      mountPath: /logs
  volumes:
  - name: log-volume
    emptyDir: {}
""",
            ),
            (
                "Downward API Metadata Injection",
                """apiVersion: v1
kind: Pod
metadata:
  name: downward-api-env
  labels:
    tier: frontend
spec:
  containers:
  - name: client
    image: busybox:1.36
    command: ["sh", "-c", "env | grep POD_ && sleep 3600"]
    env:
    - name: POD_NAME
      valueFrom:
        fieldRef:
          fieldPath: metadata.name
    - name: POD_NAMESPACE
      valueFrom:
        fieldRef:
          fieldPath: metadata.namespace
    - name: POD_IP
      valueFrom:
        fieldRef:
          fieldPath: status.podIP
""",
            ),
        ],
        "hardening": [
            "Always set both `requests` and `limits` to establish predictable QoS classes (Guaranteed vs Burstable).",
            "Set `securityContext.runAsNonRoot: true` and `securityContext.readOnlyRootFilesystem: true`.",
            "Drop all Linux capabilities with `capabilities.drop: ['ALL']` and add back only strictly necessary capabilities (e.g. `NET_BIND_SERVICE`).",
            "Pair multi-instance workloads with `PodDisruptionBudget` to ensure high availability during node drains.",
        ],
        "troubleshooting": [
            (
                "`CrashLoopBackOff`",
                "Container starts and exits immediately with an error code.",
                "1. Inspect exit code: `kubectl get pod <name> -o jsonpath='{.status.containerStatuses[*].state.terminated}'`\n2. Check previous container logs: `kubectl logs <name> -c <container> --previous`\n3. Verify entrypoint args and required environment variables.",
            ),
            (
                "`OOMKilled` (Exit Code 137)",
                "Container exceeded its memory limit cgroup.",
                "1. Run `kubectl describe pod <name>` and look for `Last State: Terminated / Reason: OOMKilled`.\n2. Increase `resources.limits.memory` or profile application heap memory consumption.",
            ),
            (
                "`Pending` (Scheduling Failure)",
                "Scheduler cannot find a node meeting CPU/memory/taint requirements.",
                "1. Inspect scheduling events: `kubectl describe pod <name>`\n2. Review cluster capacity: `kubectl describe nodes | grep -A 8 'Allocated resources'`.",
            ),
        ],
    },
    2: {
        "slug": "02-controllers",
        "api_groups": "`apps/v1`, `batch/v1` &bull; `Deployment`, `StatefulSet`, `DaemonSet`, `Job`, `CronJob`",
        "diagram": """
    ┌───────────────────────────┐
    │     Deployment Controller │
    └─────────────┬─────────────┘
                  │ Manages ReplicaSets (Rollouts, Revisions)
                  ▼
    ┌───────────────────────────┐
    │         ReplicaSet        │
    └─────────────┬─────────────┘
                  │ Maintains Desired Spec Replicas
                  ▼
    ┌───────────┐   ┌───────────┐   ┌───────────┐
    │  Pod 1    │   │  Pod 2    │   │  Pod 3    │
    └───────────┘   └───────────┘   └───────────┘
""",
        "primary_manifest": """apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-service
  labels:
    app: api-service
spec:
  replicas: 3
  revisionHistoryLimit: 5
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: api-service
  template:
    metadata:
      labels:
        app: api-service
    spec:
      containers:
      - name: api
        image: nginx:1.27-alpine
        ports:
        - containerPort: 8080
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 250m
            memory: 256Mi
""",
        "fields": [
            (
                "`spec.strategy.rollingUpdate`",
                "Object",
                "Controls zero-downtime rollouts via `maxSurge` (surge capacity) and `maxUnavailable` (tolerated disruption).",
            ),
            (
                "`spec.selector.matchLabels`",
                "Map",
                "Immutable label query used by the controller to discover its owned Pods. Must match `spec.template.metadata.labels`.",
            ),
            (
                "`spec.revisionHistoryLimit`",
                "Integer (Default: 10)",
                "Number of historical ReplicaSets retained for instant rollbacks.",
            ),
        ],
        "patterns": [
            (
                "StatefulSet with VolumeClaimTemplates",
                """apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: redis-cluster
spec:
  serviceName: redis-headless
  replicas: 3
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:7.2-alpine
        ports:
        - containerPort: 6379
        volumeMounts:
        - name: data
          mountPath: /data
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 5Gi
""",
            ),
            (
                "CronJob with Concurrency Policy",
                """apiVersion: batch/v1
kind: CronJob
metadata:
  name: nightly-backup
spec:
  schedule: "0 2 * * *"
  concurrencyPolicy: Forbid
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 1
  jobTemplate:
    spec:
      backoffLimit: 2
      template:
        spec:
          restartPolicy: OnFailure
          containers:
          - name: backup
            image: busybox:1.36
            command: ["sh", "-c", "echo 'Running DB dump...'; exit 0"]
""",
            ),
        ],
        "hardening": [
            "Use `maxUnavailable: 0` during rolling updates to guarantee baseline capacity is never reduced.",
            "Avoid orphan ReplicaSets by always setting `revisionHistoryLimit`.",
            "StatefulSets should be paired with headless Services for stable network identities (`$(pod-name).$(service-name).$(namespace).svc.cluster.local`).",
        ],
        "troubleshooting": [
            (
                "Rollout Stuck / Deployment Blocked",
                "New ReplicaSet cannot progress due to image pull or readiness probe failures.",
                "1. View rollout status: `kubectl rollout status deployment/<name>`\n2. Inspect rollout history: `kubectl rollout history deployment/<name>`\n3. Roll back immediately: `kubectl rollout undo deployment/<name>`",
            ),
            (
                "StatefulSet Pod Stuck Terminating",
                "Volume detach/attach cycle locked or node unready.",
                "1. Check PV status: `kubectl get pvc -l app=<name>`\n2. Inspect node status: `kubectl describe node <node>`",
            ),
        ],
    },
    3: {
        "slug": "03-config-secrets",
        "api_groups": "`v1` &bull; `ConfigMap`, `Secret`",
        "diagram": """
    ┌─────────────────────────────────────────────────────────────┐
    │                      Kubernetes API                         │
    │   ┌────────────────────┐          ┌─────────────────────┐   │
    │   │  ConfigMap (Plain) │          │ Secret (Base64/KMS) │   │
    │   └─────────┬──────────┘          └──────────┬──────────┘   │
    └─────────────┼────────────────────────────────┼──────────────┘
                  │                                │
                  ▼ Mounted as Files / Env Vars    ▼
    ┌─────────────────────────────────────────────────────────────┐
    │                         Pod Spec                            │
    │  • envFrom: configMapRef / secretRef                        │
    │  • volumes.configMap -> /etc/config                         │
    │  • volumes.secret    -> /etc/secrets (tmpfs memory)         │
    └─────────────────────────────────────────────────────────────┘
""",
        "primary_manifest": """apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: default
data:
  APP_ENV: "production"
  LOG_LEVEL: "info"
  nginx.conf: |
    events { worker_connections 1024; }
    http {
      server {
        listen 80;
        location / { return 200 "OK"; }
      }
    }
---
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
  namespace: default
type: Opaque
stringData:
  DB_PASSWORD: "super-secure-production-password"
  API_KEY: "secret-token-xyz-123"
""",
        "fields": [
            (
                "`data` vs `stringData`",
                "Map",
                "`data` expects base64 encoded strings; `stringData` accepts raw text and is auto-encoded on write.",
            ),
            (
                "`immutable: true`",
                "Boolean",
                "Protects against accidental config modification and reduces kube-apiserver watch load.",
            ),
            (
                "`envFrom.configMapRef`",
                "Object",
                "Exposes all key-value pairs in a ConfigMap as individual container environment variables.",
            ),
        ],
        "patterns": [
            (
                "Projected Volume Config Injection",
                """apiVersion: v1
kind: Pod
metadata:
  name: projected-config-pod
spec:
  containers:
  - name: app
    image: alpine:3.20
    command: ["sh", "-c", "ls -la /etc/config && sleep 3600"]
    volumeMounts:
    - name: config-bundle
      mountPath: /etc/config
      readOnly: true
  volumes:
  - name: config-bundle
    projected:
      sources:
      - configMap:
          name: app-config
      - secret:
          name: app-secrets
""",
            ),
            (
                "Immutable Configuration Pattern",
                """apiVersion: v1
kind: ConfigMap
metadata:
  name: static-routing-table-v1
immutable: true
data:
  routes.json: |
    {"/api/v1": "http://api-v1", "/api/v2": "http://api-v2"}
""",
            ),
        ],
        "hardening": [
            "Store sensitive data exclusively in `Secret` resources backed by KMS envelope encryption or external vault integrations (External Secrets Operator).",
            "Set `immutable: true` on ConfigMaps and Secrets used with immutable deployment pipelines to eliminate drift.",
            "Always mount Secret volumes with `readOnly: true` to prevent unauthorized in-pod file manipulation.",
        ],
        "troubleshooting": [
            (
                "`CreateContainerConfigError`",
                "Referenced ConfigMap or Secret does not exist or key name is misspelled.",
                "1. Run `kubectl describe pod <name>` and inspect the exact missing key.\n2. Check namespace: `kubectl get configmap,secret -n <namespace>`.",
            ),
            (
                "Live ConfigMap Update Not Reflected in Pod",
                "ConfigMaps injected as environment variables are static and require pod restart; volume mounts take up to kubelet sync period (default ~60s).",
                "1. Trigger rolling restart: `kubectl rollout restart deployment/<name>`.",
            ),
        ],
    },
    4: {
        "slug": "04-storage",
        "api_groups": "`v1`, `storage.k8s.io/v1` &bull; `PersistentVolume`, `PersistentVolumeClaim`, `StorageClass`",
        "diagram": """
    ┌───────────────────────────┐
    │       StorageClass        │ ◄── Provisioner (CSI: EBS/NFS/Ceph)
    └─────────────┬─────────────┘
                  │ Dynamic Provisioning
                  ▼
    ┌───────────────────────────┐         Binding (1-to-1)       ┌───────────────────────────┐
    │     PersistentVolume      │ ◄────────────────────────────► │  PersistentVolumeClaim    │
    │  (Cluster-Scoped Storage) │                                │  (Namespace-Scoped Claim) │
    └───────────────────────────┘                                └─────────────┬─────────────┘
                                                                               │ Mounted into
                                                                               ▼
                                                                 ┌───────────────────────────┐
                                                                 │       Pod VolumeMount     │
                                                                 └───────────────────────────┘
""",
        "primary_manifest": """apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-nvme
provisioner: kubernetes.io/no-provisioner
volumeBindingMode: WaitForFirstConsumer
reclaimPolicy: Retain
allowVolumeExpansion: true
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
  namespace: default
spec:
  accessModes:
  - ReadWriteOnce
  storageClassName: fast-nvme
  resources:
    requests:
      storage: 20Gi
""",
        "fields": [
            (
                "`accessModes`",
                "Array",
                "`ReadWriteOnce` (single node), `ReadOnlyMany` (multi-node read), `ReadWriteMany` (multi-node write), `ReadWriteOncePod` (single pod).",
            ),
            (
                "`volumeBindingMode`",
                "Enum",
                "`Immediate` binds immediately; `WaitForFirstConsumer` delays binding until Pod scheduling to respect zone/node constraints.",
            ),
            (
                "`reclaimPolicy`",
                "Enum",
                "`Delete` cleans up underlying physical disk upon PVC deletion; `Retain` preserves data for manual recovery.",
            ),
        ],
        "patterns": [
            (
                "Dynamic PVC with StatefulSet Volume Template",
                """apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: database
spec:
  serviceName: db
  replicas: 2
  selector:
    matchLabels:
      app: db
  template:
    metadata:
      labels:
        app: db
    spec:
      containers:
      - name: postgres
        image: postgres:16-alpine
        env:
        - name: POSTGRES_PASSWORD
          value: example
        volumeMounts:
        - name: pgdata
          mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
  - metadata:
      name: pgdata
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 10Gi
""",
            ),
            (
                "Local Static PersistentVolume",
                """apiVersion: v1
kind: PersistentVolume
metadata:
  name: local-pv-storage
spec:
  capacity:
    storage: 50Gi
  accessModes:
  - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  storageClassName: local-storage
  local:
    path: /mnt/disks/ssd1
  nodeAffinity:
    required:
      nodeSelectorTerms:
      - matchExpressions:
        - key: kubernetes.io/hostname
          operator: In
          values:
          - node-worker-1
""",
            ),
        ],
        "hardening": [
            "Always use `volumeBindingMode: WaitForFirstConsumer` for cloud block storage (EBS/GPD/AzureDisk) to avoid multi-zone scheduling deadlocks.",
            "Enable `allowVolumeExpansion: true` in StorageClasses to facilitate zero-downtime disk resizing.",
            "Protect production PVCs from accidental deletion by setting `reclaimPolicy: Retain` on mission-critical StorageClasses.",
        ],
        "troubleshooting": [
            (
                "PVC Stuck in `Pending`",
                "No PV matches capacity/accessMode, or StorageClass provisioner is failing.",
                "1. Run `kubectl describe pvc <name>`\n2. Verify StorageClass existence: `kubectl get storageclass`\n3. Check CSI controller logs in `kube-system`.",
            ),
            (
                "Multi-Attach Error (`VolumeAttachment` Deadlock)",
                "Previous Pod on another node holds the read-write block lease.",
                "1. Find attaching pod: `kubectl get volumeattachments`\n2. Verify old pod termination on failing node.",
            ),
        ],
    },
    5: {
        "slug": "05-services-networking",
        "api_groups": "`v1`, `discovery.k8s.io/v1` &bull; `Service`, `EndpointSlice`",
        "diagram": """
    ┌───────────────────────────┐
    │     Client / Ingress      │
    └─────────────┬─────────────┘
                  │ DNS: `api.default.svc.cluster.local`
                  ▼
    ┌───────────────────────────┐
    │   Service (ClusterIP)     │ ◄── Virtual IP (iptables / IPVS / eBPF)
    └─────────────┬─────────────┘
                  │ EndpointSlice Controller
                  ▼
    ┌───────────────────────────┐
    │       EndpointSlice       │ ──► [ 10.244.1.12:8080 (Pod A) ]
    │   (List of Healthy IPs)   │ ──► [ 10.244.2.45:8080 (Pod B) ]
    └───────────────────────────┘
""",
        "primary_manifest": """apiVersion: v1
kind: Service
metadata:
  name: backend-service
  namespace: default
  labels:
    app: backend
spec:
  type: ClusterIP
  sessionAffinity: ClientIP
  sessionAffinityConfig:
    clientIP:
      timeoutSeconds: 10800
  selector:
    app: backend
  ports:
  - name: http
    port: 80
    targetPort: 8080
    protocol: TCP
""",
        "fields": [
            (
                "`spec.type`",
                "Enum",
                "`ClusterIP` (internal virtual IP), `NodePort` (dedicated port on all nodes), `LoadBalancer` (cloud provider VIP), `ExternalName` (CNAME redirect).",
            ),
            (
                "`spec.clusterIP: None`",
                "String",
                "Creates a Headless Service; DNS queries return raw Pod IPs directly instead of a virtual VIP.",
            ),
            (
                "`spec.ports[*].targetPort`",
                "Integer / String",
                "The destination port exposed by container processes in matching Pods.",
            ),
        ],
        "patterns": [
            (
                "Headless Service for Stateful Workloads",
                """apiVersion: v1
kind: Service
metadata:
  name: kafka-headless
spec:
  clusterIP: None
  selector:
    app: kafka
  ports:
  - name: tcp-kafka
    port: 9092
    targetPort: 9092
""",
            ),
            (
                "ExternalName Service for Cloud SaaS Integration",
                """apiVersion: v1
kind: Service
metadata:
  name: external-database
spec:
  type: ExternalName
  externalName: db.production.rds.amazonaws.com
""",
            ),
        ],
        "hardening": [
            "Use `ClusterIP` as default; avoid exposing services as `NodePort` directly to public networks.",
            "Configure readiness probes on Pods to guarantee traffic is routed only to warm, healthy endpoints.",
            "Audit `EndpointSlice` scaling for large workloads (>1,000 pods) to prevent control plane memory pressure.",
        ],
        "troubleshooting": [
            (
                "Service Has No Endpoints (`503` / Connection Refused)",
                "Service selector does not match any Pod labels, or Pod readiness probes are failing.",
                "1. Check matching endpoints: `kubectl get endpoints <service-name>`\n2. Verify Pod labels: `kubectl get pods --show-labels`\n3. Verify container port binding: `kubectl get pods -o jsonpath='{.items[*].spec.containers[*].ports}'`",
            ),
            (
                "CoreDNS Name Resolution Failure",
                "DNS lookup fails for `service.namespace.svc.cluster.local`.",
                "1. Test from inside cluster: `kubectl run curl --rm -it --image=curlimages/curl -- nslookup <service-name>`\n2. Check CoreDNS pods: `kubectl get pods -n kube-system -l k8s-app=kube-dns`.",
            ),
        ],
    },
    6: {
        "slug": "06-ingress-gateway",
        "api_groups": "`networking.k8s.io/v1` &bull; `Ingress`, `IngressClass`",
        "diagram": """
    ┌─────────────────────────────────────────────────────────────┐
    │                        Internet                             │
    └─────────────────────────────┬───────────────────────────────┘
                                  │ HTTPS (Port 443 / TLS)
                                  ▼
    ┌─────────────────────────────────────────────────────────────┐
    │          Ingress Controller (NGINX / Envoy / Traefik)       │
    └──────────────┬──────────────────────────────┬───────────────┘
                   │ /api/*                       │ /static/*
                   ▼                              ▼
    ┌─────────────────────────────┐┌──────────────────────────────┐
    │ Service: `api-service:80`   ││ Service: `static-service:80` │
    └─────────────────────────────┘└──────────────────────────────┘
""",
        "primary_manifest": """apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: production-ingress
  namespace: default
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/proxy-body-size: "10m"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - api.example.com
    secretName: api-example-tls
  rules:
  - host: api.example.com
    http:
      paths:
      - path: /v1
        pathType: Prefix
        backend:
          service:
            name: api-v1-service
            port:
              number: 80
      - path: /v2
        pathType: Prefix
        backend:
          service:
            name: api-v2-service
            port:
              number: 80
""",
        "fields": [
            (
                "`spec.ingressClassName`",
                "String",
                "Selects the Ingress controller implementation responsible for parsing this resource.",
            ),
            (
                "`spec.rules[*].http.paths[*].pathType`",
                "Enum",
                "`Prefix` (matches URI prefix), `Exact` (exact URI match), `ImplementationSpecific`.",
            ),
            (
                "`spec.tls[*].secretName`",
                "String",
                "TLS Certificate secret containing `tls.crt` and `tls.key` keys.",
            ),
        ],
        "patterns": [
            (
                "Host-Based Virtual Hosting Routing",
                """apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: multi-tenant-ingress
spec:
  ingressClassName: nginx
  rules:
  - host: app1.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: app1-service
            port:
              number: 80
  - host: app2.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: app2-service
            port:
              number: 80
""",
            ),
            (
                "Canary Traffic Splitting via Ingress Annotations",
                """apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: api-canary
  annotations:
    nginx.ingress.kubernetes.io/canary: "true"
    nginx.ingress.kubernetes.io/canary-weight: "20"
spec:
  ingressClassName: nginx
  rules:
  - host: api.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: api-canary-service
            port:
              number: 80
""",
            ),
        ],
        "hardening": [
            "Enforce TLS 1.3 and automatic HTTP-to-HTTPS redirects across all public routes.",
            "Integrate `cert-manager` for automated Let's Encrypt TLS certificate lifecycle and renewal.",
            "Implement rate-limiting and request size restrictions via Ingress controller annotations.",
        ],
        "troubleshooting": [
            (
                "Ingress `404 Not Found`",
                "Path prefix or hostname does not match Ingress rule definitions.",
                "1. Verify Ingress rules: `kubectl describe ingress <name>`\n2. Verify Ingress Controller logs: `kubectl logs -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx`",
            ),
            (
                "Ingress `502 Bad Gateway`",
                "Target backend Service or Pod is offline or failing health probes.",
                "1. Verify backend Service endpoints: `kubectl get endpoints <service-name>`",
            ),
        ],
    },
    7: {
        "slug": "07-scheduling",
        "api_groups": "`v1` &bull; `Pod`, `Node`",
        "diagram": """
    ┌───────────────────────────┐
    │      kube-scheduler       │
    └─────────────┬─────────────┘
                  │ 1. Filtering (Tolerations, NodeSelector, Affinity)
                  │ 2. Scoring (Topology Spread, Resource Packing)
                  ▼
    ┌───────────────────────────┬───────────────────────────┐
    │  Zone: us-east-1a         │  Zone: us-east-1b         │
    │  [ Node A ] [ Node B ]    │  [ Node C ] [ Node D ]    │
    └───────────────────────────┴───────────────────────────┘
""",
        "primary_manifest": """apiVersion: apps/v1
kind: Deployment
metadata:
  name: ha-workload
spec:
  replicas: 4
  selector:
    matchLabels:
      app: ha-app
  template:
    metadata:
      labels:
        app: ha-app
    spec:
      topologySpreadConstraints:
      - maxSkew: 1
        topologyKey: topology.kubernetes.io/zone
        whenUnsatisfiable: DoNotSchedule
        labelSelector:
          matchLabels:
            app: ha-app
      affinity:
        nodeAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            nodeSelectorTerms:
            - matchExpressions:
              - key: node-role.kubernetes.io/worker
                operator: Exists
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchLabels:
                  app: ha-app
              topologyKey: kubernetes.io/hostname
      tolerations:
      - key: "dedicated"
        operator: "Equal"
        value: "compute"
        effect: "NoSchedule"
      containers:
      - name: app
        image: nginx:1.27-alpine
""",
        "fields": [
            (
                "`topologySpreadConstraints`",
                "Array",
                "Distributes Pods evenly across zones/nodes to prevent single-zone outages (`maxSkew: 1`).",
            ),
            (
                "`affinity.nodeAffinity`",
                "Object",
                "Directs Pod placement onto nodes matching specific hardware/architectural labels.",
            ),
            (
                "`tolerations`",
                "Array",
                "Permits Pods to be scheduled on nodes tainted with `NoSchedule` or `NoExecute`.",
            ),
        ],
        "patterns": [
            (
                "GPU Node Taint & Toleration Placement",
                """apiVersion: v1
kind: Pod
metadata:
  name: ml-inference-task
spec:
  tolerations:
  - key: "nvidia.com/gpu"
    operator: "Exists"
    effect: "NoSchedule"
  nodeSelector:
    accelerator: nvidia-a100
  containers:
  - name: inference
    image: python:3.12-slim
    command: ["python", "-c", "print('Inference worker running...')"]
""",
            ),
            (
                "Pod Anti-Affinity for Zero Co-location",
                """apiVersion: apps/v1
kind: Deployment
metadata:
  name: singleton-per-node
spec:
  replicas: 3
  selector:
    matchLabels:
      app: singleton
  template:
    metadata:
      labels:
        app: singleton
    spec:
      affinity:
        podAntiAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
          - labelSelector:
              matchLabels:
                app: singleton
            topologyKey: kubernetes.io/hostname
      containers:
      - name: app
        image: nginx:alpine
""",
            ),
        ],
        "hardening": [
            "Use `topologySpreadConstraints` with `topologyKey: topology.kubernetes.io/zone` for multi-AZ clusters.",
            "Use `preferredDuringScheduling` when soft affinity is desired to prevent unschedulable pod deadlocks.",
            "Reserve specialized nodes (GPU, high-memory) using node taints to prevent general workloads from consuming expensive compute.",
        ],
        "troubleshooting": [
            (
                "Pod Stuck in `Pending` (`0/10 nodes available`)",
                "Tolerations, affinity rules, or resource requests cannot be satisfied.",
                "1. Inspect scheduling failures: `kubectl describe pod <name>`\n2. Review node taints: `kubectl get nodes -o custom-columns=NAME:.metadata.name,TAINTS:.spec.taints`\n3. Review node labels: `kubectl get nodes --show-labels`",
            ),
        ],
    },
    8: {
        "slug": "08-security-rbac",
        "api_groups": "`rbac.authorization.k8s.io/v1`, `v1` &bull; `Role`, `ClusterRole`, `RoleBinding`, `ServiceAccount`",
        "diagram": """
    ┌───────────────────────────┐
    │      ServiceAccount       │ ◄── Injected into Pod JWT Token
    └─────────────┬─────────────┘
                  │ Bound via RoleBinding
                  ▼
    ┌───────────────────────────┐
    │     Role / ClusterRole    │ ◄── Rules: apiGroups, resources, verbs
    └─────────────┬─────────────┘
                  │ Authorizes
                  ▼
    ┌───────────────────────────┐
    │       kube-apiserver      │ ──► [ GET /api/v1/namespaces/default/pods ] ✓
    └───────────────────────────┘
""",
        "primary_manifest": """apiVersion: v1
kind: ServiceAccount
metadata:
  name: deployment-manager
  namespace: production
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: deployment-operator
  namespace: production
rules:
- apiGroups: ["apps"]
  resources: ["deployments", "replicasets"]
  verbs: ["get", "list", "watch", "create", "update", "patch"]
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: bind-deployment-operator
  namespace: production
subjects:
- kind: ServiceAccount
  name: deployment-manager
  namespace: production
roleRef:
  kind: Role
  name: deployment-operator
  apiGroup: rbac.authorization.k8s.io
""",
        "fields": [
            (
                "`rules[*].apiGroups`",
                "Array",
                'Target API group (`""` for core v1, `"apps"`, `"networking.k8s.io"`).',
            ),
            (
                "`rules[*].resources`",
                "Array",
                "Kubernetes resource nouns (`pods`, `deployments`, `configmaps`).",
            ),
            (
                "`rules[*].verbs`",
                "Array",
                "Permitted operations (`get`, `list`, `watch`, `create`, `update`, `patch`, `delete`).",
            ),
        ],
        "patterns": [
            (
                "ClusterRole for Cross-Namespace Read-Only Audit",
                """apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: cluster-viewer
rules:
- apiGroups: ["", "apps", "batch", "networking.k8s.io"]
  resources: ["*"]
  verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: bind-cluster-viewer
subjects:
- kind: ServiceAccount
  name: auditor
  namespace: security-tools
roleRef:
  kind: ClusterRole
  name: cluster-viewer
  apiGroup: rbac.authorization.k8s.io
""",
            ),
            (
                "Pod Security Standard Restricted SecurityContext",
                """apiVersion: v1
kind: Pod
metadata:
  name: hardened-secure-pod
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 10001
    runAsGroup: 10001
    fsGroup: 10001
    seccompProfile:
      type: RuntimeDefault
  containers:
  - name: secure-app
    image: alpine:3.20
    command: ["sleep", "3600"]
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop:
        - ALL
""",
            ),
        ],
        "hardening": [
            "Follow the Principle of Least Privilege: never grant wildcard `*` permissions in production RoleBindings.",
            "Disable automatic ServiceAccount token mounting with `automountServiceAccountToken: false` on pods that do not interact with the API Server.",
            "Enforce Pod Security Standards (`pod-security.kubernetes.io/enforce: restricted`) at the Namespace level.",
        ],
        "troubleshooting": [
            (
                "API Request `403 Forbidden`",
                "ServiceAccount lacks RBAC verb or resource permission.",
                "1. Test authorization: `kubectl auth can-i create deployments --as=system:serviceaccount:production:deployment-manager -n production`\n2. Inspect RoleBinding subjects and roleRef matching.",
            ),
        ],
    },
    9: {
        "slug": "09-network-policies",
        "api_groups": "`networking.k8s.io/v1` &bull; `NetworkPolicy`",
        "diagram": """
    ┌─────────────────────────────────────────────────────────────┐
    │                     Frontend Namespace                      │
    │   [ Frontend Pod ] ──(Port 5432 TCP)───┐                    │
    └────────────────────────────────────────┼────────────────────┘
                                             │ Allowed Ingress
                                             ▼
    ┌─────────────────────────────────────────────────────────────┐
    │                     Database Namespace                      │
    │   ┌─────────────────────────────────────────────────────┐   │
    │   │           NetworkPolicy: Allow-From-Frontend        │   │
    │   │   [ PostgreSQL Pod (Port 5432) ]                    │   │
    │   │   Default Deny All Other Ingress / Egress           │   │
    │   └─────────────────────────────────────────────────────┘   │
    └─────────────────────────────────────────────────────────────┘
""",
        "primary_manifest": """apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: api-network-policy
  namespace: default
spec:
  podSelector:
    matchLabels:
      app: backend-api
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
    ports:
    - protocol: TCP
      port: 8080
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: database
    ports:
    - protocol: TCP
      port: 5432
  - to:
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: kube-system
    ports:
    - protocol: UDP
      port: 53
""",
        "fields": [
            (
                "`spec.podSelector`",
                "Object",
                "Selects target Pods governed by this policy. Empty `{}` matches all Pods in namespace.",
            ),
            (
                "`spec.policyTypes`",
                "Array",
                "`Ingress` (inbound traffic control), `Egress` (outbound traffic control).",
            ),
            (
                "`spec.ingress[*].from`",
                "Array",
                "List of allowed sources. Multiple elements in single block are OR-ed; elements in separate blocks are AND-ed.",
            ),
        ],
        "patterns": [
            (
                "Default Deny All Ingress Traffic",
                """apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-ingress
  namespace: secure-zone
spec:
  podSelector: {}
  policyTypes:
  - Ingress
""",
            ),
            (
                "Allow Egress Only to DNS and Internal CIDR",
                """apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: restrict-egress
  namespace: default
spec:
  podSelector:
    matchLabels:
      app: worker
  policyTypes:
  - Egress
  egress:
  - ports:
    - port: 53
      protocol: UDP
    - port: 53
      protocol: TCP
  - to:
    - ipBlock:
        cidr: 10.0.0.0/16
        except:
        - 10.0.100.0/24
""",
            ),
        ],
        "hardening": [
            "Start with a namespace-wide `default-deny-ingress` and `default-deny-egress` policy and explicitly allowlist required traffic flows.",
            "Always include egress rules for CoreDNS (`kube-system` UDP/TCP port 53); otherwise, name resolution inside Pods will fail.",
            "Verify that your CNI plugin (e.g. Cilium, Calico, Antrea) actively enforces NetworkPolicy resources.",
        ],
        "troubleshooting": [
            (
                "Pod Cannot Connect to Remote Service / DNS Timeout",
                "Egress policy is blocking traffic to CoreDNS or backend CIDR.",
                "1. Verify CNI policy enforcement status.\n2. Temporarily test DNS with: `kubectl exec -it <pod> -- nslookup kubernetes.default`\n3. Verify ingress/egress port and namespaceSelector definitions.",
            ),
        ],
    },
    10: {
        "slug": "10-lifecycle-probes",
        "api_groups": "`v1` &bull; `Pod`",
        "diagram": """
    Container Startup
           │
           ▼
    ┌─────────────────────────┐
    │      Startup Probe      │ ──(Fails)──► Kubelet Restarts Container
    └────────────┬────────────┘
                 │ (Passes)
                 ▼
    ┌─────────────────────────┐          ┌─────────────────────────┐
    │     Liveness Probe      │ ──Fail──►│ Kubelet Restarts Cont.  │
    └─────────────────────────┘          └─────────────────────────┘
    ┌─────────────────────────┐          ┌─────────────────────────┐
    │     Readiness Probe     │ ──Fail──►│ Remove from Endpoints   │
    └─────────────────────────┘          └─────────────────────────┘
""",
        "primary_manifest": """apiVersion: v1
kind: Pod
metadata:
  name: robust-lifecycle-service
spec:
  containers:
  - name: web-app
    image: nginx:1.27-alpine
    ports:
    - containerPort: 8080
    startupProbe:
      httpGet:
        path: /healthz
        port: 8080
      failureThreshold: 30
      periodSeconds: 2
    livenessProbe:
      httpGet:
        path: /healthz
        port: 8080
      initialDelaySeconds: 5
      periodSeconds: 10
      timeoutSeconds: 2
      failureThreshold: 3
    readinessProbe:
      httpGet:
        path: /ready
        port: 8080
      initialDelaySeconds: 2
      periodSeconds: 5
      successThreshold: 1
      failureThreshold: 2
    lifecycle:
      preStop:
        exec:
          command: ["sh", "-c", "sleep 10"]
""",
        "fields": [
            (
                "`startupProbe`",
                "Object",
                "Disables liveness/readiness checks until application initialization is complete. Ideal for slow JVM / ML warmups.",
            ),
            (
                "`livenessProbe`",
                "Object",
                "Detects deadlocks or broken states; triggers kubelet container restart upon failure.",
            ),
            (
                "`readinessProbe`",
                "Object",
                "Determines if the container can receive traffic; triggers removal from Service EndpointSlices when failing.",
            ),
            (
                "`lifecycle.preStop`",
                "Object",
                "Executes synchronously before container receives SIGTERM, allowing in-flight requests to drain.",
            ),
        ],
        "patterns": [
            (
                "TCP Socket Readiness & Exec Liveness",
                """apiVersion: v1
kind: Pod
metadata:
  name: custom-probes
spec:
  containers:
  - name: redis
    image: redis:7.2-alpine
    ports:
    - containerPort: 6379
    livenessProbe:
      exec:
        command: ["redis-cli", "ping"]
      periodSeconds: 10
    readinessProbe:
      tcpSocket:
        port: 6379
      periodSeconds: 5
""",
            ),
            (
                "gRPC Health Checking Protocol Probe",
                """apiVersion: v1
kind: Pod
metadata:
  name: grpc-service
spec:
  containers:
  - name: grpc-app
    image: grpc-server:v1
    ports:
    - containerPort: 50051
    livenessProbe:
      grpc:
        port: 50051
        service: "HealthService"
      initialDelaySeconds: 10
""",
            ),
        ],
        "hardening": [
            "Always include a `preStop` hook with a brief `sleep` (e.g. 5–10s) to give kube-proxy / iptables time to propagate endpoint removal before SIGTERM.",
            "Never point liveness probes at downstream dependencies (e.g. database); liveness should test only local container health.",
            "Use `startupProbe` with high `failureThreshold` for slow-booting applications rather than inflated `initialDelaySeconds` on liveness probes.",
        ],
        "troubleshooting": [
            (
                "Container Constantly Restarting (`Unhealthy` events)",
                "Liveness probe timeout or non-200 HTTP response code.",
                "1. Run `kubectl describe pod <name>` and inspect `Events`.\n2. Check probe response manually: `kubectl exec -it <name> -- wget -qO- http://localhost:8080/healthz`.",
            ),
            (
                "Pod Running but Service Not Serving Traffic",
                "Readiness probe is failing, causing Pod exclusion from Endpoints.",
                "1. Check endpoint membership: `kubectl get endpoints <service-name>`\n2. Check readiness status in `kubectl describe pod <name>`.",
            ),
        ],
    },
    11: {
        "slug": "11-autoscaling",
        "api_groups": "`autoscaling/v2`, `keda.sh/v1alpha1` &bull; `HorizontalPodAutoscaler`, `ScaledObject`",
        "diagram": """
    ┌───────────────────────────┐
    │    Metrics Server / KEDA  │ ◄── CPU, Memory, SQS, Kafka Lag
    └─────────────┬─────────────┘
                  │ Evaluates Target vs Current Metric
                  ▼
    ┌───────────────────────────┐
    │            HPA            │ ──► Scales Deployment Replicas (2 ──► 10)
    └─────────────┬─────────────┘
                  │
                  ▼
    ┌───────────────────────────┐
    │     Cluster Autoscaler    │ ──► Provisions Additional Cloud Nodes
    └───────────────────────────┘
""",
        "primary_manifest": """apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-hpa
  namespace: default
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api-service
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 75
  - type: Resource
    resource:
      name: memory
      target:
        type: AverageValue
        averageValue: 200Mi
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
      - type: Percent
        value: 100
        periodSeconds: 15
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
""",
        "fields": [
            (
                "`scaleTargetRef`",
                "Object",
                "Target controller to scale (`Deployment`, `ReplicaSet`, `StatefulSet`).",
            ),
            (
                "`metrics[*].type`",
                "Enum",
                "`Resource` (CPU/Memory via metrics-server), `Pods` (custom pod metrics), `External` (cloud queues/Prometheus).",
            ),
            (
                "`behavior.scaleDown.stabilizationWindowSeconds`",
                "Integer",
                "Prevents thrashing (flapping) by damping scale-down operations for specified duration.",
            ),
        ],
        "patterns": [
            (
                "KEDA Event-Driven SQS Queue Scaler",
                """apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: sqs-worker-scaler
  namespace: default
spec:
  scaleTargetRef:
    name: queue-worker
  minReplicaCount: 1
  maxReplicaCount: 20
  triggers:
  - type: aws-sqs-queue
    metadata:
      queueURL: https://sqs.us-east-1.amazonaws.com/123456789012/order-processing
      queueLength: "10"
      awsRegion: "us-east-1"
""",
            ),
            (
                "Custom Prometheus Metric HPA",
                """apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: http-requests-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: web-frontend
  minReplicas: 3
  maxReplicas: 15
  metrics:
  - type: Pods
    pods:
      metric:
        name: http_requests_per_second
      target:
        type: AverageValue
        averageValue: 1k
""",
            ),
        ],
        "hardening": [
            "All scaled containers MUST define explicit `resources.requests.cpu` and `resources.requests.memory`; HPA cannot calculate percentages without requests.",
            "Use `behavior.scaleDown.stabilizationWindowSeconds: 300` to prevent premature scale-down during bursty traffic.",
            "Avoid running HPA and VPA (Vertical Pod Autoscaler) on the same CPU/memory metrics simultaneously to prevent scaling contention.",
        ],
        "troubleshooting": [
            (
                "HPA Status `<unknown>/75%`",
                "Metrics Server is not installed or Pods lack CPU requests.",
                "1. Verify Metrics Server: `kubectl get apiservices | grep metrics`\n2. Verify Pod metrics: `kubectl top pods`\n3. Check HPA conditions: `kubectl describe hpa <name>`",
            ),
        ],
    },
    12: {
        "slug": "12-crds-and-operators",
        "api_groups": "`apiextensions.k8s.io/v1` &bull; `CustomResourceDefinition`",
        "diagram": """
    ┌───────────────────────────┐
    │ CustomResourceDefinition  │ ◄── Registers `Foo` Kind in API Server
    └─────────────┬─────────────┘
                  │ OpenAPI v3 Validation Schema
                  ▼
    ┌───────────────────────────┐         Watches & Reconciles    ┌───────────────────────────┐
    │   Custom Resource (CR)    │ ◄─────────────────────────────► │   Custom Operator Pod     │
    │   (Kind: DatabaseCluster) │                                 │   (Reconciliation Loop)   │
    └───────────────────────────┘                                 └─────────────┬─────────────┘
                                                                                │ Creates & Manages
                                                                                ▼
                                                                  ┌───────────────────────────┐
                                                                  │ Pods, PVCs, StatefulSets  │
                                                                  └───────────────────────────┘
""",
        "primary_manifest": """apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: databaseclusters.storage.example.com
spec:
  group: storage.example.com
  names:
    plural: databaseclusters
    singular: databasecluster
    kind: DatabaseCluster
    shortNames:
    - dbc
  scope: Namespaced
  versions:
  - name: v1alpha1
    served: true
    storage: true
    subresources:
      status: {}
      scale:
        specReplicasPath: .spec.replicas
        statusReplicasPath: .status.replicas
    schema:
      openAPIV3Schema:
        type: object
        required: ["spec"]
        properties:
          spec:
            type: object
            required: ["engine", "replicas"]
            properties:
              engine:
                type: string
                enum: ["postgres", "mysql", "redis"]
              replicas:
                type: integer
                minimum: 1
                maximum: 10
              storageSize:
                type: string
                pattern: "^[0-9]+(Gi|Mi)$"
          status:
            type: object
            properties:
              phase:
                type: string
              replicas:
                type: integer
""",
        "fields": [
            (
                "`spec.scope`",
                "Enum",
                "`Namespaced` (resources live in namespaces) or `Cluster` (cluster-wide).",
            ),
            (
                "`spec.versions[*].subresources.status`",
                "Object",
                "Enables `/status` subresource; separates spec updates from status updates.",
            ),
            (
                "`spec.versions[*].schema.openAPIV3Schema`",
                "Object",
                "Strict structural schema validation enforced by the API Server on write.",
            ),
        ],
        "patterns": [
            (
                "Custom Resource Instance (CR)",
                """apiVersion: storage.example.com/v1alpha1
kind: DatabaseCluster
metadata:
  name: primary-postgres
  namespace: default
spec:
  engine: postgres
  replicas: 3
  storageSize: 50Gi
""",
            ),
            (
                "CRD with Additional Printer Columns",
                """apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: backups.storage.example.com
spec:
  group: storage.example.com
  names:
    kind: Backup
    plural: backups
  scope: Namespaced
  versions:
  - name: v1
    served: true
    storage: true
    additionalPrinterColumns:
    - name: Status
      type: string
      jsonPath: .status.phase
    - name: Age
      type: date
      jsonPath: .metadata.creationTimestamp
    schema:
      openAPIV3Schema:
        type: object
        properties:
          spec:
            type: object
""",
            ),
        ],
        "hardening": [
            "Always include complete OpenAPI v3 validation schemas with `type`, `required`, and `enum` bounds to prevent invalid state persistence.",
            "Use `/status` subresources so operator reconciliation updates do not conflict with user spec mutations.",
            "Follow Kubernetes API versioning conventions (`v1alpha1` &rarr; `v1beta1` &rarr; `v1`) and use conversion webhooks when altering stored schemas.",
        ],
        "troubleshooting": [
            (
                '`error: unable to recognize "cr.yaml": no matches for kind`',
                "CRD is not registered, or apiVersion group/version is mismatched.",
                "1. Check registered CRDs: `kubectl get crds`\n2. Verify served API versions: `kubectl get crd <name> -o yaml`.",
            ),
        ],
    },
    13: {
        "slug": "13-troubleshooting",
        "api_groups": "`v1` &bull; `Pod`, `Event`, `Node`",
        "diagram": """
    Troubleshooting Decision Flowchart
    ┌───────────────────────────┐
    │     Pod Not Working?      │
    └─────────────┬─────────────┘
                  │
      ┌───────────┴───────────┐
      ▼                       ▼
    [ Status: Pending ]     [ Status: CrashLoopBackOff ]
      │                       │
      ├─► Insufficient CPU    ├─► Check logs: `kubectl logs --previous`
      ├─► Missing PV / Secret ├─► Inspect Exit Code (137 = OOMKilled)
      └─► Node Taint Mismatch └─► Check ConfigMap / Env Vars
""",
        "primary_manifest": """apiVersion: v1
kind: Pod
metadata:
  name: diagnostic-pod
  namespace: default
spec:
  restartPolicy: OnFailure
  containers:
  - name: debug-shell
    image: busybox:1.36
    command: ["sh", "-c", "echo 'System Health Check'; env; df -h;"]
    resources:
      limits:
        memory: "64Mi"
        cpu: "100m"
""",
        "fields": [
            ("`status.phase`", "Enum", "`Pending`, `Running`, `Succeeded`, `Failed`, `Unknown`."),
            (
                "`status.containerStatuses[*].state`",
                "Object",
                "`waiting`, `running`, or `terminated` (with reason and exit code).",
            ),
            (
                "`kubectl debug`",
                "CLI Command",
                "Attaches ephemeral container to running pod for live kernel/network inspection.",
            ),
        ],
        "patterns": [
            (
                "Ephemeral Debugging Container Injection",
                """# Attach an ephemeral debug container with network tools to a running pod
# kubectl debug -it target-pod --image=nicolaka/netshoot --target=web-app
apiVersion: v1
kind: Pod
metadata:
  name: target-pod
spec:
  containers:
  - name: web-app
    image: nginx:alpine
""",
            ),
            (
                "Node Problem Diagnostic Pod",
                """apiVersion: v1
kind: Pod
metadata:
  name: node-debugger
  namespace: kube-system
spec:
  hostNetwork: true
  hostPID: true
  containers:
  - name: host-access
    image: busybox:1.36
    command: ["sh", "-c", "nsenter --target 1 --mount --uts --ipc --net --pid /bin/sh"]
    securityContext:
      privileged: true
""",
            ),
        ],
        "hardening": [
            "Restrict `kubectl debug` with ephemeral containers using RBAC to prevent unauthorized cluster privilege escalation.",
            "Export cluster events to centralized Elasticsearch/Loki sinks; etcd purges events after 1 hour by default.",
            "Use structured JSON logging in all container workloads to simplify log aggregation and alerting.",
        ],
        "troubleshooting": [
            (
                "Golden Triage Commands",
                "Standard 4-step triage sequence for any broken Kubernetes workload.",
                "```bash\n# 1. Identify failing resources\nkubectl get pods -A -o wide --sort-by=.status.startTime\n\n# 2. Inspect events & container state\nkubectl describe pod <pod-name>\n\n# 3. Read previous container crash logs\nkubectl logs <pod-name> -c <container> --previous --tail=100\n\n# 4. Check cluster-wide chronological warning events\nkubectl get events -A --field-selector type=Warning --sort-by=.metadata.creationTimestamp\n```",
            ),
        ],
    },
    14: {
        "slug": "14-gitops-argocd",
        "api_groups": "`argoproj.io/v1alpha1` &bull; `Application`, `ApplicationSet`, `Rollout`",
        "diagram": """
    ┌───────────────────────────┐
    │     Git Repository        │ ◄── Single Source of Truth (Git Commit / PR)
    └─────────────┬─────────────┘
                  │ ArgoCD Repo Server Polls / Webhook
                  ▼
    ┌───────────────────────────┐
    │  ArgoCD Application Ctrl  │ ◄── Compares Git Desired State vs Cluster Live State
    └─────────────┬─────────────┘
                  │ Auto-Sync & Self-Healing Reconciliation
                  ▼
    ┌───────────────────────────┐
    │    Kubernetes Cluster     │ ──► [ Deployments, Services, ConfigMaps ]
    └───────────────────────────┘
""",
        "primary_manifest": """apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: production-microservices
  namespace: argocd
  finalizers:
  - resources-finalizer.argocd.argoproj.io
spec:
  project: default
  source:
    repoURL: https://github.com/example-org/k8s-manifests.git
    targetRevision: main
    path: environments/production
  destination:
    server: https://kubernetes.default.svc
    namespace: production
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
    - CreateNamespace=true
    - ApplyOutOfSyncOnly=true
""",
        "fields": [
            (
                "`spec.source`",
                "Object",
                "Git repository URL, branch/tag (`targetRevision`), and directory path containing manifests/Helm/Kustomize.",
            ),
            (
                "`spec.syncPolicy.automated.prune`",
                "Boolean",
                "Deletes cluster resources when their YAML manifests are removed from Git.",
            ),
            (
                "`spec.syncPolicy.automated.selfHeal`",
                "Boolean",
                "Reverts manual out-of-band `kubectl` mutations back to Git state within seconds.",
            ),
        ],
        "patterns": [
            (
                "Argo Rollouts Canary with AnalysisTemplate",
                """apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: web-rollout
spec:
  replicas: 5
  strategy:
    canary:
      steps:
      - setWeight: 20
      - pause: {duration: 5m}
      - setWeight: 50
      - pause: {duration: 10m}
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
      - name: web
        image: nginx:1.27-alpine
""",
            ),
            (
                "ApplicationSet Matrix Generator",
                """apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: cluster-addons
  namespace: argocd
spec:
  generators:
  - list:
      elements:
      - cluster: dev-cluster
        url: https://dev-k8s.example.com
      - cluster: prod-cluster
        url: https://prod-k8s.example.com
  template:
    metadata:
      name: "{{cluster}}-addons"
    spec:
      project: default
      source:
        repoURL: https://github.com/example/addons.git
        targetRevision: HEAD
        path: "clusters/{{cluster}}"
      destination:
        server: "{{url}}"
        namespace: kube-addons
""",
            ),
        ],
        "hardening": [
            "Always enable `prune: true` and `selfHeal: true` in production GitOps pipelines to enforce true declarative reconciliation.",
            "Use `resources-finalizer.argocd.argoproj.io` to ensure all child resources are cleaned up if an Application is deleted.",
            "Protect production clusters using ArgoCD AppProjects with restricted destination namespaces and allowed source repositories.",
        ],
        "troubleshooting": [
            (
                "Application `OutOfSync` / Degraded",
                "Manifest syntax error or immutable field modification.",
                "1. Inspect sync status in ArgoCD CLI: `argocd app get <app-name>`\n2. Trigger manual sync with diff: `argocd app sync <app-name> --dry-run`\n3. Check controller logs: `kubectl logs -n argocd -l app.kubernetes.io/name=argocd-application-controller`",
            ),
        ],
    },
    15: {
        "slug": "15-service-mesh-cilium",
        "api_groups": "`cilium.io/v2` &bull; `CiliumNetworkPolicy`, `CiliumClusterwideNetworkPolicy`",
        "diagram": """
    ┌─────────────────────────────────────────────────────────────┐
    │                        Linux Kernel                         │
    │  ┌───────────────────────────────────────────────────────┐  │
    │  │                   eBPF Hook Programs                  │  │
    │  │  • L3/L4 Filtering (Fast Path Bypass iptables)        │  │
    │  │  • L7 HTTP/gRPC Inspection via Envoy                  │  │
    │  │  • Transparent WireGuard / IPsec Encryption           │  │
    │  └───────────────────────────────────────────────────────┘  │
    └─────────────────────────────┬───────────────────────────────┘
                                  │ Hubble Telemetry Stream
                                  ▼
    ┌─────────────────────────────────────────────────────────────┐
    │                 Hubble Observability UI                     │
    └─────────────────────────────────────────────────────────────┘
""",
        "primary_manifest": """apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: secure-payment-l7
  namespace: finance
spec:
  endpointSelector:
    matchLabels:
      app: payment-processor
  ingress:
  - fromEndpoints:
    - matchLabels:
        app: checkout-api
    toPorts:
    - ports:
      - port: "8080"
        protocol: TCP
      rules:
        http:
        - method: POST
          path: "/v1/charge"
  egress:
  - toFQDNs:
    - matchName: "api.stripe.com"
    toPorts:
    - ports:
      - port: "443"
        protocol: TCP
""",
        "fields": [
            (
                "`endpointSelector`",
                "Object",
                "Selects Cilium endpoints (Pods) using identity-based labels rather than volatile IP addresses.",
            ),
            (
                "`ingress[*].toPorts[*].rules.http`",
                "Array",
                "L7 application-layer policy (methods, exact URI paths, regex matching).",
            ),
            (
                "`egress[*].toFQDNs`",
                "Array",
                "DNS-aware egress security policy allowlisting specific external hostnames.",
            ),
        ],
        "patterns": [
            (
                "Clusterwide L7 Kafka Security Policy",
                """apiVersion: cilium.io/v2
kind: CiliumClusterwideNetworkPolicy
metadata:
  name: kafka-topic-isolation
spec:
  endpointSelector:
    matchLabels:
      app: kafka
  ingress:
  - fromEndpoints:
    - matchLabels:
        role: telemetry-producer
    toPorts:
    - ports:
      - port: "9092"
        protocol: TCP
      rules:
        kafka:
        - role: produce
          topic: "sensor-telemetry"
""",
            ),
            (
                "Mutual TLS (mTLS) Strict Authentication",
                """apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: enforce-mtls
  namespace: secure
spec:
  endpointSelector:
    matchLabels:
      app: vault
  ingress:
  - fromEndpoints:
    - matchLabels:
        app: client
    authentication:
      mode: required
""",
            ),
        ],
        "hardening": [
            "Use Cilium eBPF host routing (`bpf.masquerade=true`, `kube-proxy-replacement=true`) for line-rate packet processing without iptables overhead.",
            "Enforce strict egress FQDN allowlisting to protect against data exfiltration and supply chain attacks.",
            "Enable Hubble metrics and network flow logs for complete audit visibility.",
        ],
        "troubleshooting": [
            (
                "Hubble Flow Inspection",
                "Diagnose dropped packets and L7 authorization rejections in real time.",
                "```bash\n# Stream live drops in namespace\nhubble observe --namespace finance --verdict DROPPED\n\n# Trace HTTP status codes\nhubble observe --namespace finance --protocol http\n```",
            ),
        ],
    },
    16: {
        "slug": "16-policy-as-code",
        "api_groups": "`kyverno.io/v1`, `templates.gatekeeper.sh/v1` &bull; `ClusterPolicy`, `ConstraintTemplate`",
        "diagram": """
    ┌───────────────────────────┐
    │     User / CI Pipeline    │ ──(kubectl apply)──► kube-apiserver
    └───────────────────────────┘                            │
                                                             ▼ Admission Phase
    ┌─────────────────────────────────────────────────────────────┐
    │            Policy Engine (Kyverno / Gatekeeper)             │
    │  • Validate: Block privileged containers, enforce non-root  │
    │  • Mutate: Auto-inject default securityContext & labels     │
    │  • Generate: Auto-create NetworkPolicies on new Namespaces  │
    └─────────────────────────────────────────────────────────────┘
""",
        "primary_manifest": """apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: disallow-privileged-and-root
spec:
  validationFailureAction: Enforce
  background: true
  rules:
  - name: require-run-as-non-root
    match:
      any:
      - resources:
          kinds:
          - Pod
    validate:
      message: "Running as root is forbidden. Set securityContext.runAsNonRoot: true."
      pattern:
        spec:
          securityContext:
            runAsNonRoot: true
          containers:
          - securityContext:
              allowPrivilegeEscalation: false
""",
        "fields": [
            (
                "`validationFailureAction`",
                "Enum",
                "`Audit` (logs violations without blocking) or `Enforce` (rejects non-compliant API requests).",
            ),
            (
                "`background`",
                "Boolean",
                "Scans existing cluster resources periodically to report non-compliant workloads.",
            ),
            (
                "`rules[*].mutate` / `rules[*].generate`",
                "Object",
                "Automates manifest transformation and default resource creation.",
            ),
        ],
        "patterns": [
            (
                "Auto-Inject Default NetworkPolicy on Namespace Creation",
                """apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: default-network-policy
spec:
  rules:
  - name: generate-default-deny
    match:
      any:
      - resources:
          kinds:
          - Namespace
    generate:
      apiVersion: networking.k8s.io/v1
      kind: NetworkPolicy
      name: default-deny-all
      namespace: "{{request.object.metadata.name}}"
      synchronize: true
      data:
        spec:
          podSelector: {}
          policyTypes:
          - Ingress
          - Egress
""",
            ),
            (
                "Gatekeeper ConstraintTemplate (Rego)",
                """apiVersion: templates.gatekeeper.sh/v1
kind: ConstraintTemplate
metadata:
  name: k8srequiredlabels
spec:
  crd:
    spec:
      names:
        kind: K8sRequiredLabels
      validation:
        openAPIV3Schema:
          type: object
          properties:
            labels:
              type: array
              items: {type: string}
  targets:
  - target: admission.k8s.gatekeeper.sh
    rego: |
      package k8srequiredlabels
      violation[{"msg": msg}] {
        provided := {label | input.review.object.metadata.labels[label]}
        required := {label | label := input.parameters.labels[_]}
        missing := required - provided
        count(missing) > 0
        msg := sprintf("Missing required labels: %v", [missing])
      }
""",
            ),
        ],
        "hardening": [
            "Start policies in `validationFailureAction: Audit` for 2 weeks to assess existing workloads before switching to `Enforce`.",
            "Exclude critical system namespaces (`kube-system`, `kyverno`, `gatekeeper-system`) from mutating policies.",
            "Run policy validation tests in CI (e.g. `kyverno test .` or `gator test .`) before manifests reach cluster environments.",
        ],
        "troubleshooting": [
            (
                "Manifest Rejected by Policy (`Error from server: admission webhook denied`)",
                "Resource violated an enforced policy rule.",
                "1. Review the exact error message returned by `kubectl`.\n2. Check Kyverno PolicyReports: `kubectl get policyreports -A`\n3. Check Gatekeeper constraints: `kubectl get constraints`",
            ),
        ],
    },
    17: {
        "slug": "17-multitenancy-vcluster",
        "api_groups": "`v1`, `hnc.x-k8s.io/v1alpha2` &bull; `ResourceQuota`, `LimitRange`, `HierarchyConfiguration`",
        "diagram": """
    ┌─────────────────────────────────────────────────────────────┐
    │                      Host K8s Cluster                       │
    │  ┌───────────────────────────────────────────────────────┐  │
    │  │               Tenant Namespace: `team-alpha`          │  │
    │  │  ┌─────────────────────────────────────────────────┐  │  │
    │  │  │              vcluster Control Plane             │  │  │
    │  │  │   (Virtual API Server + SQLite/k3s / Syncer)    │  │  │
    │  │  └────────────────────────┬────────────────────────┘  │  │
    │  │                           │ Synced Workload Pods      │  │
    │  │                           ▼                           │  │
    │  │  [ Pod A (synced) ] [ Pod B (synced) ] [ Secret ]     │  │
    │  └───────────────────────────────────────────────────────┘  │
    └─────────────────────────────────────────────────────────────┘
""",
        "primary_manifest": """apiVersion: v1
kind: ResourceQuota
metadata:
  name: tenant-quota
  namespace: team-alpha
spec:
  hard:
    requests.cpu: "4"
    requests.memory: 8Gi
    limits.cpu: "8"
    limits.memory: 16Gi
    pods: "20"
    services.loadbalancers: "1"
---
apiVersion: v1
kind: LimitRange
metadata:
  name: tenant-limit-range
  namespace: team-alpha
spec:
  limits:
  - default:
      cpu: "500m"
      memory: "512Mi"
    defaultRequest:
      cpu: "100m"
      memory: "128Mi"
    type: Container
""",
        "fields": [
            (
                "`ResourceQuota`",
                "Hard ceiling",
                "Bounds aggregate compute resources, storage allocations, and object counts across a namespace.",
            ),
            (
                "`LimitRange`",
                "Defaults & Bounds",
                "Injects default resource requests/limits for bare pods and enforces min/max container size constraints.",
            ),
            (
                "`vcluster`",
                "Virtual Cluster",
                "Runs a lightweight, dedicated control plane inside a namespace for full multi-tenant CRD and cluster-admin isolation.",
            ),
        ],
        "patterns": [
            (
                "Hierarchical Namespaces (HNC) Tree",
                """apiVersion: hnc.x-k8s.io/v1alpha2
kind: HierarchyConfiguration
metadata:
  name: hierarchy
  namespace: team-alpha-staging
spec:
  parent: team-alpha-root
""",
            ),
            (
                "vcluster Helm Values Configuration",
                """# vcluster helm configuration for lightweight k3s tenant
syncer:
  extraArgs:
  - --sync-nodes=false
  - --sync-all-secrets=false
isolation:
  enabled: true
  podSecurityStandard: restricted
  resourceQuota:
    enabled: true
    quota:
      requests.cpu: "2"
      requests.memory: 4Gi
""",
            ),
        ],
        "hardening": [
            "Combine `ResourceQuota` with `LimitRange` in every tenant namespace to prevent unconstrained pod scheduling from saturating quotas.",
            "Use `vcluster` when tenants require custom CRDs, independent API versions, or cluster-scoped role simulations.",
            "Enforce NetworkPolicies between tenant namespaces to eliminate cross-tenant lateral movement.",
        ],
        "troubleshooting": [
            (
                "`exceeded quota: ... requested: ..., used: ..., limited: ...`",
                "Tenant namespace has exhausted its ResourceQuota ceiling.",
                "1. Inspect quota usage: `kubectl describe resourcequota -n <tenant-namespace>`\n2. Delete orphaned pods or scale down unused deployments.",
            ),
        ],
    },
    18: {
        "slug": "18-admission-webhooks",
        "api_groups": "`admissionregistration.k8s.io/v1` &bull; `MutatingWebhookConfiguration`, `ValidatingWebhookConfiguration`",
        "diagram": """
    API Request ──► [ Authentication ] ──► [ Authorization ]
                                                   │
                                                   ▼
    [ Mutating Webhooks ] ◄── Calls Webhook Service (Modifies Spec)
           │
           ▼
    [ Schema Validation ]
           │
           ▼
    [ Validating Webhooks ] ◄── Calls Webhook Service (Accept / Deny)
           │
           ▼
    [ Persist to etcd ]
""",
        "primary_manifest": """apiVersion: admissionregistration.k8s.io/v1
kind: ValidatingWebhookConfiguration
metadata:
  name: strict-image-validator
webhooks:
- name: image-validator.security.example.com
  rules:
  - apiGroups: [""]
    apiVersions: ["v1"]
    operations: ["CREATE", "UPDATE"]
    resources: ["pods"]
    scope: "Namespaced"
  clientConfig:
    service:
      name: webhook-service
      namespace: security-system
      path: "/validate-images"
      port: 443
    caBundle: "LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCg=="
  admissionReviewVersions: ["v1"]
  sideEffects: None
  timeoutSeconds: 3
  failurePolicy: Fail
""",
        "fields": [
            (
                "`failurePolicy`",
                "Enum",
                "`Fail` (rejects API request if webhook times out or crashes) or `Ignore` (allows request through upon failure).",
            ),
            (
                "`clientConfig.caBundle`",
                "Base64",
                "PEM-encoded CA certificate used by API Server to verify the webhook server TLS certificate.",
            ),
            (
                "`sideEffects: None`",
                "Enum",
                "Guarantees the webhook has no out-of-band side effects on dry-run requests.",
            ),
        ],
        "patterns": [
            (
                "Mutating Webhook for Sidecar Injection",
                """apiVersion: admissionregistration.k8s.io/v1
kind: MutatingWebhookConfiguration
metadata:
  name: sidecar-injector
webhooks:
- name: sidecar.inject.example.com
  rules:
  - apiGroups: [""]
    apiVersions: ["v1"]
    operations: ["CREATE"]
    resources: ["pods"]
  clientConfig:
    service:
      name: injector-service
      namespace: default
      path: "/mutate"
  admissionReviewVersions: ["v1"]
  sideEffects: None
  failurePolicy: Ignore
""",
            ),
            (
                "Namespace Exclusion Selector",
                """# Webhook configuration with namespaceSelector to exclude system components
apiVersion: admissionregistration.k8s.io/v1
kind: ValidatingWebhookConfiguration
metadata:
  name: app-validator
webhooks:
- name: validator.example.com
  rules:
  - apiGroups: ["apps"]
    apiVersions: ["v1"]
    operations: ["CREATE"]
    resources: ["deployments"]
  namespaceSelector:
    matchExpressions:
    - key: kubernetes.io/metadata.name
      operator: NotIn
      values: ["kube-system", "kube-public"]
  clientConfig:
    service:
      name: validator-svc
      namespace: default
      path: "/validate"
  admissionReviewVersions: ["v1"]
  sideEffects: None
""",
            ),
        ],
        "hardening": [
            "Always set `namespaceSelector` to exclude `kube-system` from webhooks to prevent circular bricking of control plane restarts.",
            "Use `timeoutSeconds: 3` (or less) to prevent slow webhooks from stalling kube-apiserver admission pipelines.",
            "Use `cert-manager` CA injector to automatically maintain `caBundle` synchronization.",
        ],
        "troubleshooting": [
            (
                "`Internal error occurred: failed calling webhook ... connection refused`",
                "Webhook server pod is dead or unreachable over TLS.",
                "1. Inspect webhook server logs: `kubectl logs -n <namespace> -l app=<webhook-name>`\n2. Temporarily switch `failurePolicy: Ignore` to restore cluster operations during emergencies.",
            ),
        ],
    },
    19: {
        "slug": "19-helm-packaging",
        "api_groups": "`helm.sh` &bull; `Chart.yaml`, `values.yaml`, `templates/*.yaml`",
        "diagram": """
    ┌───────────────────────────┐      ┌───────────────────────────┐
    │     Chart.yaml            │      │       values.yaml         │
    │  (Metadata, Dependencies) │      │  (User Config Overrides)  │
    └─────────────┬─────────────┘      └─────────────┬─────────────┘
                  │                                  │
                  ▼                                  ▼
    ┌─────────────────────────────────────────────────────────────┐
    │                Helm Template Rendering Engine               │
    │  • Evaluates Go Templates (`templates/deployment.yaml`)     │
    │  • Applies Helper Functions (`_helpers.tpl`)                │
    │  • Validates OpenAPI values schema (`values.schema.json`)   │
    └─────────────────────────────┬───────────────────────────────┘
                                  │ Fully Rendered Kubernetes Manifests
                                  ▼
    ┌─────────────────────────────────────────────────────────────┐
    │                      Kubernetes Cluster                     │
    └─────────────────────────────────────────────────────────────┘
""",
        "primary_manifest": """# Chart.yaml
apiVersion: v2
name: enterprise-web-app
description: Production-grade Helm chart for microservice web workloads
type: application
version: 1.4.0
appVersion: "2.18.0"
maintainers:
- name: SRE Platform Team
  email: platform@example.com
dependencies:
- name: redis
  version: 18.0.0
  repository: https://charts.bitnami.com/bitnami
  condition: redis.enabled
""",
        "fields": [
            (
                "`apiVersion: v2`",
                "String",
                "Standard for Helm 3 charts; supports declarative chart dependencies.",
            ),
            (
                "`version` vs `appVersion`",
                "SemVer",
                "`version` is the chart version; `appVersion` reflects the packaged application version.",
            ),
            (
                "`dependencies`",
                "Array",
                "Subcharts managed and bundled via `helm dependency update`.",
            ),
        ],
        "patterns": [
            (
                "Production values.yaml Structure",
                """# values.yaml
replicaCount: 3

image:
  repository: nginx
  tag: 1.27-alpine
  pullPolicy: IfNotPresent

service:
  type: ClusterIP
  port: 80

resources:
  limits:
    cpu: 250m
    memory: 256Mi
  requests:
    cpu: 100m
    memory: 128Mi

redis:
  enabled: true
  auth:
    enabled: true
""",
            ),
            (
                "Rendered Helm Template Deployment Manifest",
                """apiVersion: apps/v1
kind: Deployment
metadata:
  name: release-enterprise-web-app
  labels:
    helm.sh/chart: enterprise-web-app-1.4.0
    app.kubernetes.io/name: enterprise-web-app
    app.kubernetes.io/instance: release
spec:
  replicas: 3
  selector:
    matchLabels:
      app.kubernetes.io/name: enterprise-web-app
  template:
    metadata:
      labels:
        app.kubernetes.io/name: enterprise-web-app
    spec:
      containers:
      - name: web
        image: nginx:1.27-alpine
        ports:
        - containerPort: 80
""",
            ),
        ],
        "hardening": [
            "Create a strict `values.schema.json` to catch invalid data types during `helm lint` and CI.",
            "Always quote string variables in templates (e.g. `{{ .Values.tag | quote }}`) to avoid YAML type coercion issues.",
            "Use `helm template --debug` and `helm lint` in pull request workflows to validate charts before publishing.",
        ],
        "troubleshooting": [
            (
                "Helm Template Rendering Error (`nil pointer evaluating interface`)",
                "Referenced value key does not exist in `values.yaml`.",
                "1. Run template debug: `helm template my-release ./my-chart --debug`\n2. Use `default` or `required` filters to handle optional fields safely.",
            ),
        ],
    },
    20: {
        "slug": "20-kustomize-overlays",
        "api_groups": "`kustomize.config.k8s.io/v1beta1` &bull; `Kustomization`",
        "diagram": """
    ┌───────────────────────────┐
    │     Base Configuration    │ ◄── Common Deployment, Service, Config
    │    (`base/kustomization`) │
    └─────────────┬─────────────┘
                  │ Inherited by Environments
          ┌───────┴───────┐
          ▼               ▼
    ┌───────────┐   ┌───────────┐
    │  Dev      │   │  Prod     │ ◄── Strategic Merge Patches,
    │  Overlay  │   │  Overlay  │     Replica Count, Name Prefixes
    └───────────┘   └───────────┘
""",
        "primary_manifest": """apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
namespace: production
namePrefix: prod-
commonLabels:
  environment: production
  managed-by: kustomize
resources:
- ../../base
patches:
- target:
    kind: Deployment
    name: web-app
  patch: |-
    - op: replace
      path: /spec/replicas
      value: 10
configMapGenerator:
- name: app-env
  behavior: merge
  literals:
  - LOG_LEVEL=warn
  - CACHE_TTL=3600
""",
        "fields": [
            (
                "`resources`",
                "Array",
                "Relative paths to bases, other overlays, or remote Git URLs.",
            ),
            (
                "`patches`",
                "Array",
                "Targeted JSON 6902 patches or Strategic Merge Patches modifying specific fields without duplicating manifests.",
            ),
            (
                "`configMapGenerator`",
                "Array",
                "Generates ConfigMaps with automatic content-hash suffixes for zero-downtime rolling updates.",
            ),
        ],
        "patterns": [
            (
                "Base Kustomization Definition",
                """apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
- deployment.yaml
- service.yaml
""",
            ),
            (
                "Strategic Merge Patch for Resource Limits",
                """apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
spec:
  template:
    spec:
      containers:
      - name: app
        resources:
          limits:
            cpu: "2"
            memory: "4Gi"
""",
            ),
        ],
        "hardening": [
            "Use `configMapGenerator` with hash suffixes so configuration updates trigger automated rolling restarts.",
            "Keep `base/` minimal and purely structural; push environment-specific configurations into `overlays/`.",
            "Validate Kustomize builds in CI with `kubectl kustomize overlays/production --dry-run=client`.",
        ],
        "troubleshooting": [
            (
                "`patch target not found`",
                "Patch target `kind` or `name` does not match any resource generated in the base.",
                "1. Review base build output: `kubectl kustomize base`\n2. Verify `namePrefix` or `nameSuffix` has not modified the target name prior to patching.",
            ),
        ],
    },
    21: {
        "slug": "21-gateway-api",
        "api_groups": "`gateway.networking.k8s.io/v1` &bull; `GatewayClass`, `Gateway`, `HTTPRoute`, `ReferenceGrant`",
        "diagram": """
    ┌───────────────────────────┐
    │     Cluster Operator      │ ──► Manages GatewayClass & Gateway (Infrastructure)
    └─────────────┬─────────────┘
                  │
                  ▼
    ┌───────────────────────────┐
    │          Gateway          │ ◄── Listens on Port 80/443 (Shared VIP)
    └─────────────┬─────────────┘
                  │ Attaches Routes (Role-Oriented)
                  ▼
    ┌───────────────────────────┐
    │  Application Developer    │ ──► Manages HTTPRoute (80% / 20% Traffic Split)
    │  (HTTPRoute / GRPCRoute)  │
    └─────────────┬─────────────┘
                  │ Routes Traffic to Services
          ┌───────┴───────┐
          ▼               ▼
    ┌───────────┐   ┌───────────┐
    │ Service A │   │ Service B │
    │   (80%)   │   │   (20%)   │
    └───────────┘   └───────────┘
""",
        "primary_manifest": """apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: external-gateway
  namespace: infra
spec:
  gatewayClassName: envoy-gateway
  listeners:
  - name: https
    protocol: HTTPS
    port: 443
    tls:
      mode: Terminate
      certificateRefs:
      - name: tls-cert-example
    allowedRoutes:
      namespaces:
        from: All
---
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: api-traffic-split
  namespace: apps
spec:
  parentRefs:
  - name: external-gateway
    namespace: infra
  hostnames:
  - "api.example.com"
  rules:
  - matches:
    - path:
        type: PathPrefix
        value: /v2
    backendRefs:
    - name: api-v2-service
      port: 8080
      weight: 90
    - name: api-v2-canary
      port: 8080
      weight: 10
""",
        "fields": [
            (
                "`GatewayClass`",
                "Infrastructure",
                "Defines the controller implementation (e.g. Envoy Gateway, Cilium, Istio). Managed by Cluster Admins.",
            ),
            (
                "`Gateway`",
                "Entrypoint",
                "Defines network listeners, TLS termination, and allowed route namespaces.",
            ),
            (
                "`HTTPRoute.spec.rules[*].backendRefs`",
                "Array",
                "Defines weighted traffic routing, request header modifications, and url rewriting.",
            ),
        ],
        "patterns": [
            (
                "Cross-Namespace ReferenceGrant for TLS Security",
                """apiVersion: gateway.networking.k8s.io/v1beta1
kind: ReferenceGrant
metadata:
  name: allow-gateway-tls
  namespace: secrets-vault
spec:
  from:
  - group: gateway.networking.k8s.io
    kind: Gateway
    namespace: infra
  to:
  - group: ""
    kind: Secret
    name: wildcard-tls
""",
            ),
            (
                "Header-Based Canary Route",
                """apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: beta-testers-route
  namespace: apps
spec:
  parentRefs:
  - name: external-gateway
    namespace: infra
  rules:
  - matches:
    - headers:
      - name: X-Beta-Tester
        value: "true"
    backendRefs:
    - name: api-beta-svc
      port: 8080
""",
            ),
        ],
        "hardening": [
            "Use `allowedRoutes.namespaces` to restrict which namespaces can attach routes to shared Gateway listeners.",
            "Enforce `ReferenceGrant` when routes or gateways bind to resources in external namespaces.",
            "Standardize on Gateway API as the next-generation successor to Kubernetes Ingress.",
        ],
        "troubleshooting": [
            (
                "HTTPRoute `Not Admitted` / `ResolvedRefs=False`",
                "Parent Gateway not found or ReferenceGrant missing.",
                "1. Check HTTPRoute status: `kubectl describe httproute <name> -n <namespace>`\n2. Verify Gateway listener conditions: `kubectl describe gateway <name> -n <namespace>`.",
            ),
        ],
    },
    22: {
        "slug": "22-crossplane-iac",
        "api_groups": "`apiextensions.crossplane.io/v1`, `pkg.crossplane.io/v1` &bull; `CompositeResourceDefinition`, `Composition`",
        "diagram": """
    ┌───────────────────────────┐
    │     Application Dev       │ ──► Declares Composite Resource Claim (XRC)
    └─────────────┬─────────────┘
                  │
                  ▼
    ┌───────────────────────────┐
    │        Composition        │ ◄── Platform Team Blueprint
    └─────────────┬─────────────┘
                  │ Composes Managed Resources (MR)
          ┌───────┴───────┐
          ▼               ▼
    ┌───────────┐   ┌───────────┐
    │  AWS RDS  │   │  AWS S3   │ ◄── External Cloud Providers
    │  Instance │   │  Bucket   │
    └───────────┘   └───────────┘
""",
        "primary_manifest": """apiVersion: apiextensions.crossplane.io/v1
kind: CompositeResourceDefinition
metadata:
  name: xpostgresqlinstances.database.example.org
spec:
  group: database.example.org
  names:
    kind: XPostgreSQLInstance
    plural: xpostgresqlinstances
  claimNames:
    kind: PostgreSQLInstance
    plural: postgresqlinstances
  versions:
  - name: v1alpha1
    served: true
    referenceable: true
    schema:
      openAPIV3Schema:
        type: object
        properties:
          spec:
            type: object
            required: ["storageGB"]
            properties:
              storageGB:
                type: integer
""",
        "fields": [
            (
                "`CompositeResourceDefinition` (XRD)",
                "API Contract",
                "Defines the custom schema exposed to application developers.",
            ),
            (
                "`Composition`",
                "Infrastructure Template",
                "Binds the XRD to specific Managed Resources (e.g. AWS RDS, GCP CloudSQL).",
            ),
            (
                "`Managed Resource` (MR)",
                "Cloud Primitive",
                "Direct representation of cloud resources with continuous state reconciliation.",
            ),
        ],
        "patterns": [
            (
                "Application Developer Claim (XRC)",
                """apiVersion: database.example.org/v1alpha1
kind: PostgreSQLInstance
metadata:
  name: app-database
  namespace: default
spec:
  storageGB: 20
""",
            ),
            (
                "ProviderConfig IAM Configuration",
                """apiVersion: aws.upbound.io/v1beta1
kind: ProviderConfig
metadata:
  name: default
spec:
  credentials:
    source: IRSA
""",
            ),
        ],
        "hardening": [
            "Use IAM Roles for Service Accounts (IRSA / Workload Identity) rather than static long-lived cloud API keys.",
            "Lock Composition schemas with strict validation and automated drift detection.",
            "Protect critical databases from accidental deletion with `deletionPolicy: Orphan`.",
        ],
        "troubleshooting": [
            (
                "Managed Resource `Ready=False` / `Synced=False`",
                "Cloud provider authentication failure or parameter validation error.",
                "1. Run `kubectl describe <managed-resource> <name>`\n2. Verify ProviderConfig status: `kubectl get providerconfigs`.",
            ),
        ],
    },
    23: {
        "slug": "23-ebpf-tetragon",
        "api_groups": "`cilium.io/v1alpha1` &bull; `TracingPolicy`, `TracingPolicyNamespaced`",
        "diagram": """
    ┌─────────────────────────────────────────────────────────────┐
    │                         Linux Kernel                        │
    │  System Calls: `sys_execve`, `sys_openat`, `sys_socket`     │
    │  ┌───────────────────────────────────────────────────────┐  │
    │  │             Tetragon eBPF In-Kernel Probe             │  │
    │  │  • Real-time Process Ancestry & Namespace Tracing     │  │
    │  │  • In-Kernel Kill Action (Synchronous SIGKILL)        │  │
    │  └───────────────────────────────────────────────────────┘  │
    └─────────────────────────────┬───────────────────────────────┘
                                  │ JSON Security Event Log
                                  ▼
    ┌─────────────────────────────────────────────────────────────┐
    │                 SIEM / Alerting Pipeline                    │
    └─────────────────────────────────────────────────────────────┘
""",
        "primary_manifest": """apiVersion: cilium.io/v1alpha1
kind: TracingPolicy
metadata:
  name: block-privilege-escalation-exec
spec:
  kprobes:
  - call: "sys_execve"
    syscall: true
    args:
    - index: 0
      type: "string"
    selectors:
    - matchArgs:
      - index: 0
        operator: "Prefix"
        values:
        - "/bin/nc"
        - "/usr/bin/ncat"
        - "/bin/netcat"
      matchActions:
      - action: Sigkill
""",
        "fields": [
            ("`kprobes`", "Array", "Attaches eBPF probes to kernel symbols and system calls."),
            (
                "`selectors[*].matchArgs`",
                "Array",
                "Filters system call arguments (file paths, sockets, flags).",
            ),
            (
                "`selectors[*].matchActions`",
                "Array",
                "Action dispatched upon match (e.g. `Sigkill` terminates process immediately in kernel).",
            ),
        ],
        "patterns": [
            (
                "Detect Sensitive File Access (/etc/shadow)",
                """apiVersion: cilium.io/v1alpha1
kind: TracingPolicy
metadata:
  name: detect-shadow-file-access
spec:
  kprobes:
  - call: "fd_install"
    syscall: false
    args:
    - index: 1
      type: "file"
    selectors:
    - matchArgs:
      - index: 1
        operator: "Prefix"
        values:
        - "/etc/shadow"
      matchActions:
      - action: Post
""",
            ),
            (
                "Namespaced Tracing Policy for Production Workloads",
                """apiVersion: cilium.io/v1alpha1
kind: TracingPolicyNamespaced
metadata:
  name: restrict-shell-in-pod
  namespace: payment-apps
spec:
  kprobes:
  - call: "sys_execve"
    syscall: true
    args:
    - index: 0
      type: "string"
    selectors:
    - matchArgs:
      - index: 0
        operator: "Prefix"
        values: ["/bin/sh", "/bin/bash"]
      matchActions:
      - action: Sigkill
""",
            ),
        ],
        "hardening": [
            "Use `Sigkill` actions on reverse shell binaries (`nc`, `ncat`, `socat`) in production namespaces.",
            "Enforce Namespaced TracingPolicies so security rules follow application boundaries.",
            "Forward Tetragon JSON audit logs (`tetra getevents -o compact`) to SIEM systems for forensic audits.",
        ],
        "troubleshooting": [
            (
                "Process Terminated Unexpectedly with `SIGKILL`",
                "Workload executed a binary blocked by an active TracingPolicy.",
                "1. Inspect Tetragon logs: `kubectl logs -n kube-system -l app.kubernetes.io/name=tetragon -c tetragon --tail=100`\n2. Stream live events: `tetra getevents --namespace <namespace>`",
            ),
        ],
    },
    24: {
        "slug": "24-kuberay-ml",
        "api_groups": "`ray.io/v1` &bull; `RayCluster`, `RayJob`, `RayService`",
        "diagram": """
    ┌─────────────────────────────────────────────────────────────┐
    │                     RayCluster Topology                     │
    │  ┌───────────────────────────────────────────────────────┐  │
    │  │                  Ray Head Node Pod                    │  │
    │  │  (GCS Metadata Store, Dashboard, Global Scheduler)   │  │
    │  └──────────────────────────┬────────────────────────────┘  │
    │                             │ Distributed Tasks & Actors    │
    │              ┌──────────────┴──────────────┐                │
    │              ▼                             ▼                │
    │  ┌───────────────────────┐     ┌───────────────────────┐    │
    │  │   Ray Worker Pod 1    │     │   Ray Worker Pod 2    │    │
    │  │   (GPU Worker Group)  │     │   (CPU Worker Group)  │    │
    │  └───────────────────────┘     └───────────────────────┘    │
    └─────────────────────────────────────────────────────────────┘
""",
        "primary_manifest": """apiVersion: ray.io/v1
kind: RayCluster
metadata:
  name: distributed-training-cluster
  namespace: ml-workloads
spec:
  rayVersion: "2.35.0"
  headGroupSpec:
    rayStartParams:
      dashboard-host: "0.0.0.0"
    template:
      spec:
        containers:
        - name: ray-head
          image: rayproject/ray:2.35.0-py310
          resources:
            limits:
              cpu: "2"
              memory: "8Gi"
            requests:
              cpu: "1"
              memory: "4Gi"
  workerGroupSpecs:
  - groupName: gpu-workers
    replicas: 2
    minReplicas: 1
    maxReplicas: 8
    rayStartParams: {}
    template:
      spec:
        containers:
        - name: ray-worker
          image: rayproject/ray:2.35.0-py310-gpu
          resources:
            limits:
              cpu: "4"
              memory: "16Gi"
            requests:
              cpu: "2"
              memory: "8Gi"
""",
        "fields": [
            (
                "`headGroupSpec`",
                "Object",
                "Configuration for Ray Head node (Global Control Store, scheduler, web dashboard).",
            ),
            (
                "`workerGroupSpecs`",
                "Array",
                "Heterogeneous worker pools (CPU, GPU, high-memory) with independent autoscaling bounds.",
            ),
            (
                "`RayJob` / `RayService`",
                "CRD",
                "`RayJob` submits batch training tasks to completion; `RayService` provides zero-downtime serving with Ray Serve.",
            ),
        ],
        "patterns": [
            (
                "RayJob Batch Submission Spec",
                """apiVersion: ray.io/v1
kind: RayJob
metadata:
  name: llm-finetuning-job
  namespace: ml-workloads
spec:
  entrypoint: "python train.py --epochs 10"
  shutdownAfterJobFinishes: true
  rayClusterSpec:
    rayVersion: "2.35.0"
    headGroupSpec:
      template:
        spec:
          containers:
          - name: ray-head
            image: rayproject/ray:2.35.0
""",
            ),
            (
                "RayService for Multi-Model Inference",
                """apiVersion: ray.io/v1
kind: RayService
metadata:
  name: embedding-service
  namespace: ml-workloads
spec:
  serviceUnhealthyThreshold: 300
  rayClusterConfig:
    rayVersion: "2.35.0"
    headGroupSpec:
      template:
        spec:
          containers:
          - name: ray-head
            image: rayproject/ray:2.35.0
""",
            ),
        ],
        "hardening": [
            "Use `shutdownAfterJobFinishes: true` on `RayJob` resources to release expensive cloud GPU instances immediately after training.",
            "Deploy Ray clusters in isolated namespaces paired with ResourceQuotas.",
            "Expose the Ray Dashboard (port 8265) through secure Ingress with OAuth/OIDC authentication.",
        ],
        "troubleshooting": [
            (
                "Ray Worker Nodes Not Joining Cluster",
                "GCS connection failure or mismatched `rayVersion`.",
                "1. Inspect Head logs: `kubectl logs <head-pod-name> -c ray-head`\n2. Inspect Worker logs: `kubectl logs <worker-pod-name> -c ray-worker`",
            ),
        ],
    },
    25: {
        "slug": "25-batch-kueue-volcano",
        "api_groups": "`kueue.x-k8s.io/v1beta1`, `scheduling.volcano.sh/v1beta1` &bull; `ClusterQueue`, `LocalQueue`, `PodGroup`",
        "diagram": """
    ┌───────────────────────────┐
    │   User Submitted Jobs     │ ──► [ LocalQueue (Namespace A) ]
    └───────────────────────────┘                     │
                                                      ▼
    ┌─────────────────────────────────────────────────────────────┐
    │                      ClusterQueue                           │
    │  • Cohort Borrowing (Shares idle capacity between teams)    │
    │  • Preemption & Fair-Share Scheduling                       │
    └─────────────────────────────┬───────────────────────────────┘
                                  │ Admits Workload
                                  ▼
    ┌─────────────────────────────────────────────────────────────┐
    │          Gang Scheduling (Volcano / Coscheduling)           │
    │          [ All N Pods Scheduled Simultaneously or None ]   │
    └─────────────────────────────────────────────────────────────┘
""",
        "primary_manifest": """apiVersion: kueue.x-k8s.io/v1beta1
kind: ClusterQueue
metadata:
  name: research-cluster-queue
spec:
  namespaceSelector: {}
  cohort: engineering-cohort
  resourceGroups:
  - coveredResources: ["cpu", "memory", "nvidia.com/gpu"]
    flavors:
    - name: standard-flavor
      resources:
      - name: "cpu"
        nominalQuota: "32"
        borrowingLimit: "16"
      - name: "memory"
        nominalQuota: 128Gi
      - name: "nvidia.com/gpu"
        nominalQuota: "8"
---
apiVersion: kueue.x-k8s.io/v1beta1
kind: LocalQueue
metadata:
  name: research-team-queue
  namespace: research-ns
spec:
  clusterQueue: research-cluster-queue
""",
        "fields": [
            (
                "`ClusterQueue`",
                "Cluster Resource",
                "Pools cluster-wide compute resources and establishes quotas, borrowing limits, and preemption policies.",
            ),
            (
                "`cohort`",
                "String",
                "Enables capacity sharing: queues in the same cohort can borrow unused quota from sister queues.",
            ),
            (
                "`LocalQueue`",
                "Namespace Resource",
                "Submission queue in a specific namespace pointing to an upstream ClusterQueue.",
            ),
        ],
        "patterns": [
            (
                "Volcano Gang Scheduling PodGroup",
                """apiVersion: scheduling.volcano.sh/v1beta1
kind: PodGroup
metadata:
  name: distributed-training-pg
  namespace: default
spec:
  minMember: 4
  minResources:
    cpu: "8"
    memory: "32Gi"
""",
            ),
            (
                "Kueue-Managed Batch Job Submission",
                """apiVersion: batch/v1
kind: Job
metadata:
  name: sample-batch-analysis
  namespace: research-ns
  labels:
    kueue.x-k8s.io/queue-name: research-team-queue
spec:
  parallelism: 4
  completions: 4
  template:
    spec:
      restartPolicy: Never
      containers:
      - name: worker
        image: python:3.12-slim
        command: ["python", "-c", "print('Batch step complete')"]
""",
            ),
        ],
        "hardening": [
            "Use Gang Scheduling (`minMember`) for distributed PyTorch/JAX training to avoid deadlock where half the workers occupy GPUs waiting forever for missing peers.",
            "Establish `borrowingLimit` bounds to prevent a single team from monopolizing cohort resources.",
            "Enable preemption rules to allow high-priority production jobs to reclaim borrowed capacity.",
        ],
        "troubleshooting": [
            (
                "Job Inactive / Workload Not Admitted by Kueue",
                "ClusterQueue nominal quota and borrowing limits are exhausted.",
                "1. Inspect Kueue Workload: `kubectl get workloads -n <namespace>`\n2. Check ClusterQueue status: `kubectl describe clusterqueue <name>`",
            ),
        ],
    },
    26: {
        "slug": "26-hardware-acceleration-dra",
        "api_groups": "`resource.k8s.io/v1alpha3` &bull; `ResourceClaim`, `ResourceClaimTemplate`, `DeviceClass`",
        "diagram": """
    ┌───────────────────────────┐
    │     Pod Specification     │ ──► References `ResourceClaim`
    └─────────────┬─────────────┘
                  │
                  ▼
    ┌───────────────────────────┐
    │       ResourceClaim       │ ◄── Requests Specific Device Attributes
    │  (DRA: GPU, TPU, FPGA)    │     (e.g., 20GB VRAM, NVLink Mesh)
    └─────────────┬─────────────┘
                  │ Dynamic Driver Allocation
                  ▼
    ┌───────────────────────────┐
    │   DRA Node Driver Plugin  │ ──► Configures Hardware & Binds to Container
    └───────────────────────────┘
""",
        "primary_manifest": """apiVersion: resource.k8s.io/v1alpha3
kind: ResourceClaim
metadata:
  name: gpu-claim
  namespace: default
spec:
  devices:
    requests:
    - name: high-mem-gpu
      deviceClassName: gpu.nvidia.com
      selectors:
      - cel:
          expression: "device.attributes['gpu.nvidia.com'].memory >= 24 * 1024 * 1024 * 1024"
---
apiVersion: v1
kind: Pod
metadata:
  name: dra-accelerated-inference
  namespace: default
spec:
  resourceClaims:
  - name: gpu-resource
    resourceClaimName: gpu-claim
  containers:
  - name: inference-engine
    image: nvidia/cuda:12.4.1-runtime-ubuntu22.04
    command: ["nvidia-smi"]
    resources:
      claims:
      - name: gpu-resource
""",
        "fields": [
            (
                "`DeviceClass`",
                "Cluster Resource",
                "Defines the hardware class and selecting driver (e.g. `gpu.nvidia.com`, `dra.intel.com`).",
            ),
            (
                "`ResourceClaim`",
                "Claim Resource",
                "Requests fine-grained device properties (memory, architecture, interconnects) using CEL expressions.",
            ),
            (
                "`spec.resourceClaims`",
                "Pod Spec",
                "Binds claims to container instances dynamically during scheduling.",
            ),
        ],
        "patterns": [
            (
                "NVIDIA Multi-Instance GPU (MIG) Partitioning",
                """apiVersion: v1
kind: Pod
metadata:
  name: mig-partitioned-pod
spec:
  containers:
  - name: cuda-task
    image: nvidia/cuda:12.4.1-base-ubuntu22.04
    resources:
      limits:
        nvidia.com/mig-1g.10gb: 1
""",
            ),
            (
                "ResourceClaimTemplate with Stateful Deployment",
                """apiVersion: resource.k8s.io/v1alpha3
kind: ResourceClaimTemplate
metadata:
  name: per-pod-gpu-template
spec:
  spec:
    devices:
      requests:
      - name: dedicated-gpu
        deviceClassName: gpu.nvidia.com
""",
            ),
        ],
        "hardening": [
            "Use Dynamic Resource Allocation (DRA) for complex hardware constraints rather than static integer extended resources (`nvidia.com/gpu: 1`).",
            "Leverage NVIDIA MIG to slice large A100/H100 GPUs into isolated compute instances for lightweight inference tasks.",
            "Enforce resource limits on GPU-enabled namespaces using dedicated quotas.",
        ],
        "troubleshooting": [
            (
                "`Failed to allocate device for claim`",
                "No node in cluster has a hardware device satisfying the CEL selector expression.",
                "1. Inspect claim state: `kubectl describe resourceclaim <name>`\n2. Check DRA driver plugin daemonset: `kubectl get pods -n kube-system -l app=nvidia-dra-driver-kubelet-plugin`",
            ),
        ],
    },
}

for chapter in manifest.chapters:
    data = CHAPTER_DATA.get(chapter.number)
    if not data:
        continue

    slug = data["slug"]
    guide_path = GUIDES_DIR / f"{slug}.md"

    # Build bidirectional practice table
    practice_rows = []
    for ex in chapter.exercises:
        practice_rows.append(
            f"| **`{ex.name}`** | {ex.title} | [`../playground/index.html?exercise={ex.name}`](../playground/index.html?exercise={ex.name}) | [**⚡ Solve in Playground →**](../playground/index.html?exercise={ex.name}){{ .md-button .md-button--primary }} |"
        )
    practice_table = "\n".join(practice_rows)

    # Build fields table
    fields_rows = []
    for field_name, f_type, desc in data["fields"]:
        fields_rows.append(f"| {field_name} | `{f_type}` | {desc} |")
    fields_table = "\n".join(fields_rows)

    # Build patterns markdown
    patterns_md_list = []
    for pattern_title, pattern_yaml in data["patterns"]:
        patterns_md_list.append(f"""### {pattern_title}

```yaml
{pattern_yaml.strip()}
```
""")
    patterns_md = "\n".join(patterns_md_list)

    # Build hardening markdown
    hardening_list = "\n".join([f"- {h}" for h in data["hardening"]])

    # Build troubleshooting markdown
    troubleshoot_md_list = []
    for failure_title, failure_cause, triage_steps in data["troubleshooting"]:
        troubleshoot_md_list.append(f"""??? failure "{failure_title}"
    **Root Cause:** {failure_cause}

    **Diagnostic Triage Sequence:**
    {triage_steps}
""")
    troubleshoot_md = "\n".join(troubleshoot_md_list)

    md_content = f"""# Chapter {chapter.number:02d}: {chapter.title}

<div class="grid cards" markdown>

-   :material-school: **Topic Focus** &bull; {chapter.description}
-   :material-api: **Primary APIs** &bull; {data["api_groups"]}
-   :material-rocket-launch: [**Launch Playground in Wasm →**](../playground/index.html?chapter={chapter.number}){{ .md-button .md-button--primary }}

</div>

---

## 1. Architectural Overview & Control Plane Mechanics

In Kubernetes, **{chapter.title}** is reconciled through declarative state loops managed by the control plane:

```text
{textwrap.dedent(data["diagram"]).strip()}
```

When resources in this chapter are submitted, the `kube-apiserver` validates the OpenAPI v3 schema, stores state in `etcd`, and triggers the responsible controllers or node daemons to reconcile actual cluster state.

---

## 2. Annotated Production YAML Anatomy & Field Reference

Below is a production-grade declarative manifest demonstrating field definitions and operational patterns:

```yaml
{data["primary_manifest"].strip()}
```

### Key Field Schema Reference

| Field | Type | Description |
| :--- | :--- | :--- |
{fields_table}

---

## 3. Real-World Architectural Patterns

{patterns_md}

---

## 4. Production Hardening & Operational Governance

{hardening_list}

---

## 5. Failure Modes & Diagnostic Triage Tree

{troubleshoot_md}

---

## 6. Interactive Practice Matrix

Practice concepts from this chapter directly in the interactive WebAssembly sandbox:

| Exercise ID | Challenge Description | Direct Link | Action |
| :--- | :--- | :--- | :--- |
{practice_table}
"""

    guide_path.write_text(md_content, encoding="utf-8")
    print(f"Generated {guide_path}")

print("All 26 reference guides successfully generated!")

# Generate bidirectional curriculum syllabus
syllabus_lines = [
    "# Curriculum Syllabus",
    "",
    "Kubelings features **26 chapters** covering **114 real-world exercises** with bidirectional reference guides and WebAssembly playground integration:",
    "",
    "---",
    "",
]

for chapter in manifest.chapters:
    data = CHAPTER_DATA.get(chapter.number)
    slug = data["slug"] if data else f"{chapter.number:02d}-{chapter.name}"
    syllabus_lines.append(f"### [Chapter {chapter.number:02d}: {chapter.title}](guides/{slug}.md)")
    for ex in chapter.exercises:
        syllabus_lines.append(
            f"- [**`{ex.name}`**](playground/index.html?exercise={ex.name}): {ex.title}"
        )
    syllabus_lines.append("")

syllabus_path = REPO_ROOT / "docs" / "syllabus.md"
syllabus_path.write_text("\n".join(syllabus_lines), encoding="utf-8")
print(f"Generated {syllabus_path}")

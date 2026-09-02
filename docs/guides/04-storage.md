# Chapter 04: Storage & Persistent Volumes

<div class="grid cards" markdown>

-   :material-school: **Topic Focus** &bull; PVs, PVCs, Access Modes, StorageClasses, and Snapshots
-   :material-api: **Primary APIs** &bull; `v1`, `storage.k8s.io/v1` &bull; `PersistentVolume`, `PersistentVolumeClaim`, `StorageClass`
-   :material-rocket-launch: [**Launch Playground in Wasm →**](../playground/index.html?chapter=4){ .md-button .md-button--primary }

</div>

---

## 1. Architectural Overview & Control Plane Mechanics

In Kubernetes, **Storage & Persistent Volumes** is reconciled through declarative state loops managed by the control plane:

```text
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
```

When resources in this chapter are submitted, the `kube-apiserver` validates the OpenAPI v3 schema, stores state in `etcd`, and triggers the responsible controllers or node daemons to reconcile actual cluster state.

---

## 2. Annotated Production YAML Anatomy & Field Reference

Below is a production-grade declarative manifest demonstrating field definitions and operational patterns:

```yaml
apiVersion: storage.k8s.io/v1
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
```

### Key Field Schema Reference

| Field | Type | Description |
| :--- | :--- | :--- |
| `accessModes` | `Array` | `ReadWriteOnce` (single node), `ReadOnlyMany` (multi-node read), `ReadWriteMany` (multi-node write), `ReadWriteOncePod` (single pod). |
| `volumeBindingMode` | `Enum` | `Immediate` binds immediately; `WaitForFirstConsumer` delays binding until Pod scheduling to respect zone/node constraints. |
| `reclaimPolicy` | `Enum` | `Delete` cleans up underlying physical disk upon PVC deletion; `Retain` preserves data for manual recovery. |

---

## 3. Real-World Architectural Patterns

### Dynamic PVC with StatefulSet Volume Template

```yaml
apiVersion: apps/v1
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
```

### Local Static PersistentVolume

```yaml
apiVersion: v1
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
```


---

## 4. Production Hardening & Operational Governance

- Always use `volumeBindingMode: WaitForFirstConsumer` for cloud block storage (EBS/GPD/AzureDisk) to avoid multi-zone scheduling deadlocks.
- Enable `allowVolumeExpansion: true` in StorageClasses to facilitate zero-downtime disk resizing.
- Protect production PVCs from accidental deletion by setting `reclaimPolicy: Retain` on mission-critical StorageClasses.

---

## 5. Failure Modes & Diagnostic Triage Tree

??? failure "PVC Stuck in `Pending`"
    **Root Cause:** No PV matches capacity/accessMode, or StorageClass provisioner is failing.

    **Diagnostic Triage Sequence:**
    1. Run `kubectl describe pvc <name>`
    2. Verify StorageClass existence: `kubectl get storageclass`
    3. Check CSI controller logs in `kube-system`.

??? failure "Multi-Attach Error (`VolumeAttachment` Deadlock)"
    **Root Cause:** Previous Pod on another node holds the read-write block lease.

    **Diagnostic Triage Sequence:**
    1. Find attaching pod: `kubectl get volumeattachments`
    2. Verify old pod termination on failing node.


---

## 6. Interactive Practice Matrix

Practice concepts from this chapter directly in the interactive WebAssembly sandbox:

| Exercise ID | Challenge Description | Direct Link | Action |
| :--- | :--- | :--- | :--- |
| **`storage01`** | Volume Types (emptyDir & hostPath) | [`../playground/index.html?exercise=storage01`](../playground/index.html?exercise=storage01) | [**⚡ Solve in Playground →**](../playground/index.html?exercise=storage01){ .md-button .md-button--primary } |
| **`storage02`** | PersistentVolumes & PersistentVolumeClaims | [`../playground/index.html?exercise=storage02`](../playground/index.html?exercise=storage02) | [**⚡ Solve in Playground →**](../playground/index.html?exercise=storage02){ .md-button .md-button--primary } |
| **`storage03`** | Access Modes & Reclaim Policies | [`../playground/index.html?exercise=storage03`](../playground/index.html?exercise=storage03) | [**⚡ Solve in Playground →**](../playground/index.html?exercise=storage03){ .md-button .md-button--primary } |
| **`storage04`** | StorageClasses & Dynamic Provisioning | [`../playground/index.html?exercise=storage04`](../playground/index.html?exercise=storage04) | [**⚡ Solve in Playground →**](../playground/index.html?exercise=storage04){ .md-button .md-button--primary } |
| **`storage05`** | Volume Snapshots & Volume Expansion | [`../playground/index.html?exercise=storage05`](../playground/index.html?exercise=storage05) | [**⚡ Solve in Playground →**](../playground/index.html?exercise=storage05){ .md-button .md-button--primary } |

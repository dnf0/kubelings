# Chapter 04: Storage & Persistent Volumes

<div class="grid cards" markdown>

-   :material-school: **Topic Focus** &bull; PVs, PVCs, Access Modes, StorageClasses, and Snapshots
-   :material-api: **Primary APIs** &bull; `v1`, `storage.k8s.io/v1` &bull; `PersistentVolume`, `PersistentVolumeClaim`, `StorageClass`
-   :material-rocket-launch: [**Launch Playground in Wasm →**](../playground/index.html?chapter=4){ .md-button .md-button--primary }

</div>

!!! tip "⚡ Interactive Problems in this Chapter (Click to solve in Playground)"
    - [**`storage01`**: Volume Types (emptyDir & hostPath) →](../playground/index.html?exercise=storage01)
    - [**`storage02`**: PersistentVolumes & PersistentVolumeClaims →](../playground/index.html?exercise=storage02)
    - [**`storage03`**: Access Modes & Reclaim Policies →](../playground/index.html?exercise=storage03)
    - [**`storage04`**: StorageClasses & Dynamic Provisioning →](../playground/index.html?exercise=storage04)
    - [**`storage05`**: Volume Snapshots & Volume Expansion →](../playground/index.html?exercise=storage05)

---

## 1. Architectural Overview & Control Plane Mechanics

In Kubernetes, **Storage & Persistent Volumes** is reconciled through declarative state loops managed by the control plane:

```mermaid
flowchart TD
    subgraph StorageControlPlane["Dynamic CSI Provisioning Loop"]
        PVC["PersistentVolumeClaim<br/><i>(User Storage Request)</i>"]
        SC["StorageClass<br/><i>Provisioner: ebs.csi.aws.com</i>"]
        CSI_PROV["csi-provisioner<br/><i>External Controller</i>"]
        PV["PersistentVolume<br/><i>Bound (ReadWriteOnce)</i>"]
        PVC -->|References| SC
        SC -->|Triggers| CSI_PROV
        CSI_PROV -->|Provisions Block Device| PV
        PV -.->|Binds to| PVC
    end

    subgraph NodeAttachment["Worker Node Attachment & Mount"]
        KUBELET["kubelet Volume Manager"]
        CSI_NODE["CSI Node Plugin Daemon<br/><i>(Format & Mount ext4/xfs)</i>"]
        TARGET_DIR[("Target Path<br/><code>/var/lib/kubelet/pods/UID/volumes</code>")]
        CONTAINER["App Container<br/><code>/var/lib/data</code>"]
    end

    PVC -->|Scheduled Pod| KUBELET
    KUBELET -->|NodePublishVolume gRPC| CSI_NODE
    CSI_NODE -->|Mounts Block Storage| TARGET_DIR
    TARGET_DIR -->|Bind Mount| CONTAINER
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
| **`storage01`** | Volume Types (emptyDir & hostPath) | [`../playground/index.html?exercise=storage01`](../playground/index.html?exercise=storage01) | [**⚡ Solve `storage01` in Playground →**](../playground/index.html?exercise=storage01){ .md-button .md-button--primary } |
| **`storage02`** | PersistentVolumes & PersistentVolumeClaims | [`../playground/index.html?exercise=storage02`](../playground/index.html?exercise=storage02) | [**⚡ Solve `storage02` in Playground →**](../playground/index.html?exercise=storage02){ .md-button .md-button--primary } |
| **`storage03`** | Access Modes & Reclaim Policies | [`../playground/index.html?exercise=storage03`](../playground/index.html?exercise=storage03) | [**⚡ Solve `storage03` in Playground →**](../playground/index.html?exercise=storage03){ .md-button .md-button--primary } |
| **`storage04`** | StorageClasses & Dynamic Provisioning | [`../playground/index.html?exercise=storage04`](../playground/index.html?exercise=storage04) | [**⚡ Solve `storage04` in Playground →**](../playground/index.html?exercise=storage04){ .md-button .md-button--primary } |
| **`storage05`** | Volume Snapshots & Volume Expansion | [`../playground/index.html?exercise=storage05`](../playground/index.html?exercise=storage05) | [**⚡ Solve `storage05` in Playground →**](../playground/index.html?exercise=storage05){ .md-button .md-button--primary } |

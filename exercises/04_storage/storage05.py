"""
Exercise: exercises/04_storage/storage05.py
Topic: Volume Snapshots & Volume Expansion

Context & Why:
Enterprise storage architectures require disaster recovery, point-in-time backups, and capacity scaling.
The Kubernetes CSI snapshotting framework provides three standardized Custom Resource Definitions (CRDs):
1. `VolumeSnapshotClass`: Defines the CSI driver and storage lifecycle parameters (e.g. deletionPolicy).
2. `VolumeSnapshot`: A user request to capture a point-in-time block snapshot of an active PersistentVolumeClaim.
3. Restoring Snapshots: Creating a new PVC with `spec.dataSource` pointing to a VolumeSnapshot pre-populates
   the newly provisioned PV with the snapshot's block data.
In addition, Kubernetes supports volume expansion (resizing PVC storage requests upward on storage classes with
`allowVolumeExpansion: true`), but strictly forbids shrinking volumes due to filesystem corruption risks.

Instructions:
Kubernetes supports Volume Snapshots (via the CSI external-snapshotter) and
online/offline PVC Volume Expansion.

1. Configure the VolumeSnapshotClass 'csi-aws-vsc':
   - apiVersion: 'snapshot.storage.k8s.io/v1'
   - kind: 'VolumeSnapshotClass'
   - driver: 'ebs.csi.aws.com'
   - deletionPolicy: 'Delete'
2. Configure the VolumeSnapshot 'prod-db-snap-01':
   - volumeSnapshotClassName: 'csi-aws-vsc'
   - source.persistentVolumeClaimName: 'dynamic-db-pvc'
3. Configure a restored PVC 'restored-db-pvc':
   - dataSource pointing to VolumeSnapshot 'prod-db-snap-01' (apiGroup: snapshot.storage.k8s.io)
   - requests storage: '20Gi'
   - storageClassName: 'fast-ebs'
4. Implement `validate_expansion_request(initial_size_str, new_size_str, allow_expansion)`:
   - Volume expansion can only increase storage size (cannot shrink volumes).
   - If `allow_expansion` is False, return False.
   - If new size > initial size and allow_expansion is True, return True; otherwise False.
"""

import yaml

from kubelings.validator import validate_manifests

MANIFESTS = """
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshotClass
metadata:
  name: csi-aws-vsc
# TODO: Set driver to 'ebs.csi.aws.com' and deletionPolicy to 'Delete'
# WHY: Directs snapshot lifecycle management to the AWS EBS CSI driver and ensures snapshots are deleted when the object is deleted.
driver: ???
deletionPolicy: ???
---
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshot
metadata:
  name: prod-db-snap-01
spec:
  # TODO: Link volumeSnapshotClassName to 'csi-aws-vsc' and source persistentVolumeClaimName to 'dynamic-db-pvc'
  # WHY: Creates a point-in-time copy of the source PVC using the specified VolumeSnapshotClass driver.
  volumeSnapshotClassName: ???
  source:
    persistentVolumeClaimName: ???
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: restored-db-pvc
spec:
  storageClassName: fast-ebs
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 20Gi
  dataSource:
    # TODO: Set dataSource name: 'prod-db-snap-01', kind: VolumeSnapshot, and apiGroup: 'snapshot.storage.k8s.io'
    # WHY: Instructs the CSI driver to clone data from the specified snapshot into a new persistent volume.
    name: ???
    kind: VolumeSnapshot
    apiGroup: ???
"""


def _parse_storage_str(val: str) -> int:
    val = val.strip()
    if val.endswith("Gi"):
        return int(val[:-2]) * 1024 * 1024 * 1024
    if val.endswith("Mi"):
        return int(val[:-2]) * 1024 * 1024
    if val.endswith("Ki"):
        return int(val[:-2]) * 1024
    return int(val)


def validate_expansion_request(
    initial_size_str: str, new_size_str: str, allow_expansion: bool
) -> bool:
    """Determine if a PVC resize request is permissible."""
    # TODO: Implement expansion validation logic checking allow_expansion flag and strictly increasing size
    # WHY: Enforces Kubernetes storage rules that disallow volume shrinking and require StorageClass expansion opt-in.
    return False


def verify():
    manifests = list(yaml.safe_load_all(MANIFESTS))
    assert len(manifests) == 3, "Must define 3 manifests (VolumeSnapshotClass, VolumeSnapshot, PVC)"
    validate_manifests(
        manifests, expected_kinds=["VolumeSnapshotClass", "VolumeSnapshot", "PersistentVolumeClaim"]
    )

    vsc, snap, pvc = manifests[0], manifests[1], manifests[2]

    assert vsc["metadata"]["name"] == "csi-aws-vsc"
    assert vsc["driver"] == "ebs.csi.aws.com"
    assert vsc["deletionPolicy"] == "Delete"

    assert snap["metadata"]["name"] == "prod-db-snap-01"
    assert snap["spec"]["volumeSnapshotClassName"] == "csi-aws-vsc"
    assert snap["spec"]["source"]["persistentVolumeClaimName"] == "dynamic-db-pvc"

    assert pvc["metadata"]["name"] == "restored-db-pvc"
    assert pvc["spec"]["dataSource"]["name"] == "prod-db-snap-01"
    assert pvc["spec"]["dataSource"]["kind"] == "VolumeSnapshot"
    assert pvc["spec"]["dataSource"]["apiGroup"] == "snapshot.storage.k8s.io"

    # Test expansion helper
    assert validate_expansion_request("10Gi", "20Gi", allow_expansion=True) is True
    assert validate_expansion_request("10Gi", "10Gi", allow_expansion=True) is False
    assert validate_expansion_request("20Gi", "10Gi", allow_expansion=True) is False, (
        "Cannot shrink volumes"
    )
    assert validate_expansion_request("10Gi", "20Gi", allow_expansion=False) is False, (
        "Expansion disabled on StorageClass"
    )

    print("✓ storage05 passed!")


if __name__ == "__main__":
    verify()

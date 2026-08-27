"""
Exercise: exercises/04_storage/storage05.py
Topic: Volume Snapshots & Volume Expansion

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
driver: ???
deletionPolicy: ???
---
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshot
metadata:
  name: prod-db-snap-01
spec:
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
    return int(val)


def validate_expansion_request(
    initial_size_str: str, new_size_str: str, allow_expansion: bool
) -> bool:
    """Determine if a PVC resize request is permissible."""
    # TODO: Implement expansion validation
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

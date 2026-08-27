"""
Exercise: exercises/04_storage/storage03.py
Topic: Access Modes & Reclaim Policies

Instructions:
Kubernetes supports three primary PersistentVolume Access Modes:
- ReadWriteOnce (RWO): mounted as read-write by a single node.
- ReadOnlyMany (ROX): mounted read-only by many nodes.
- ReadWriteMany (RWX): mounted as read-write by many nodes.

And three Reclaim Policies:
- Retain: Manual reclamation. When PVC is deleted, PV enters 'Released' state and retains data.
- Delete: Deletes both the PersistentVolume object and the associated storage asset in external infra.
- Recycle: Performs basic scrub (`rm -rf /volume/*`) and makes PV available again (deprecated in favor of dynamic provisioning).

1. Fix the PersistentVolume manifest below:
   - name: 'shared-nfs-pv'
   - capacity storage: '50Gi'
   - accessModes: ['ReadWriteMany', 'ReadOnlyMany']
   - persistentVolumeReclaimPolicy: 'Retain'
   - storageClassName: 'nfs-storage'
   - nfs: server '10.0.0.100', path '/exports/shared'
2. Complete `evaluate_reclaim_lifecycle(reclaim_policy, pvc_deleted)`:
   - If `pvc_deleted` is False: return "BOUND".
   - If `pvc_deleted` is True:
     - "Retain" -> "RELEASED_RETAINED"
     - "Delete" -> "STORAGE_DELETED"
     - "Recycle" -> "SCRUBBED_AVAILABLE"
     - other -> raise ValueError("Unknown reclaim policy")
"""

import yaml

from kubelings.validator import validate_manifest

PV_MANIFEST = """
apiVersion: v1
kind: PersistentVolume
metadata:
  name: shared-nfs-pv
spec:
  capacity:
    storage: ???
  accessModes:
    - ???
    - ???
  persistentVolumeReclaimPolicy: ???
  storageClassName: nfs-storage
  nfs:
    server: 10.0.0.100
    path: /exports/shared
"""


def evaluate_reclaim_lifecycle(reclaim_policy: str, pvc_deleted: bool) -> str:
    """Determine the PV status outcome when its bound PVC is deleted."""
    # TODO: Implement lifecycle evaluation
    return ""


def verify():
    manifest = yaml.safe_load(PV_MANIFEST)
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(manifest, expected_kind="PersistentVolume", expected_api_version="v1")

    assert manifest["metadata"]["name"] == "shared-nfs-pv"
    assert manifest["spec"]["capacity"]["storage"] == "50Gi"
    modes = set(manifest["spec"]["accessModes"])
    assert modes == {"ReadWriteMany", "ReadOnlyMany"}, "Must support RWX and ROX access modes"
    assert manifest["spec"]["persistentVolumeReclaimPolicy"] == "Retain"
    assert manifest["spec"]["storageClassName"] == "nfs-storage"
    assert manifest["spec"]["nfs"]["server"] == "10.0.0.100"
    assert manifest["spec"]["nfs"]["path"] == "/exports/shared"

    assert evaluate_reclaim_lifecycle("Retain", pvc_deleted=False) == "BOUND"
    assert evaluate_reclaim_lifecycle("Retain", pvc_deleted=True) == "RELEASED_RETAINED"
    assert evaluate_reclaim_lifecycle("Delete", pvc_deleted=True) == "STORAGE_DELETED"
    assert evaluate_reclaim_lifecycle("Recycle", pvc_deleted=True) == "SCRUBBED_AVAILABLE"

    try:
        evaluate_reclaim_lifecycle("InvalidPolicy", pvc_deleted=True)
        raise AssertionError("Expected ValueError on invalid policy")
    except ValueError:
        pass

    print("✓ storage03 passed!")


if __name__ == "__main__":
    verify()

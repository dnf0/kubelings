"""
Exercise: solutions/04_storage/storage03.py
Topic: Access Modes & Reclaim Policies

Reference Solution
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
    storage: 50Gi
  accessModes:
    - ReadWriteMany
    - ReadOnlyMany
  persistentVolumeReclaimPolicy: Retain
  storageClassName: nfs-storage
  nfs:
    server: 10.0.0.100
    path: /exports/shared
"""


def evaluate_reclaim_lifecycle(reclaim_policy: str, pvc_deleted: bool) -> str:
    """Determine the PV status outcome when its bound PVC is deleted."""
    if not pvc_deleted:
        return "BOUND"

    if reclaim_policy == "Retain":
        return "RELEASED_RETAINED"
    elif reclaim_policy == "Delete":
        return "STORAGE_DELETED"
    elif reclaim_policy == "Recycle":
        return "SCRUBBED_AVAILABLE"
    else:
        raise ValueError(f"Unknown reclaim policy: {reclaim_policy}")


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

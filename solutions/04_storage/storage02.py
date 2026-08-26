"""
Exercise: solutions/04_storage/storage02.py
Topic: PersistentVolumes & PersistentVolumeClaims

Reference Solution
"""

from typing import Any, Dict
import yaml
from kubelings.validator import validate_manifests

MANIFESTS = """
apiVersion: v1
kind: PersistentVolume
metadata:
  name: task-pv
spec:
  capacity:
    storage: 10Gi
  accessModes:
    - ReadWriteOnce
  storageClassName: manual
  hostPath:
    path: /mnt/data
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: task-pvc
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: manual
  resources:
    requests:
      storage: 5Gi
"""


def _parse_storage_str(val: str) -> int:
    """Parse storage string like '5Gi' or '10Mi' into bytes."""
    val = val.strip()
    if val.endswith("Gi"):
        return int(val[:-2]) * 1024 * 1024 * 1024
    if val.endswith("Mi"):
        return int(val[:-2]) * 1024 * 1024
    if val.endswith("Ki"):
        return int(val[:-2]) * 1024
    return int(val)


def check_pvc_matches_pv(pv: Dict[str, Any], pvc: Dict[str, Any]) -> bool:
    """Check whether a PersistentVolume satisfies a PersistentVolumeClaim request."""
    pv_spec = pv.get("spec", {})
    pvc_spec = pvc.get("spec", {})

    # Match StorageClassName
    if pv_spec.get("storageClassName") != pvc_spec.get("storageClassName"):
        return False

    # Check capacity >= requested storage
    pv_capacity_str = pv_spec.get("capacity", {}).get("storage", "0")
    pvc_request_str = pvc_spec.get("resources", {}).get("requests", {}).get("storage", "0")
    if _parse_storage_str(pv_capacity_str) < _parse_storage_str(pvc_request_str):
        return False

    # Check accessModes (all requested modes must be supported by PV)
    pv_modes = set(pv_spec.get("accessModes", []))
    pvc_modes = set(pvc_spec.get("accessModes", []))
    if not pvc_modes.issubset(pv_modes):
        return False

    return True


def verify():
    manifests = list(yaml.safe_load_all(MANIFESTS))
    assert len(manifests) == 2, "Must contain exactly 2 manifests (PV and PVC)"
    validate_manifests(manifests, expected_kinds=["PersistentVolume", "PersistentVolumeClaim"])

    pv, pvc = manifests[0], manifests[1]

    assert pv["metadata"]["name"] == "task-pv"
    assert pv["spec"]["capacity"]["storage"] == "10Gi"
    assert pv["spec"]["accessModes"] == ["ReadWriteOnce"]
    assert pv["spec"]["storageClassName"] == "manual"
    assert pv["spec"]["hostPath"]["path"] == "/mnt/data"

    assert pvc["metadata"]["name"] == "task-pvc"
    assert pvc["spec"]["accessModes"] == ["ReadWriteOnce"]
    assert pvc["spec"]["resources"]["requests"]["storage"] == "5Gi"
    assert pvc["spec"]["storageClassName"] == "manual"

    assert check_pvc_matches_pv(pv, pvc) is True, "PV should satisfy PVC requirements"

    # Test mismatch cases
    incompatible_pvc = yaml.safe_load(yaml.dump(pvc))
    incompatible_pvc["spec"]["resources"]["requests"]["storage"] = "20Gi"
    assert check_pvc_matches_pv(pv, incompatible_pvc) is False, "PV should not satisfy 20Gi request"

    incompatible_sc = yaml.safe_load(yaml.dump(pvc))
    incompatible_sc["spec"]["storageClassName"] = "fast-ssd"
    assert check_pvc_matches_pv(pv, incompatible_sc) is False, "PV should not satisfy mismatched storageClass"

    print("✓ storage02 passed!")


if __name__ == "__main__":
    verify()

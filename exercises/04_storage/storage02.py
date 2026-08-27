"""
Exercise: exercises/04_storage/storage02.py
Topic: PersistentVolumes & PersistentVolumeClaims

Instructions:
Kubernetes decouples storage infrastructure provisioning (PersistentVolume)
from application storage requests (PersistentVolumeClaim).

1. Define a PersistentVolume 'task-pv':
   - capacity: 10Gi storage
   - accessModes: [ReadWriteOnce]
   - hostPath: path '/mnt/data'
   - storageClassName: 'manual'
2. Define a PersistentVolumeClaim 'task-pvc':
   - accessModes: [ReadWriteOnce]
   - requests storage: 5Gi
   - storageClassName: 'manual'
3. Implement `check_pvc_matches_pv(pv, pvc)`:
   - Returns True if pvc requested storage <= pv capacity, storageClassNames match,
     and all pvc accessModes are supported by pv accessModes. Otherwise, returns False.
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
    storage: ???
  accessModes:
    - ???
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
    - ???
  storageClassName: manual
  resources:
    requests:
      storage: ???
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
    # TODO: Implement matching logic
    return False


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
    incompatible_pvc["spec"]["resources"]["requests"]["storage"] == "20Gi"
    incompatible_pvc["spec"]["resources"]["requests"]["storage"] = "20Gi"
    assert check_pvc_matches_pv(pv, incompatible_pvc) is False, "PV should not satisfy 20Gi request"

    incompatible_sc = yaml.safe_load(yaml.dump(pvc))
    incompatible_sc["spec"]["storageClassName"] = "fast-ssd"
    assert check_pvc_matches_pv(pv, incompatible_sc) is False, (
        "PV should not satisfy mismatched storageClass"
    )

    print("✓ storage02 passed!")


if __name__ == "__main__":
    verify()

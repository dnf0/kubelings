"""
Exercise: solutions/04_storage/storage04.py
Topic: StorageClasses & Dynamic Provisioning

Reference Solution
"""

import yaml
from kubelings.validator import validate_manifests

MANIFESTS = """
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-ebs
provisioner: ebs.csi.aws.com
volumeBindingMode: WaitForFirstConsumer
reclaimPolicy: Delete
allowVolumeExpansion: true
parameters:
  type: gp3
  iops: "3000"
  encrypted: "true"
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: dynamic-db-pvc
spec:
  storageClassName: fast-ebs
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 20Gi
"""


def verify():
    manifests = list(yaml.safe_load_all(MANIFESTS))
    assert len(manifests) == 2, "Must define 2 manifests (StorageClass and PVC)"
    validate_manifests(manifests, expected_kinds=["StorageClass", "PersistentVolumeClaim"])

    sc, pvc = manifests[0], manifests[1]

    assert sc["metadata"]["name"] == "fast-ebs"
    assert sc["provisioner"] == "ebs.csi.aws.com"
    assert sc["volumeBindingMode"] == "WaitForFirstConsumer"
    assert sc["reclaimPolicy"] == "Delete"
    assert sc.get("allowVolumeExpansion") is True
    assert sc["parameters"]["type"] == "gp3"
    assert sc["parameters"]["iops"] == "3000"
    assert sc["parameters"]["encrypted"] == "true"

    assert pvc["metadata"]["name"] == "dynamic-db-pvc"
    assert pvc["spec"]["storageClassName"] == "fast-ebs"
    assert pvc["spec"]["accessModes"] == ["ReadWriteOnce"]
    assert pvc["spec"]["resources"]["requests"]["storage"] == "20Gi"

    print("✓ storage04 passed!")


if __name__ == "__main__":
    verify()

"""
Exercise: exercises/04_storage/storage04.py
Topic: StorageClasses & Dynamic Provisioning

Instructions:
A StorageClass enables dynamic volume provisioning without pre-allocating PVs manually.
The `volumeBindingMode: WaitForFirstConsumer` delays volume binding and provisioning until
a Pod using the PVC is created, allowing the scheduler to choose an appropriate topology/zone.

1. Configure the StorageClass 'fast-ebs':
   - apiVersion: 'storage.k8s.io/v1'
   - kind: 'StorageClass'
   - provisioner: 'ebs.csi.aws.com'
   - volumeBindingMode: 'WaitForFirstConsumer'
   - reclaimPolicy: 'Delete'
   - allowVolumeExpansion: true
   - parameters: {type: 'gp3', iops: '3000', encrypted: 'true'}
2. Configure the PersistentVolumeClaim 'dynamic-db-pvc':
   - storageClassName: 'fast-ebs'
   - accessModes: ['ReadWriteOnce']
   - requests storage: '20Gi'
"""

# I AM NOT DONE

import yaml
from kubelings.validator import validate_manifests

MANIFESTS = """
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-ebs
provisioner: ???
volumeBindingMode: ???
reclaimPolicy: ???
allowVolumeExpansion: false
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
  storageClassName: ???
  accessModes:
    - ???
  resources:
    requests:
      storage: ???
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

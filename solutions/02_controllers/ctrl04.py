"""
Exercise: solutions/02_controllers/ctrl04.py
Topic: StatefulSets & Stable Network IDs

Reference Solution
"""

from typing import List
import yaml
from kubelings.validator import validate_manifest

STATEFULSET_MANIFEST = """
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: redis-cluster
spec:
  replicas: 3
  serviceName: redis-headless
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:7.2-alpine
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes:
      - ReadWriteOnce
      resources:
        requests:
          storage: 1Gi
"""


def generate_expected_pod_and_pvc_names(manifest_dict: dict) -> List[str]:
    """Generate the expected ordinal pod names for this statefulset."""
    name = manifest_dict["metadata"]["name"]
    replicas = manifest_dict["spec"]["replicas"]
    return [f"{name}-{i}" for i in range(replicas)]


def verify():
    manifest = yaml.safe_load(STATEFULSET_MANIFEST)
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(manifest, expected_kind="StatefulSet", expected_api_version="apps/v1")

    assert manifest["metadata"]["name"] == "redis-cluster"
    assert manifest["spec"]["serviceName"] == "redis-headless", (
        "serviceName must be 'redis-headless'"
    )
    assert manifest["spec"]["replicas"] == 3, "Replicas must equal 3"

    vct = manifest["spec"].get("volumeClaimTemplates", [])
    assert len(vct) == 1, "Must define exactly 1 volumeClaimTemplate"
    assert vct[0]["metadata"]["name"] == "data"
    assert vct[0]["spec"]["accessModes"] == ["ReadWriteOnce"]
    assert vct[0]["spec"]["resources"]["requests"]["storage"] == "1Gi"

    pod_names = generate_expected_pod_and_pvc_names(manifest)
    assert pod_names == ["redis-cluster-0", "redis-cluster-1", "redis-cluster-2"]

    print("✓ ctrl04 passed!")


if __name__ == "__main__":
    verify()

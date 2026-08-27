"""
Exercise: exercises/02_controllers/ctrl04.py
Topic: StatefulSets & Stable Network IDs

Instructions:
StatefulSets provide unique ordinal identities (e.g. redis-cluster-0, redis-cluster-1)
and dedicated persistent volume claims for each replica.

Complete the StatefulSet manifest below:
1. Name: 'redis-cluster' with 3 replicas.
2. Link to headless service 'redis-headless' via `serviceName`.
3. Selector matchLabels: {app: redis}.
4. Container 'redis' with image 'redis:7.2-alpine'.
5. Define `volumeClaimTemplates` with name 'data', accessModes ['ReadWriteOnce'],
   and requests storage '1Gi'.
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
  replicas: 0
  serviceName: ???
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
  # TODO: define volumeClaimTemplates
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

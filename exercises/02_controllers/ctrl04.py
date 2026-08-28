"""
Exercise: exercises/02_controllers/ctrl04.py
Topic: StatefulSets & Stable Network IDs

Context & Why:
Stateless applications can be scaled arbitrarily with Deployments, but stateful workloads
(databases like Redis, PostgreSQL, Kafka, or Cassandra) require persistent network identities
and dedicated storage. StatefulSets meet these requirements by assigning each pod a sticky,
deterministic ordinal index (`name-0`, `name-1`). StatefulSets require a companion Headless
Service (`spec.serviceName`) to generate stable DNS records for each replica, allowing peer-to-peer
cluster consensus without virtual IP load-balancing. Furthermore, `volumeClaimTemplates`
dynamically provision dedicated PersistentVolumeClaims bound to each ordinal pod, ensuring that
if a pod is rescheduled, it automatically reattaches to its original storage volume.

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
  # TODO: Set replicas to 3
  # WHY: Establishes a 3-node stateful cluster with ordinal indices (redis-cluster-0 through redis-cluster-2).
  replicas: 0
  # TODO: Link serviceName to 'redis-headless'
  # WHY: The serviceName field binds the StatefulSet to a Headless Service, giving each ordinal pod a predictable DNS FQDN.
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
  # TODO: Define volumeClaimTemplates with name 'data', accessModes ['ReadWriteOnce'], and requests storage '1Gi'
  # WHY: volumeClaimTemplates create dedicated, stable PersistentVolumeClaims for each ordinal replica that survive pod restarts.
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

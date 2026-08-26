"""
Exercise: exercises/07_scheduling/sched03.py
Topic: Pod Affinity & Pod Anti-Affinity

Instructions:
Pod Affinity and Anti-Affinity schedule pods based on labels of *other pods*
already running on nodes within a specific topology domain (e.g. hostname or zone).

Use cases:
1. Pod Anti-Affinity: Spread replicas across different hosts/nodes for high availability.
2. Pod Affinity: Co-locate tightly-coupled microservices (e.g. web app and in-memory cache) in the same zone.

1. Complete the Pod manifest:
   - name: 'web-frontend'
   - hard anti-affinity: do NOT co-locate with another pod having label `app: web-frontend` on the same `topologyKey: kubernetes.io/hostname`.
   - soft affinity (weight 100): prefer co-locating with pods having label `app: redis-cache` in the same `topologyKey: topology.kubernetes.io/zone`.
2. Implement `can_coexist_on_host(running_pod_labels_on_node, pod_manifest)`:
   - Returns False if placing the pod on this host violates its hard podAntiAffinity rule. Otherwise True.
"""

# I AM NOT DONE

from typing import Any, Dict, List

import yaml

from kubelings.validator import validate_manifest

POD_MANIFEST = """
apiVersion: v1
kind: Pod
metadata:
  name: web-frontend
  labels:
    app: web-frontend
spec:
  affinity:
    podAntiAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
      - labelSelector:
          matchLabels:
            app: ???
        topologyKey: ???
    podAffinity:
      preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 100
        podAffinityTerm:
          labelSelector:
            matchLabels:
              app: redis-cache
          topologyKey: ???
  containers:
  - name: web
    image: nginx:alpine
"""


def can_coexist_on_host(
    running_pod_labels_on_node: List[Dict[str, str]],
    pod_manifest: Dict[str, Any],
) -> bool:
    """Check if placing the candidate pod violates host-level podAntiAffinity."""
    # TODO: Implement anti-affinity checker
    return True


def verify():
    manifest = yaml.safe_load(POD_MANIFEST)
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(manifest, expected_kind="Pod", expected_api_version="v1")

    aff = manifest["spec"]["affinity"]
    anti_terms = aff["podAntiAffinity"]["requiredDuringSchedulingIgnoredDuringExecution"]
    assert anti_terms[0]["labelSelector"]["matchLabels"]["app"] == "web-frontend"
    assert anti_terms[0]["topologyKey"] == "kubernetes.io/hostname"

    pref_terms = aff["podAffinity"]["preferredDuringSchedulingIgnoredDuringExecution"]
    assert pref_terms[0]["weight"] == 100
    assert pref_terms[0]["podAffinityTerm"]["labelSelector"]["matchLabels"]["app"] == "redis-cache"
    assert pref_terms[0]["podAffinityTerm"]["topologyKey"] == "topology.kubernetes.io/zone"

    # Test host co-existence
    node_with_web = [{"app": "web-frontend", "version": "1.0"}, {"tier": "backend"}]
    node_with_cache = [{"app": "redis-cache"}, {"tier": "backend"}]

    assert can_coexist_on_host(node_with_web, manifest) is False, (
        "Cannot co-locate on same host as another web-frontend"
    )
    assert can_coexist_on_host(node_with_cache, manifest) is True

    print("✓ sched03 passed!")


if __name__ == "__main__":
    verify()

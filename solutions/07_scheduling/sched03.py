"""
Exercise: solutions/07_scheduling/sched03.py
Topic: Pod Affinity & Pod Anti-Affinity

Reference Solution
"""

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
            app: web-frontend
        topologyKey: kubernetes.io/hostname
    podAffinity:
      preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 100
        podAffinityTerm:
          labelSelector:
            matchLabels:
              app: redis-cache
          topologyKey: topology.kubernetes.io/zone
  containers:
  - name: web
    image: nginx:alpine
"""


def can_coexist_on_host(
    running_pod_labels_on_node: List[Dict[str, str]],
    pod_manifest: Dict[str, Any],
) -> bool:
    """Check if placing the candidate pod violates host-level podAntiAffinity."""
    aff = pod_manifest.get("spec", {}).get("affinity", {})
    anti_terms = (
        aff.get("podAntiAffinity", {})
        .get("requiredDuringSchedulingIgnoredDuringExecution", [])
    )

    for term in anti_terms:
        if term.get("topologyKey") == "kubernetes.io/hostname":
            match_labels = term.get("labelSelector", {}).get("matchLabels", {})
            for pod_labels in running_pod_labels_on_node:
                if all(pod_labels.get(k) == v for k, v in match_labels.items()):
                    return False
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

    assert can_coexist_on_host(node_with_web, manifest) is False, "Cannot co-locate on same host as another web-frontend"
    assert can_coexist_on_host(node_with_cache, manifest) is True

    print("✓ sched03 passed!")


if __name__ == "__main__":
    verify()

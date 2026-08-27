"""
Exercise: exercises/07_scheduling/sched05.py
Topic: Topology Spread Constraints

Instructions:
`topologySpreadConstraints` control how Pods are spread across failure domains
(such as regions, zones, nodes, and other user-defined topology domains) to achieve
even distribution and high availability.

Fields:
- `maxSkew`: The maximum allowable difference in pod counts between any two topology domains.
- `topologyKey`: The node label key representing the domain (e.g. `topology.kubernetes.io/zone`).
- `whenUnsatisfiable`: `DoNotSchedule` (hard constraint) or `ScheduleAnyway` (soft constraint).
- `labelSelector`: Finds matching pods to count across topology domains.

1. Configure the Pod manifest:
   - name: 'payment-processor'
   - maxSkew: 1
   - topologyKey: 'topology.kubernetes.io/zone'
   - whenUnsatisfiable: 'DoNotSchedule'
   - labelSelector matchLabels: {app: 'payment-processor'}
2. Implement `is_placement_skew_acceptable(current_zone_counts, candidate_zone, max_skew)`:
   - Evaluates if adding 1 pod to `candidate_zone` keeps `max(counts) - min(counts) <= max_skew`.
"""

from typing import Dict

import yaml

from kubelings.validator import validate_manifest

POD_MANIFEST = """
apiVersion: v1
kind: Pod
metadata:
  name: payment-processor
  labels:
    app: payment-processor
spec:
  topologySpreadConstraints:
  - maxSkew: 0
    topologyKey: ???
    whenUnsatisfiable: ???
    labelSelector:
      matchLabels:
        app: ???
  containers:
  - name: processor
    image: python:3.11-slim
"""


def is_placement_skew_acceptable(
    current_zone_counts: Dict[str, int],
    candidate_zone: str,
    max_skew: int = 1,
) -> bool:
    """Calculate if placing a new pod in candidate_zone satisfies the maxSkew constraint."""
    # TODO: Implement topology skew validator
    return False


def verify():
    manifest = yaml.safe_load(POD_MANIFEST)
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(manifest, expected_kind="Pod", expected_api_version="v1")

    tsc = manifest["spec"]["topologySpreadConstraints"][0]
    assert tsc["maxSkew"] == 1
    assert tsc["topologyKey"] == "topology.kubernetes.io/zone"
    assert tsc["whenUnsatisfiable"] == "DoNotSchedule"
    assert tsc["labelSelector"]["matchLabels"]["app"] == "payment-processor"

    # Test skew calculation
    # Zone counts: zoneA=2, zoneB=2, zoneC=1 -> adding to zoneC makes it (2, 2, 2) skew=0 (OK)
    zones = {"zoneA": 2, "zoneB": 2, "zoneC": 1}
    assert is_placement_skew_acceptable(zones, "zoneC", max_skew=1) is True

    # Adding to zoneA makes it (3, 2, 1) -> skew = 3 - 1 = 2 > maxSkew (1) -> Invalid
    assert is_placement_skew_acceptable(zones, "zoneA", max_skew=1) is False

    # Single zone or balanced zones
    balanced = {"zoneA": 1, "zoneB": 1}
    assert is_placement_skew_acceptable(balanced, "zoneA", max_skew=1) is True

    print("✓ sched05 passed!")


if __name__ == "__main__":
    verify()

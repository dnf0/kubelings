"""
Exercise: solutions/07_scheduling/sched05.py
Topic: Topology Spread Constraints

Reference Solution
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
  - maxSkew: 1
    topologyKey: topology.kubernetes.io/zone
    whenUnsatisfiable: DoNotSchedule
    labelSelector:
      matchLabels:
        app: payment-processor
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
    updated_counts = dict(current_zone_counts)
    updated_counts[candidate_zone] = updated_counts.get(candidate_zone, 0) + 1

    values = list(updated_counts.values())
    if not values:
        return True
    skew = max(values) - min(values)
    return skew <= max_skew


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

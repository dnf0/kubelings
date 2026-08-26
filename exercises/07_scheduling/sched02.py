"""
Exercise: exercises/07_scheduling/sched02.py
Topic: Node Affinity & Constraints

Instructions:
Node Affinity allows expressive pod scheduling constraints:
1. `requiredDuringSchedulingIgnoredDuringExecution`: Hard constraint (must be satisfied for scheduling).
2. `preferredDuringSchedulingIgnoredDuringExecution`: Soft constraint with weights (1-100) to prioritize nodes.

1. Complete the Pod manifest:
   - name: 'affinity-app'
   - hard requirement: `topology.kubernetes.io/zone` must be `In` ['us-east-1a', 'us-east-1b']
   - soft preference (weight 80): `instance-type` is `In` ['c5.2xlarge', 'c5.4xlarge']
2. Implement `evaluate_node_affinity_score(node_labels, node_affinity)`:
   - Returns `(is_eligible: bool, score: int)`.
   - If hard requirement fails, return `(False, 0)`.
   - If hard requirement passes, return `(True, matching_weight_score)`.
"""

# I AM NOT DONE

from typing import Any, Dict, Tuple

import yaml

from kubelings.validator import validate_manifest

POD_MANIFEST = """
apiVersion: v1
kind: Pod
metadata:
  name: affinity-app
spec:
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
        - matchExpressions:
          - key: topology.kubernetes.io/zone
            operator: ???
            values:
            - ???
            - ???
      preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 80
        preference:
          matchExpressions:
          - key: instance-type
            operator: In
            values:
            - c5.2xlarge
            - c5.4xlarge
  containers:
  - name: server
    image: nginx:alpine
"""


def evaluate_node_affinity_score(
    node_labels: Dict[str, str],
    node_affinity: Dict[str, Any],
) -> Tuple[bool, int]:
    """Calculate whether a node is eligible and compute its preference affinity score."""
    # TODO: Implement node affinity evaluation
    return (False, 0)


def verify():
    manifest = yaml.safe_load(POD_MANIFEST)
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(manifest, expected_kind="Pod", expected_api_version="v1")

    node_aff = manifest["spec"]["affinity"]["nodeAffinity"]
    terms = node_aff["requiredDuringSchedulingIgnoredDuringExecution"]["nodeSelectorTerms"]
    expr = terms[0]["matchExpressions"][0]
    assert expr["key"] == "topology.kubernetes.io/zone"
    assert expr["operator"] == "In"
    assert "us-east-1a" in expr["values"]
    assert "us-east-1b" in expr["values"]

    pref = node_aff["preferredDuringSchedulingIgnoredDuringExecution"][0]
    assert pref["weight"] == 80

    # Node tests
    node_optimal = {"topology.kubernetes.io/zone": "us-east-1a", "instance-type": "c5.2xlarge"}
    node_valid_unpreferred = {
        "topology.kubernetes.io/zone": "us-east-1b",
        "instance-type": "t3.medium",
    }
    node_ineligible = {
        "topology.kubernetes.io/zone": "eu-central-1a",
        "instance-type": "c5.2xlarge",
    }

    assert evaluate_node_affinity_score(node_optimal, node_aff) == (True, 80)
    assert evaluate_node_affinity_score(node_valid_unpreferred, node_aff) == (True, 0)
    assert evaluate_node_affinity_score(node_ineligible, node_aff) == (False, 0)

    print("✓ sched02 passed!")


if __name__ == "__main__":
    verify()

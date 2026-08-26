"""
Exercise: solutions/07_scheduling/sched02.py
Topic: Node Affinity & Constraints

Reference Solution
"""

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
            operator: In
            values:
            - us-east-1a
            - us-east-1b
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
    # Check hard requirements
    req = node_affinity.get("requiredDuringSchedulingIgnoredDuringExecution", {})
    terms = req.get("nodeSelectorTerms", [])

    if terms:
        term_matched = False
        for term in terms:
            expressions = term.get("matchExpressions", [])
            all_expr_matched = True
            for expr in expressions:
                key = expr.get("key")
                op = expr.get("operator")
                values = expr.get("values", [])
                val_on_node = node_labels.get(key)

                if op == "In" and (val_on_node not in values):
                    all_expr_matched = False
                    break
                elif op == "NotIn" and (val_on_node in values):
                    all_expr_matched = False
                    break
                elif op == "Exists" and (key not in node_labels):
                    all_expr_matched = False
                    break
                elif op == "DoesNotExist" and (key in node_labels):
                    all_expr_matched = False
                    break

            if all_expr_matched:
                term_matched = True
                break

        if not term_matched:
            return (False, 0)

    # Check soft preferences
    score = 0
    prefs = node_affinity.get("preferredDuringSchedulingIgnoredDuringExecution", [])
    for pref in prefs:
        weight = pref.get("weight", 0)
        expressions = pref.get("preference", {}).get("matchExpressions", [])
        matched = True
        for expr in expressions:
            key = expr.get("key")
            op = expr.get("operator")
            values = expr.get("values", [])
            val_on_node = node_labels.get(key)
            if op == "In" and val_on_node not in values:
                matched = False
                break
        if matched:
            score += weight

    return (True, score)


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

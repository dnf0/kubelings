"""
Exercise: exercises/01_pods/pods06.py
Topic: Pod Disruption Budgets (PDB)

Context & Why:
High availability requires guarding against voluntary disruptions such as node drains
during cluster upgrades, kernel security patching, or cluster autoscaler scale-downs.
A PodDisruptionBudget (PDB) specifies the budget of replicas that can be safely disrupted
simultaneously, configured either via `minAvailable` or `maxUnavailable`. When an operator
or automated tool runs `kubectl drain`, the Kubernetes Eviction API checks the PDB and
blocks node evacuation if evicting a pod would violate the specified budget, preventing
accidental service outages during cluster maintenance.

Instructions:
A PodDisruptionBudget limits the number of Pods of a replicated application that are
down simultaneously from voluntary disruptions (e.g. node drains during upgrades).

Define a PodDisruptionBudget manifest named 'web-pdb':
1. apiVersion: policy/v1
2. kind: PodDisruptionBudget
3. spec.minAvailable: 2
4. spec.selector.matchLabels: app: web
"""

import yaml

from kubelings.validator import validate_manifest

PDB_MANIFEST = """
# TODO: Update apiVersion to policy/v1
# WHY: policy/v1 is the GA API version for PodDisruptionBudgets (policy/v1beta1 was deprecated and removed).
apiVersion: policy/v1beta1
kind: PodDisruptionBudget
metadata:
  # TODO: Set metadata.name to 'web-pdb'
  # WHY: Naming the PDB clearly associates the disruption budget with the application workloads it protects.
  name: ???
spec:
  # TODO: Configure minAvailable to 2
  # WHY: Guarantees that the eviction API will block voluntary disruptions if available replicas drop below 2.
  minAvailable: 0
  selector:
    matchLabels:
      # TODO: Match label 'app: web'
      # WHY: Connects the disruption budget to the target pods using label-based matching.
      app: ???
"""


def verify():
    manifest = yaml.safe_load(PDB_MANIFEST)
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(
        manifest, expected_kind="PodDisruptionBudget", expected_api_version="policy/v1"
    )

    assert manifest["metadata"]["name"] == "web-pdb", "PDB name must be 'web-pdb'"
    assert manifest["spec"].get("minAvailable") == 2, "spec.minAvailable must equal 2"

    selector = manifest["spec"].get("selector", {}).get("matchLabels", {})
    assert selector.get("app") == "web", "selector.matchLabels.app must equal 'web'"

    print("✓ pods06 passed!")


if __name__ == "__main__":
    verify()

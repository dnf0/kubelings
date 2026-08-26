"""
Exercise: solutions/01_pods/pods06.py
Topic: Pod Disruption Budgets (PDB)

Reference Solution
"""

import yaml

from kubelings.validator import validate_manifest

PDB_MANIFEST = """
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: web-pdb
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: web
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

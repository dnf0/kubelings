"""
Exercise: solutions/03_config_secrets/config05.py
Topic: Immutable ConfigMaps and Secrets

Reference Solution
"""

from typing import Any, Dict
import yaml
from kubelings.validator import validate_manifest

CONFIGMAP_MANIFEST = """
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-feature-flags
immutable: true
data:
  NEW_UI: "true"
  MAX_WORKERS: "8"
"""


def check_immutability_guard(existing: Dict[str, Any], updated: Dict[str, Any]) -> bool:
    """Verify that updates to an immutable resource do not alter data contents."""
    if existing.get("immutable") is True:
        for field in ("data", "stringData", "binaryData"):
            if existing.get(field) != updated.get(field):
                raise ValueError(f"Cannot update {field} of an immutable resource")
    return True


def verify():
    manifest = yaml.safe_load(CONFIGMAP_MANIFEST)
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(manifest, expected_kind="ConfigMap", expected_api_version="v1")

    assert manifest["metadata"]["name"] == "app-feature-flags"
    assert manifest.get("immutable") is True, "ConfigMap must have 'immutable: true'"
    assert manifest["data"]["NEW_UI"] == "true"
    assert manifest["data"]["MAX_WORKERS"] == "8"

    # Test unchanged update succeeds
    assert check_immutability_guard(manifest, manifest) is True

    # Test mutating data raises ValueError
    mutated = yaml.safe_load(CONFIGMAP_MANIFEST)
    mutated["data"]["MAX_WORKERS"] = "16"
    try:
        check_immutability_guard(manifest, mutated)
        raise AssertionError("Expected ValueError when mutating immutable ConfigMap data")
    except ValueError as e:
        assert "immutable" in str(e).lower()

    print("✓ config05 passed!")


if __name__ == "__main__":
    verify()

"""
Exercise: solutions/02_controllers/ctrl03.py
Topic: Deployment Rollbacks & Revision History

Reference Solution
"""

from typing import Any, Dict, List
import copy
import yaml
from kubelings.validator import validate_manifest

DEPLOYMENT_MANIFEST = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: versioned-app
spec:
  replicas: 3
  revisionHistoryLimit: 5
  selector:
    matchLabels:
      app: versioned-app
  template:
    metadata:
      labels:
        app: versioned-app
    spec:
      containers:
      - name: web
        image: nginx:1.24
"""


def simulate_rollout_history(
    base_manifest: Dict[str, Any], new_images: List[str]
) -> List[Dict[str, Any]]:
    """Simulate deployment image rollouts and return pruned revision history list."""
    limit = base_manifest.get("spec", {}).get("revisionHistoryLimit", 10)
    current_manifest = copy.deepcopy(base_manifest)
    history: List[Dict[str, Any]] = []

    for idx, img in enumerate(new_images, start=1):
        current_manifest["spec"]["template"]["spec"]["containers"][0]["image"] = img
        history.append({"revision": idx, "image": img})

    # Prune oldest revisions if exceeding limit
    if len(history) > limit:
        history = history[-limit:]

    return history


def verify():
    manifest = yaml.safe_load(DEPLOYMENT_MANIFEST)
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(manifest, expected_kind="Deployment", expected_api_version="apps/v1")

    assert manifest["metadata"]["name"] == "versioned-app"
    assert manifest["spec"].get("revisionHistoryLimit") == 5, (
        "spec.revisionHistoryLimit must equal 5"
    )

    # Simulate 8 updates with a history limit of 5
    images = [f"nginx:1.{v}" for v in range(20, 28)]  # 8 versions
    history = simulate_rollout_history(manifest, images)

    assert len(history) == 5, f"History should be pruned to 5 revisions, got {len(history)}"
    assert history[-1]["revision"] == 8, "Latest revision number must be 8"
    assert history[-1]["image"] == "nginx:1.27", "Latest image must be nginx:1.27"
    assert history[0]["revision"] == 4, "Oldest retained revision must be 4"

    print("✓ ctrl03 passed!")


if __name__ == "__main__":
    verify()

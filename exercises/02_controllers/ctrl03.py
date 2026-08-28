"""
Exercise: exercises/02_controllers/ctrl03.py
Topic: Deployment Rollbacks & Revision History

Context & Why:
Whenever a Deployment's pod template is modified, the Deployment controller provisions
a new ReplicaSet representing that revision while scaling down the previous ReplicaSet.
Kubernetes retains previous ReplicaSets in etcd up to the number specified by
`revisionHistoryLimit`. This enables instant rollbacks (`kubectl rollout undo`) to any
earlier stable revision. Setting an appropriate `revisionHistoryLimit` (e.g. 5 or 10)
balances operational safety with etcd database cleanliness, preventing thousands of
dormant ReplicaSets from accumulating over time.

Instructions:
Kubernetes retains rollout history as underlying ReplicaSets up to `revisionHistoryLimit`.
This enables rolling back failed deployments (`kubectl rollout undo`).

1. Set `revisionHistoryLimit: 5` in the Deployment manifest below.
2. Implement `simulate_rollout_history` to simulate successive image updates:
   - For each new image, update the container image in the manifest.
   - Record the revision in history: `{"revision": revision_num, "image": image}`.
   - Ensure the returned history list only keeps the latest `revisionHistoryLimit` revisions.
"""

import copy  # noqa: F401
from typing import Any, Dict, List

import yaml

from kubelings.validator import validate_manifest

DEPLOYMENT_MANIFEST = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: versioned-app
spec:
  replicas: 3
  # TODO: Configure revisionHistoryLimit to 5
  # WHY: Retains the 5 most recent ReplicaSets for rollback recovery while pruning older ReplicaSets to prevent etcd bloat.
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
    # TODO: Implement rollout history tracking and revision limit pruning
    # WHY: Replicates the Deployment controller's internal ReplicaSet retention algorithm that garbage-collects old revisions beyond the revisionHistoryLimit.
    return []


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

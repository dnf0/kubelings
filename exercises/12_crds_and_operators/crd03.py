"""
Exercise: exercises/12_crds_and_operators/crd03.py
Topic: Python Kubernetes Operator Loop

Instructions:
A Kubernetes Operator encodes domain-specific operational knowledge into software.
The core of every operator is the reconciliation loop:
1. Observe the current state of custom resources and child objects.
2. Compare the desired state (`spec`) with observed state.
3. Take corrective actions (create, scale, update) to bring current state to desired state.
4. Update the custom resource `status` subresource with the observed condition and phase.

Implement the `reconcile_database` operator function according to these rules:
- If `existing_deployment` is None:
    Return action "CREATE" with deployment spec (name matching CR name, image "{engine}:{version}", replicas),
    and status_patch {"phase": "Creating", "observedGeneration": generation}.
- If `existing_deployment` exists:
    - If `existing_deployment["replicas"] != replicas`:
        Return action "SCALE" with new replicas count,
        and status_patch {"phase": "Scaling", "observedGeneration": generation}.
    - Else if `existing_deployment.get("readyReplicas", 0) == replicas`:
        Return action "NONE" with status_patch {"phase": "Ready", "observedGeneration": generation}.
    - Else:
        Return action "NONE" with status_patch {"phase": "Progressing", "observedGeneration": generation}.
"""

# I AM NOT DONE

from typing import Any, Dict, Optional

import yaml

from kubelings.validator import validate_manifest

SAMPLE_CR_MANIFEST = """
apiVersion: database.example.com/v1alpha1
kind: Database
metadata:
  name: prod-postgres
  namespace: data-tier
  generation: 1
spec:
  engine: postgres
  version: "16.1"
  replicas: 3
"""


def reconcile_database(
    custom_resource: Dict[str, Any],
    existing_deployment: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    # TODO: Implement operator reconciliation logic using custom_resource and existing_deployment
    return {
        "action": "TODO",
        "status_patch": {},
    }


def verify():
    manifest = yaml.safe_load(SAMPLE_CR_MANIFEST)
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(
        manifest,
        expected_kind="Database",
        expected_api_version="database.example.com/v1alpha1",
    )

    cr = manifest

    # Scenario 1: Deployment does not exist yet -> Create deployment
    res1 = reconcile_database(cr, existing_deployment=None)
    assert res1["action"] == "CREATE", "Expected action 'CREATE' when deployment is missing"
    assert res1["deployment"]["name"] == "prod-postgres"
    assert res1["deployment"]["image"] == "postgres:16.1"
    assert res1["deployment"]["replicas"] == 3
    assert res1["status_patch"]["phase"] == "Creating"
    assert res1["status_patch"]["observedGeneration"] == 1

    # Scenario 2: Deployment exists but has wrong replicas -> Scale deployment
    current_dep_wrong_scale = {"name": "prod-postgres", "replicas": 1, "readyReplicas": 1}
    res2 = reconcile_database(cr, existing_deployment=current_dep_wrong_scale)
    assert res2["action"] == "SCALE", "Expected action 'SCALE' when replica count differs"
    assert res2["replicas"] == 3
    assert res2["status_patch"]["phase"] == "Scaling"

    # Scenario 3: Deployment exists, scaling in progress (readyReplicas < desired) -> Progressing
    current_dep_progressing = {"name": "prod-postgres", "replicas": 3, "readyReplicas": 1}
    res3 = reconcile_database(cr, existing_deployment=current_dep_progressing)
    assert res3["action"] == "NONE"
    assert res3["status_patch"]["phase"] == "Progressing"

    # Scenario 4: Deployment is fully healthy and ready -> Ready
    current_dep_ready = {"name": "prod-postgres", "replicas": 3, "readyReplicas": 3}
    res4 = reconcile_database(cr, existing_deployment=current_dep_ready)
    assert res4["action"] == "NONE"
    assert res4["status_patch"]["phase"] == "Ready"

    print("✓ crd03 passed!")


if __name__ == "__main__":
    verify()

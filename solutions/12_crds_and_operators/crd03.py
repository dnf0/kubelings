"""
Exercise: solutions/12_crds_and_operators/crd03.py
Topic: Python Kubernetes Operator Loop

Reference Solution
"""

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
    metadata = custom_resource.get("metadata", {})
    name = metadata.get("name", "")
    generation = metadata.get("generation", 1)
    spec = custom_resource.get("spec", {})
    engine = spec.get("engine", "postgres")
    version = spec.get("version", "latest")
    desired_replicas = spec.get("replicas", 1)

    if existing_deployment is None:
        return {
            "action": "CREATE",
            "deployment": {
                "name": name,
                "image": f"{engine}:{version}",
                "replicas": desired_replicas,
            },
            "status_patch": {
                "phase": "Creating",
                "observedGeneration": generation,
            },
        }

    current_replicas = existing_deployment.get("replicas", 0)
    if current_replicas != desired_replicas:
        return {
            "action": "SCALE",
            "replicas": desired_replicas,
            "status_patch": {
                "phase": "Scaling",
                "observedGeneration": generation,
            },
        }

    ready_replicas = existing_deployment.get("readyReplicas", 0)
    if ready_replicas == desired_replicas:
        phase = "Ready"
    else:
        phase = "Progressing"

    return {
        "action": "NONE",
        "status_patch": {
            "phase": phase,
            "observedGeneration": generation,
        },
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

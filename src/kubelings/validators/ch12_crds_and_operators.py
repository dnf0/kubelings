"""
Validators for Chapter 12: Custom Resources, CRDs & Operators
"""

from typing import Any, Dict, Optional

from kubelings.validator import validate_manifest
from kubelings.validators import register_validator


@register_validator("crd01")
def validate_crd01(manifest: Any, raw_yaml: str = "") -> None:
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(
        manifest,
        expected_kind="CustomResourceDefinition",
        expected_api_version="apiextensions.k8s.io/v1",
    )
    metadata = manifest.get("metadata", {})
    assert metadata.get("name") == "databases.database.example.com"
    spec = manifest.get("spec", {})
    assert spec.get("group") == "database.example.com"
    assert spec.get("scope") == "Namespaced"
    names = spec.get("names", {})
    assert names.get("plural") == "databases"
    assert names.get("singular") == "database"
    assert names.get("kind") == "Database"
    assert names.get("shortNames") == ["db"]
    versions = spec.get("versions", [])
    assert len(versions) == 1
    v = versions[0]
    assert v.get("name") == "v1alpha1"
    assert v.get("served") is True
    assert v.get("storage") is True
    schema = v.get("schema", {}).get("openAPIV3Schema", {})
    assert schema.get("type") == "object"
    spec_props = schema.get("properties", {}).get("spec", {})
    assert spec_props.get("type") == "object"
    assert set(spec_props.get("required", [])) == {"engine", "version", "replicas"}
    inner_props = spec_props.get("properties", {})
    assert inner_props.get("engine", {}).get("enum") == ["postgres", "mysql", "redis"]
    assert inner_props.get("replicas", {}).get("minimum") == 1
    assert inner_props.get("replicas", {}).get("maximum") == 5
    assert inner_props.get("storageGB", {}).get("minimum") == 10


@register_validator("crd02")
def validate_crd02(manifest: Any, raw_yaml: str = "") -> None:
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(
        manifest,
        expected_kind="CustomResourceDefinition",
        expected_api_version="apiextensions.k8s.io/v1",
    )
    metadata = manifest.get("metadata", {})
    assert metadata.get("name") == "backups.backup.example.com"
    spec = manifest.get("spec", {})
    assert spec.get("group") == "backup.example.com"
    assert spec.get("names", {}).get("kind") == "Backup"
    versions = spec.get("versions", [])
    assert len(versions) == 1
    v = versions[0]
    assert v.get("name") == "v1"
    subresources = v.get("subresources", {})
    assert "status" in subresources, "Must define 'status: {}' subresource"
    scale = subresources.get("scale", {})
    assert scale.get("specReplicasPath") == ".spec.replicas"
    assert scale.get("statusReplicasPath") == ".status.replicas"
    columns = v.get("additionalPrinterColumns", [])
    assert len(columns) == 3, "Must define 3 additionalPrinterColumns"
    col_map = {c.get("name"): c for c in columns}
    assert "Schedule" in col_map
    assert col_map["Schedule"].get("type") == "string"
    assert col_map["Schedule"].get("jsonPath") == ".spec.schedule"
    assert "Status" in col_map
    assert col_map["Status"].get("type") == "string"
    assert col_map["Status"].get("jsonPath") == ".status.phase"
    assert "Age" in col_map
    assert col_map["Age"].get("type") == "date"
    assert col_map["Age"].get("jsonPath") == ".metadata.creationTimestamp"


def reconcile_database(
    custom_resource: Dict[str, Any], existing_deployment: Optional[Dict[str, Any]]
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
            "status_patch": {"phase": "Creating", "observedGeneration": generation},
        }
    current_replicas = existing_deployment.get("replicas", 0)
    if current_replicas != desired_replicas:
        return {
            "action": "SCALE",
            "replicas": desired_replicas,
            "status_patch": {"phase": "Scaling", "observedGeneration": generation},
        }
    ready_replicas = existing_deployment.get("readyReplicas", 0)
    if ready_replicas == desired_replicas:
        phase = "Ready"
    else:
        phase = "Progressing"
    return {"action": "NONE", "status_patch": {"phase": phase, "observedGeneration": generation}}


@register_validator("crd03")
def validate_crd03(manifest: Any, raw_yaml: str = "") -> None:
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(
        manifest, expected_kind="Database", expected_api_version="database.example.com/v1alpha1"
    )
    cr = manifest
    res1 = reconcile_database(cr, existing_deployment=None)
    assert res1["action"] == "CREATE", "Expected action 'CREATE' when deployment is missing"
    assert res1["deployment"]["name"] == "prod-postgres"
    assert res1["deployment"]["image"] == "postgres:16.1"
    assert res1["deployment"]["replicas"] == 3
    assert res1["status_patch"]["phase"] == "Creating"
    assert res1["status_patch"]["observedGeneration"] == 1
    current_dep_wrong_scale = {"name": "prod-postgres", "replicas": 1, "readyReplicas": 1}
    res2 = reconcile_database(cr, existing_deployment=current_dep_wrong_scale)
    assert res2["action"] == "SCALE", "Expected action 'SCALE' when replica count differs"
    assert res2["replicas"] == 3
    assert res2["status_patch"]["phase"] == "Scaling"
    current_dep_progressing = {"name": "prod-postgres", "replicas": 3, "readyReplicas": 1}
    res3 = reconcile_database(cr, existing_deployment=current_dep_progressing)
    assert res3["action"] == "NONE"
    assert res3["status_patch"]["phase"] == "Progressing"
    current_dep_ready = {"name": "prod-postgres", "replicas": 3, "readyReplicas": 3}
    res4 = reconcile_database(cr, existing_deployment=current_dep_ready)
    assert res4["action"] == "NONE"
    assert res4["status_patch"]["phase"] == "Ready"


def handle_admission_review(review: Dict[str, Any]) -> Dict[str, Any]:
    req = review.get("request", {})
    uid = req.get("uid", "")
    pod_obj = req.get("object", {})
    spec = pod_obj.get("spec", {})
    pod_sec = spec.get("securityContext", {})
    containers = spec.get("containers", [])
    for c in containers:
        c_sec = c.get("securityContext", {})
        if c_sec.get("privileged") is True:
            return {
                "apiVersion": "admission.k8s.io/v1",
                "kind": "AdmissionReview",
                "response": {
                    "uid": uid,
                    "allowed": False,
                    "status": {"code": 403, "message": "Privileged containers are not allowed."},
                },
            }
        is_non_root = (
            c_sec.get("runAsNonRoot") is True
            or (isinstance(c_sec.get("runAsUser"), int) and c_sec["runAsUser"] > 0)
            or pod_sec.get("runAsNonRoot") is True
            or (isinstance(pod_sec.get("runAsUser"), int) and pod_sec["runAsUser"] > 0)
        )
        if not is_non_root:
            return {
                "apiVersion": "admission.k8s.io/v1",
                "kind": "AdmissionReview",
                "response": {
                    "uid": uid,
                    "allowed": False,
                    "status": {"code": 403, "message": "Containers must run as non-root user."},
                },
            }
    return {
        "apiVersion": "admission.k8s.io/v1",
        "kind": "AdmissionReview",
        "response": {"uid": uid, "allowed": True},
    }


@register_validator("crd04")
def validate_crd04(manifest: Any, raw_yaml: str = "") -> None:
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(
        manifest,
        expected_kind="ValidatingWebhookConfiguration",
        expected_api_version="admissionregistration.k8s.io/v1",
    )
    metadata = manifest.get("metadata", {})
    assert metadata.get("name") == "pod-security-webhook"
    webhooks = manifest.get("webhooks", [])
    assert len(webhooks) == 1
    wh = webhooks[0]
    assert wh.get("name") == "validate-security.example.com"
    assert wh.get("sideEffects") == "None"
    assert wh.get("admissionReviewVersions") == ["v1"]
    rule = wh.get("rules", [])[0]
    assert set(rule.get("operations", [])) == {"CREATE", "UPDATE"}
    assert rule.get("resources") == ["pods"]
    svc = wh.get("clientConfig", {}).get("service", {})
    assert svc.get("name") == "security-webhook-svc"
    assert svc.get("namespace") == "kube-system"
    assert svc.get("path") == "/validate-pods"
    assert svc.get("port") == 443
    bad_req_privileged = {
        "request": {
            "uid": "req-111",
            "object": {
                "spec": {
                    "containers": [
                        {
                            "name": "app",
                            "securityContext": {"privileged": True, "runAsNonRoot": True},
                        }
                    ]
                }
            },
        }
    }
    resp1 = handle_admission_review(bad_req_privileged)
    assert resp1["response"]["uid"] == "req-111"
    assert resp1["response"]["allowed"] is False
    assert resp1["response"].get("status", {}).get("code") == 403
    bad_req_root = {
        "request": {
            "uid": "req-222",
            "object": {"spec": {"containers": [{"name": "app", "image": "nginx"}]}},
        }
    }
    resp2 = handle_admission_review(bad_req_root)
    assert resp2["response"]["uid"] == "req-222"
    assert resp2["response"]["allowed"] is False
    assert resp2["response"].get("status", {}).get("code") == 403
    good_req = {
        "request": {
            "uid": "req-333",
            "object": {
                "spec": {
                    "securityContext": {"runAsNonRoot": True, "runAsUser": 10001},
                    "containers": [
                        {
                            "name": "app",
                            "image": "nginx:alpine",
                            "securityContext": {"allowPrivilegeEscalation": False},
                        }
                    ],
                }
            },
        }
    }
    resp3 = handle_admission_review(good_req)
    assert resp3["response"]["uid"] == "req-333"
    assert resp3["response"]["allowed"] is True

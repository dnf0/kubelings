"""
Validators for Chapter 28: Google Cloud GKE & Ecosystem
"""

from typing import Any

from kubelings.validator import validate_manifest_text
from kubelings.validators import register_validator


@register_validator("gke01")
def validate_gke01(manifest: Any, raw_yaml: str = "") -> None:
    passed, errors = validate_manifest_text(raw_yaml, "gke01")
    assert passed, f"GKE Workload Identity manifest validation failed: {errors}"
    docs = manifest if isinstance(manifest, list) else [manifest]
    assert len(docs) == 2, "Manifest must define exactly 2 documents (ServiceAccount and Pod)"

    sa_doc = next((d for d in docs if d.get("kind") == "ServiceAccount"), None)
    assert sa_doc is not None, "Missing ServiceAccount document"
    assert sa_doc["metadata"]["name"] == "bigquery-sa", "ServiceAccount name must be 'bigquery-sa'"
    annotations = sa_doc["metadata"].get("annotations", {})
    assert (
        annotations.get("iam.gke.io/gcp-service-account")
        == "bq-sync@my-gcp-project.iam.gserviceaccount.com"
    ), (
        "ServiceAccount must have annotation 'iam.gke.io/gcp-service-account: bq-sync@my-gcp-project.iam.gserviceaccount.com'"
    )

    pod_doc = next((d for d in docs if d.get("kind") == "Pod"), None)
    assert pod_doc is not None, "Missing Pod document"
    assert pod_doc["metadata"]["name"] == "bq-loader-pod", "Pod name must be 'bq-loader-pod'"
    assert pod_doc["spec"].get("serviceAccountName") == "bigquery-sa", (
        "Pod spec.serviceAccountName must be 'bigquery-sa'"
    )
    node_sel = pod_doc["spec"].get("nodeSelector", {})
    assert node_sel.get("iam.gke.io/gke-metadata-server-enabled") == "true", (
        "nodeSelector must specify 'iam.gke.io/gke-metadata-server-enabled: \"true\"'"
    )
    container = pod_doc["spec"]["containers"][0]
    assert container["name"] == "loader", "Container name must be 'loader'"
    assert container["image"] == "google/cloud-sdk:slim", (
        "Container image must be 'google/cloud-sdk:slim'"
    )


@register_validator("gke02")
def validate_gke02(manifest: Any, raw_yaml: str = "") -> None:
    passed, errors = validate_manifest_text(raw_yaml, "gke02")
    assert passed, f"GKE Autopilot Deployment manifest validation failed: {errors}"
    assert manifest["kind"] == "Deployment", "Kind must be 'Deployment'"
    assert manifest["metadata"]["name"] == "analytics-worker", "Name must be 'analytics-worker'"
    assert manifest["spec"]["replicas"] == 3, "spec.replicas must be 3"
    annotations = manifest["spec"]["template"]["metadata"].get("annotations", {})
    assert annotations.get("autopilot.gke.io/compute-class") == "Performance", (
        "Pod template must have annotation 'autopilot.gke.io/compute-class: Performance'"
    )
    container = manifest["spec"]["template"]["spec"]["containers"][0]
    assert container["name"] == "processor", "Container name must be 'processor'"
    reqs = container["resources"]["requests"]
    assert str(reqs.get("cpu")) == "2", "CPU request must be '2'"
    assert reqs.get("memory") == "8Gi", "Memory request must be '8Gi'"


@register_validator("gke03")
def validate_gke03(manifest: Any, raw_yaml: str = "") -> None:
    passed, errors = validate_manifest_text(raw_yaml, "gke03")
    assert passed, f"GCPBackendPolicy manifest validation failed: {errors}"
    assert manifest["kind"] == "GCPBackendPolicy", "Kind must be 'GCPBackendPolicy'"
    assert manifest["metadata"]["name"] == "cloud-armor-backend-policy", (
        "Name must be 'cloud-armor-backend-policy'"
    )
    target = manifest["spec"]["targetRef"]
    assert target.get("kind") == "Service", "targetRef.kind must be 'Service'"
    assert target.get("name") == "web-frontend-svc", "targetRef.name must be 'web-frontend-svc'"
    default_cfg = manifest["spec"]["default"]
    assert default_cfg.get("securityPolicy") == "edge-ddos-protection-policy", (
        "default.securityPolicy must be 'edge-ddos-protection-policy'"
    )
    assert default_cfg.get("logging", {}).get("enable") is True, "logging.enable must be true"


@register_validator("gke04")
def validate_gke04(manifest: Any, raw_yaml: str = "") -> None:
    passed, errors = validate_manifest_text(raw_yaml, "gke04")
    assert passed, f"StorageBucket manifest validation failed: {errors}"
    assert manifest["kind"] == "StorageBucket", "Kind must be 'StorageBucket'"
    assert manifest["metadata"]["name"] == "prod-analytics-archive-bucket", (
        "Name must be 'prod-analytics-archive-bucket'"
    )
    annotations = manifest["metadata"].get("annotations", {})
    assert annotations.get("cnrm.cloud.google.com/deletion-policy") == "abandon", (
        "Annotation 'cnrm.cloud.google.com/deletion-policy' must be 'abandon'"
    )
    assert manifest["spec"]["location"] == "US-CENTRAL1", "spec.location must be 'US-CENTRAL1'"
    assert manifest["spec"]["storageClass"] == "STANDARD", "spec.storageClass must be 'STANDARD'"
    assert manifest["spec"]["uniformBucketLevelAccess"] is True, (
        "spec.uniformBucketLevelAccess must be true"
    )
    assert manifest["spec"]["versioning"]["enabled"] is True, "spec.versioning.enabled must be true"

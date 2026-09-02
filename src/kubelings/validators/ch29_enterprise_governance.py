"""
Validators for Chapter 29: Enterprise Multi-Account Governance & Secret Management
"""

from typing import Any

from kubelings.validator import validate_manifest_text
from kubelings.validators import register_validator


@register_validator("eso01")
def validate_eso01(manifest: Any, raw_yaml: str = "") -> None:
    passed, errors = validate_manifest_text(raw_yaml, "eso01")
    assert passed, f"External Secrets manifest validation failed: {errors}"
    docs = manifest if isinstance(manifest, list) else [manifest]
    assert len(docs) == 2, "Manifest must define exactly 2 documents (SecretStore and ExternalSecret)"

    store_doc = next((d for d in docs if d.get("kind") == "SecretStore"), None)
    assert store_doc is not None, "Missing SecretStore document"
    assert store_doc["metadata"]["name"] == "aws-secrets-store", (
        "SecretStore name must be 'aws-secrets-store'"
    )
    provider_aws = store_doc["spec"]["provider"]["aws"]
    assert provider_aws.get("service") == "SecretsManager", (
        "AWS provider service must be 'SecretsManager'"
    )
    assert provider_aws.get("region") == "us-east-1", "AWS provider region must be 'us-east-1'"

    ext_doc = next((d for d in docs if d.get("kind") == "ExternalSecret"), None)
    assert ext_doc is not None, "Missing ExternalSecret document"
    assert ext_doc["metadata"]["name"] == "app-db-credentials", (
        "ExternalSecret name must be 'app-db-credentials'"
    )
    assert ext_doc["spec"]["secretStoreRef"]["name"] == "aws-secrets-store", (
        "secretStoreRef.name must be 'aws-secrets-store'"
    )
    assert ext_doc["spec"]["target"]["name"] == "db-credentials-secret", (
        "target.name must be 'db-credentials-secret'"
    )
    data_entry = ext_doc["spec"]["data"][0]
    assert data_entry["secretKey"] == "password", "data[0].secretKey must be 'password'"
    assert data_entry["remoteRef"]["key"] == "prod/rds/app-password", (
        "data[0].remoteRef.key must be 'prod/rds/app-password'"
    )


@register_validator("vault01")
def validate_vault01(manifest: Any, raw_yaml: str = "") -> None:
    passed, errors = validate_manifest_text(raw_yaml, "vault01")
    assert passed, f"Vault Agent Pod manifest validation failed: {errors}"
    assert manifest["kind"] == "Pod", "Kind must be 'Pod'"
    assert manifest["metadata"]["name"] == "secure-billing-service", (
        "Name must be 'secure-billing-service'"
    )
    annotations = manifest["metadata"].get("annotations", {})
    assert annotations.get("vault.hashicorp.com/agent-inject") == "true", (
        "Annotation 'vault.hashicorp.com/agent-inject' must be 'true'"
    )
    assert annotations.get("vault.hashicorp.com/role") == "billing-app-role", (
        "Annotation 'vault.hashicorp.com/role' must be 'billing-app-role'"
    )
    assert (
        annotations.get("vault.hashicorp.com/agent-inject-secret-database-config")
        == "secret/data/billing/db"
    ), "Annotation 'vault.hashicorp.com/agent-inject-secret-database-config' must be 'secret/data/billing/db'"
    assert manifest["spec"].get("serviceAccountName") == "billing-service-sa", (
        "Pod spec.serviceAccountName must be 'billing-service-sa'"
    )
    container = manifest["spec"]["containers"][0]
    assert container["name"] == "billing-api", "Container name must be 'billing-api'"
    assert container["image"] == "billing/app:v2.4", "Container image must be 'billing/app:v2.4'"


@register_validator("gov01")
def validate_gov01(manifest: Any, raw_yaml: str = "") -> None:
    passed, errors = validate_manifest_text(raw_yaml, "gov01")
    assert passed, f"ArgoCD ApplicationSet manifest validation failed: {errors}"
    assert manifest["kind"] == "ApplicationSet", "Kind must be 'ApplicationSet'"
    assert manifest["metadata"]["name"] == "fleet-baseline-monitoring", (
        "Name must be 'fleet-baseline-monitoring'"
    )
    matrix = manifest["spec"]["generators"][0]["matrix"]
    cluster_gen = next((g for g in matrix["generators"] if "clusters" in g), None)
    assert cluster_gen is not None, "Matrix generator must include clusters generator"
    assert (
        cluster_gen["clusters"]["selector"]["matchLabels"].get("tier") == "production"
    ), "Cluster selector must match 'tier: production'"
    git_gen = next((g for g in matrix["generators"] if "git" in g), None)
    assert git_gen is not None, "Matrix generator must include git generator"
    assert "monitoring/*" in [d.get("path") for d in git_gen["git"]["directories"]], (
        "Git generator directories must include 'monitoring/*'"
    )
    template_spec = manifest["spec"]["template"]["spec"]
    assert template_spec["destination"]["server"] == "{{server}}", (
        "destination.server must be '{{server}}'"
    )
    assert template_spec["destination"]["namespace"] == "monitoring", (
        "destination.namespace must be 'monitoring'"
    )


@register_validator("gov02")
def validate_gov02(manifest: Any, raw_yaml: str = "") -> None:
    passed, errors = validate_manifest_text(raw_yaml, "gov02")
    assert passed, f"Governance Multi-Tenant manifest validation failed: {errors}"
    docs = manifest if isinstance(manifest, list) else [manifest]
    assert len(docs) == 2, "Manifest must define exactly 2 documents (ResourceQuota and LimitRange)"

    quota_doc = next((d for d in docs if d.get("kind") == "ResourceQuota"), None)
    assert quota_doc is not None, "Missing ResourceQuota document"
    assert quota_doc["metadata"]["name"] == "tenant-compute-quota", (
        "ResourceQuota name must be 'tenant-compute-quota'"
    )
    assert quota_doc["metadata"]["namespace"] == "tenant-alpha", (
        "ResourceQuota namespace must be 'tenant-alpha'"
    )
    hard = quota_doc["spec"]["hard"]
    assert hard.get("requests.cpu") == "16", "hard.requests.cpu must be '16'"
    assert hard.get("requests.memory") == "64Gi", "hard.requests.memory must be '64Gi'"
    assert hard.get("limits.cpu") == "32", "hard.limits.cpu must be '32'"
    assert hard.get("limits.memory") == "128Gi", "hard.limits.memory must be '128Gi'"

    limit_doc = next((d for d in docs if d.get("kind") == "LimitRange"), None)
    assert limit_doc is not None, "Missing LimitRange document"
    assert limit_doc["metadata"]["name"] == "tenant-limits", (
        "LimitRange name must be 'tenant-limits'"
    )
    assert limit_doc["metadata"]["namespace"] == "tenant-alpha", (
        "LimitRange namespace must be 'tenant-alpha'"
    )
    limit_item = limit_doc["spec"]["limits"][0]
    assert limit_item.get("type") == "Container", "LimitRange item type must be 'Container'"
    assert limit_item.get("default", {}).get("cpu") == "1", "default.cpu must be '1'"
    assert limit_item.get("default", {}).get("memory") == "2Gi", "default.memory must be '2Gi'"

"""
Validators for Chapter 22: Infrastructure as Data with Crossplane
"""

from typing import Any

from kubelings.validators import register_validator


def build_xrd() -> dict:
    return {
        "apiVersion": "apiextensions.crossplane.io/v1",
        "kind": "CompositeResourceDefinition",
        "metadata": {"name": "xpostgresqlinstances.database.kubelings.io"},
        "spec": {
            "group": "database.kubelings.io",
            "names": {"kind": "XPostgreSQLInstance", "plural": "xpostgresqlinstances"},
            "claimNames": {"kind": "PostgreSQLInstance", "plural": "postgresqlinstances"},
            "versions": [
                {
                    "name": "v1alpha1",
                    "served": True,
                    "referenceable": True,
                    "schema": {
                        "openAPIV3Schema": {
                            "type": "object",
                            "properties": {
                                "spec": {
                                    "type": "object",
                                    "properties": {
                                        "parameters": {
                                            "type": "object",
                                            "properties": {
                                                "storageGB": {"type": "integer"},
                                                "engineVersion": {"type": "string"},
                                            },
                                            "required": ["storageGB", "engineVersion"],
                                        }
                                    },
                                }
                            },
                        }
                    },
                }
            ],
        },
    }


@register_validator("crossplane01")
def validate_crossplane01(manifest: Any, raw_yaml: str = "") -> None:
    xrd = manifest
    assert xrd.get("apiVersion") == "apiextensions.crossplane.io/v1"
    assert xrd.get("kind") == "CompositeResourceDefinition"
    assert xrd.get("metadata", {}).get("name") == "xpostgresqlinstances.database.kubelings.io"
    spec = xrd.get("spec", {})
    assert spec.get("group") == "database.kubelings.io"
    assert spec.get("names", {}).get("kind") == "XPostgreSQLInstance"
    assert spec.get("claimNames", {}).get("kind") == "PostgreSQLInstance"
    versions = spec.get("versions", [])
    assert len(versions) >= 1
    v0 = versions[0]
    assert v0.get("name") == "v1alpha1"
    assert v0.get("served") is True
    assert v0.get("referenceable") is True
    schema = v0.get("schema", {}).get("openAPIV3Schema", {})
    params = (
        schema.get("properties", {}).get("spec", {}).get("properties", {}).get("parameters", {})
    )
    props = params.get("properties", {})
    assert "storageGB" in props and props["storageGB"].get("type") == "integer"
    assert "engineVersion" in props and props["engineVersion"].get("type") == "string"
    assert "storageGB" in params.get("required", [])
    assert "engineVersion" in params.get("required", [])


def build_composition() -> dict:
    return {
        "apiVersion": "apiextensions.crossplane.io/v1",
        "kind": "Composition",
        "metadata": {
            "name": "postgres-aws-composition",
            "labels": {"provider": "aws", "db": "postgres"},
        },
        "spec": {
            "compositeTypeRef": {
                "apiVersion": "database.kubelings.io/v1alpha1",
                "kind": "XPostgreSQLInstance",
            },
            "resources": [
                {
                    "base": {
                        "apiVersion": "rds.aws.upbound.io/v1beta1",
                        "kind": "Instance",
                        "spec": {
                            "forProvider": {
                                "instanceClass": "db.t3.micro",
                                "skipFinalSnapshot": True,
                            }
                        },
                    },
                    "patches": [
                        {
                            "type": "FromCompositeFieldPath",
                            "fromFieldPath": "spec.parameters.storageGB",
                            "toFieldPath": "spec.forProvider.allocatedStorage",
                        },
                        {
                            "type": "FromCompositeFieldPath",
                            "fromFieldPath": "spec.parameters.engineVersion",
                            "toFieldPath": "spec.forProvider.engineVersion",
                        },
                    ],
                }
            ],
        },
    }


@register_validator("crossplane02")
def validate_crossplane02(manifest: Any, raw_yaml: str = "") -> None:
    comp = manifest
    assert comp.get("apiVersion") == "apiextensions.crossplane.io/v1"
    assert comp.get("kind") == "Composition"
    assert comp.get("metadata", {}).get("name") == "postgres-aws-composition"
    assert comp.get("metadata", {}).get("labels", {}).get("provider") == "aws"
    type_ref = comp.get("spec", {}).get("compositeTypeRef", {})
    assert type_ref.get("kind") == "XPostgreSQLInstance"
    resources = comp.get("spec", {}).get("resources", [])
    assert len(resources) == 1, f"Expected 1 composed resource, found {len(resources)}"
    res0 = resources[0]
    base = res0.get("base", {})
    assert base.get("kind") == "Instance"
    assert base.get("spec", {}).get("forProvider", {}).get("skipFinalSnapshot") is True
    patches = res0.get("patches", [])
    assert len(patches) >= 2, f"Expected at least 2 patches, found {len(patches)}"
    p_storage = next(
        (p for p in patches if p.get("toFieldPath") == "spec.forProvider.allocatedStorage"), None
    )
    assert p_storage is not None, "Missing storage allocation patch"
    assert p_storage.get("fromFieldPath") == "spec.parameters.storageGB"
    p_engine = next(
        (p for p in patches if p.get("toFieldPath") == "spec.forProvider.engineVersion"), None
    )
    assert p_engine is not None, "Missing engine version patch"
    assert p_engine.get("fromFieldPath") == "spec.parameters.engineVersion"


def build_provider_and_resource() -> list[dict]:
    provider_config = {
        "apiVersion": "aws.upbound.io/v1beta1",
        "kind": "ProviderConfig",
        "metadata": {"name": "default-aws-provider"},
        "spec": {
            "credentials": {
                "source": "Secret",
                "secretRef": {
                    "namespace": "crossplane-system",
                    "name": "aws-credentials",
                    "key": "creds",
                },
            }
        },
    }
    bucket = {
        "apiVersion": "s3.aws.upbound.io/v1beta1",
        "kind": "Bucket",
        "metadata": {"name": "app-assets-bucket"},
        "spec": {"providerConfigRef": {"name": "default-aws-provider"}, "deletionPolicy": "Delete"},
    }
    return [provider_config, bucket]


@register_validator("crossplane03")
def validate_crossplane03(manifest: Any, raw_yaml: str = "") -> None:
    manifests = manifest
    assert len(manifests) == 2, f"Expected 2 manifests, found {len(manifests)}"
    pc = next((m for m in manifests if m.get("kind") == "ProviderConfig"), None)
    assert pc is not None, "Missing ProviderConfig manifest"
    assert pc.get("metadata", {}).get("name") == "default-aws-provider"
    creds = pc.get("spec", {}).get("credentials", {})
    assert creds.get("source") == "Secret"
    assert creds.get("secretRef", {}).get("name") == "aws-credentials"
    assert creds.get("secretRef", {}).get("namespace") == "crossplane-system"
    bucket = next((m for m in manifests if m.get("kind") == "Bucket"), None)
    assert bucket is not None, "Missing Bucket manifest"
    assert bucket.get("metadata", {}).get("name") == "app-assets-bucket"
    assert bucket.get("spec", {}).get("providerConfigRef", {}).get("name") == "default-aws-provider"
    assert bucket.get("spec", {}).get("deletionPolicy") == "Delete"


def build_developer_claim() -> dict:
    return {
        "apiVersion": "database.kubelings.io/v1alpha1",
        "kind": "PostgreSQLInstance",
        "metadata": {"name": "production-postgres-claim", "namespace": "production"},
        "spec": {
            "parameters": {"storageGB": 100, "engineVersion": "16.1"},
            "compositionSelector": {"matchLabels": {"provider": "aws", "db": "postgres"}},
            "writeConnectionSecretToRef": {"name": "production-postgres-conn"},
        },
    }


@register_validator("crossplane04")
def validate_crossplane04(manifest: Any, raw_yaml: str = "") -> None:
    claim = manifest
    assert claim.get("apiVersion") == "database.kubelings.io/v1alpha1"
    assert claim.get("kind") == "PostgreSQLInstance"
    assert claim.get("metadata", {}).get("name") == "production-postgres-claim"
    assert claim.get("metadata", {}).get("namespace") == "production"
    spec = claim.get("spec", {})
    params = spec.get("parameters", {})
    assert params.get("storageGB") == 100
    assert params.get("engineVersion") == "16.1"
    selector = spec.get("compositionSelector", {}).get("matchLabels", {})
    assert selector.get("provider") == "aws"
    assert selector.get("db") == "postgres"
    secret_ref = spec.get("writeConnectionSecretToRef", {})
    assert secret_ref.get("name") == "production-postgres-conn"

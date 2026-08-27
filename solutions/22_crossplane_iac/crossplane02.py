"""
Solution: crossplane02.py
Topic: Crossplane - Composition and Field Path Transforms
"""


def build_composition() -> dict:
    return {
        "apiVersion": "apiextensions.crossplane.io/v1",
        "kind": "Composition",
        "metadata": {
            "name": "postgres-aws-composition",
            "labels": {
                "provider": "aws",
                "db": "postgres",
            },
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
                            },
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
                },
            ],
        },
    }


def verify():
    comp = build_composition()
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

    print("✓ Crossplane Composition and field transforms successfully validated!")


if __name__ == "__main__":
    verify()

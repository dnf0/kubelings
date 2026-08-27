"""
Solution: crossplane01.py
Topic: Crossplane - CompositeResourceDefinition (XRD)
"""


def build_xrd() -> dict:
    return {
        "apiVersion": "apiextensions.crossplane.io/v1",
        "kind": "CompositeResourceDefinition",
        "metadata": {
            "name": "xpostgresqlinstances.database.kubelings.io",
        },
        "spec": {
            "group": "database.kubelings.io",
            "names": {
                "kind": "XPostgreSQLInstance",
                "plural": "xpostgresqlinstances",
            },
            "claimNames": {
                "kind": "PostgreSQLInstance",
                "plural": "postgresqlinstances",
            },
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
                                                "storageGB": {
                                                    "type": "integer",
                                                },
                                                "engineVersion": {
                                                    "type": "string",
                                                },
                                            },
                                            "required": ["storageGB", "engineVersion"],
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            ],
        },
    }


def verify():
    xrd = build_xrd()
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

    print("✓ Crossplane CompositeResourceDefinition (XRD) successfully validated!")


if __name__ == "__main__":
    verify()

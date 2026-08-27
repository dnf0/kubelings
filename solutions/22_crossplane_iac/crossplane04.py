"""
Solution: crossplane04.py
Topic: Crossplane - Developer Self-Service Claims and Connection Secrets
"""


def build_developer_claim() -> dict:
    return {
        "apiVersion": "database.kubelings.io/v1alpha1",
        "kind": "PostgreSQLInstance",
        "metadata": {
            "name": "production-postgres-claim",
            "namespace": "production",
        },
        "spec": {
            "parameters": {
                "storageGB": 100,
                "engineVersion": "16.1",
            },
            "compositionSelector": {
                "matchLabels": {
                    "provider": "aws",
                    "db": "postgres",
                },
            },
            "writeConnectionSecretToRef": {
                "name": "production-postgres-conn",
            },
        },
    }


def verify():
    claim = build_developer_claim()
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

    print("✓ Developer Crossplane Claim and Connection Secret successfully validated!")


if __name__ == "__main__":
    verify()

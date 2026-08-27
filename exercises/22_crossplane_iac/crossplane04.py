"""
Exercise: crossplane04.py
Topic: Crossplane - Developer Self-Service Claims and Connection Secrets

Task:
Define an application-level Developer Claim requesting a PostgreSQL instance:
1. 'apiVersion': 'database.kubelings.io/v1alpha1', 'kind': 'PostgreSQLInstance'
2. Named 'production-postgres-claim' in namespace 'production'
3. 'spec.parameters':
   - 'storageGB': 100
   - 'engineVersion': '16.1'
4. 'spec.compositionSelector':
   - 'matchLabels': {'provider': 'aws', 'db': 'postgres'}
5. 'spec.writeConnectionSecretToRef':
   - 'name': 'production-postgres-conn'
"""

import yaml


def build_developer_claim() -> dict:
    # TODO: Define and return developer claim manifest
    return {}


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

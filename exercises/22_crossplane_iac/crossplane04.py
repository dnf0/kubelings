"""
Exercise: crossplane04.py
Topic: Crossplane - Developer Self-Service Claims and Connection Secrets

Context & Why:
Self-service developer workflows are central to internal developer platforms (IDP). Application
teams need to provision databases, caches, and object storage directly from their application
namespaces without opening IT tickets or managing raw cloud credentials.

Crossplane implements this via composite resource Claims (XRCs):
- Application developers author a namespace-scoped Claim (e.g. `PostgreSQLInstance` in namespace `production`).
- The claim uses `compositionSelector.matchLabels` to select an appropriate composition
  (e.g. matching `provider: aws, db: postgres` for AWS RDS).
- Upon successful provisioning, Crossplane dynamically generates a Kubernetes `Secret` containing
  connection strings, endpoints, usernames, and passwords directly into the developer's namespace
  (`spec.writeConnectionSecretToRef.name`), enabling application pods to mount credentials immediately.

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
    # TODO: Define and return the developer Claim manifest requesting database resources and specifying the output connection secret.
    # WHY: Claims empower application developers to self-service cloud infrastructure directly within their application namespaces,
    #      automatically receiving securely generated connection credentials in Kubernetes Secrets without requiring direct cloud console or IAM access.
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

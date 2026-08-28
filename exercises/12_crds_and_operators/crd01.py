"""
Exercise: exercises/12_crds_and_operators/crd01.py
Topic: CustomResourceDefinition (CRD) Schema

Context & Why:
CustomResourceDefinitions (CRDs) extend the Kubernetes API with domain-specific resources (such as
databases, queues, or backup schedules) managed like native Kubernetes objects. In production, defining
a strict OpenAPI v3 validation schema (`openAPIV3Schema`) is vital. Structural schemas allow the API server
to validate field types, enforce required fields, validate enumerated strings, and reject out-of-bounds
numerical values at admission time before persisting objects to etcd, preventing malformed CR manifests
from causing controller runtime crashes.

Instructions:
1. Define a CustomResourceDefinition 'databases.database.example.com':
   - apiVersion: apiextensions.k8s.io/v1
   - kind: CustomResourceDefinition
   - metadata.name: 'databases.database.example.com'
   - spec:
     - group: 'database.example.com'
     - scope: 'Namespaced'
     - names:
       - plural: 'databases'
       - singular: 'database'
       - kind: 'Database'
       - shortNames: ['db']
     - versions:
       - name: 'v1alpha1'
         served: true
         storage: true
         schema:
           openAPIV3Schema:
             type: object
             properties:
               spec:
                 type: object
                 required: ['engine', 'version', 'replicas']
                 properties:
                   engine:
                     type: string
                     enum: ['postgres', 'mysql', 'redis']
                   version:
                     type: string
                   replicas:
                     type: integer
                     minimum: 1
                     maximum: 5
                   storageGB:
                     type: integer
                     minimum: 10
"""

import yaml

from kubelings.validator import validate_manifest

CRD_MANIFEST = """
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: databases.database.example.com
spec:
  # TODO: Define the API group 'database.example.com'.
  # WHY: Namespaces the custom API under your organization's domain to avoid collision with core APIs.
  group: ???
  # TODO: Set the CRD scope to 'Namespaced'.
  # WHY: Ensures instances of Database CRs are created and isolated within individual namespaces.
  scope: ???
  names:
    plural: databases
    singular: database
    kind: Database
    shortNames:
    - db
  versions:
  - name: v1alpha1
    # TODO: Enable served flag (boolean true).
    # WHY: Instructs the API server to expose this version endpoint to REST clients.
    served: ???
    # TODO: Enable storage flag (boolean true).
    # WHY: Designates v1alpha1 as the underlying schema version stored in etcd.
    storage: ???
    schema:
      openAPIV3Schema:
        type: object
        properties:
          spec:
            type: object
            required:
            - engine
            - version
            - replicas
            properties:
              engine:
                type: string
                enum:
                - postgres
                - mysql
                - redis
              version:
                type: string
              replicas:
                type: integer
                minimum: 1
                # TODO: Set maximum allowed replicas to 5.
                # WHY: Validates replica counts at the API boundary, rejecting excessive resource requests.
                maximum: ???
              storageGB:
                type: integer
                # TODO: Set minimum allowed storageGB to 10.
                # WHY: Prevents creating databases with insufficient disk allocation.
                minimum: ???
"""


def verify():
    manifest = yaml.safe_load(CRD_MANIFEST)
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

    print("✓ crd01 passed!")


if __name__ == "__main__":
    verify()

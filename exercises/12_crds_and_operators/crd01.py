"""
Exercise: exercises/12_crds_and_operators/crd01.py
Topic: CustomResourceDefinition (CRD) Schema

Instructions:
CustomResourceDefinitions (CRDs) allow developers to extend the Kubernetes API
with custom objects. The OpenAPI v3 schema validation ensures that any custom
resource created complies with type and constraint specifications.

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

# I AM NOT DONE

import yaml
from kubelings.validator import validate_manifest

CRD_MANIFEST = """
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: databases.database.example.com
spec:
  group: ???
  scope: ???
  names:
    plural: databases
    singular: database
    kind: Database
    shortNames:
    - db
  versions:
  - name: v1alpha1
    served: ???
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
                maximum: ???
              storageGB:
                type: integer
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

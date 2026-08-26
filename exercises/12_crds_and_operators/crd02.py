"""
Exercise: exercises/12_crds_and_operators/crd02.py
Topic: CRD Subresources & Printer Columns

Instructions:
Kubernetes CustomResourceDefinitions can enable subresources and custom printer
columns:
1. `subresources.status: {}` enables the `/status` subresource, preventing spec
   mutations when updating status and enabling granular RBAC.
2. `subresources.scale` integrates the custom resource with `kubectl scale` and HPA.
3. `additionalPrinterColumns` customizes the fields displayed by `kubectl get`.

Define a CustomResourceDefinition 'backups.backup.example.com':
- apiVersion: apiextensions.k8s.io/v1
- kind: CustomResourceDefinition
- metadata.name: backups.backup.example.com
- spec:
  - group: backup.example.com
  - scope: Namespaced
  - names:
    - plural: backups
    - singular: backup
    - kind: Backup
  - versions:
    - name: v1
      served: true
      storage: true
      subresources:
        status: {}
        scale:
          specReplicasPath: .spec.replicas
          statusReplicasPath: .status.replicas
      additionalPrinterColumns:
      - name: Schedule
        type: string
        jsonPath: .spec.schedule
      - name: Status
        type: string
        jsonPath: .status.phase
      - name: Age
        type: date
        jsonPath: .metadata.creationTimestamp
      schema:
        openAPIV3Schema:
          type: object
          properties:
            spec:
              type: object
            status:
              type: object
"""

# I AM NOT DONE

import yaml

from kubelings.validator import validate_manifest

CRD_MANIFEST = """
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: backups.backup.example.com
spec:
  group: backup.example.com
  scope: Namespaced
  names:
    plural: backups
    singular: backup
    kind: Backup
  versions:
  - name: v1
    served: true
    storage: true
    subresources:
      status: {}
      scale:
        specReplicasPath: ???
        statusReplicasPath: ???
    additionalPrinterColumns:
    - name: Schedule
      type: string
      jsonPath: ???
    - name: Status
      type: string
      jsonPath: ???
    - name: Age
      type: date
      jsonPath: .metadata.creationTimestamp
    schema:
      openAPIV3Schema:
        type: object
        properties:
          spec:
            type: object
          status:
            type: object
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
    assert metadata.get("name") == "backups.backup.example.com"

    spec = manifest.get("spec", {})
    assert spec.get("group") == "backup.example.com"
    assert spec.get("names", {}).get("kind") == "Backup"

    versions = spec.get("versions", [])
    assert len(versions) == 1
    v = versions[0]
    assert v.get("name") == "v1"

    subresources = v.get("subresources", {})
    assert "status" in subresources, "Must define 'status: {}' subresource"
    scale = subresources.get("scale", {})
    assert scale.get("specReplicasPath") == ".spec.replicas"
    assert scale.get("statusReplicasPath") == ".status.replicas"

    columns = v.get("additionalPrinterColumns", [])
    assert len(columns) == 3, "Must define 3 additionalPrinterColumns"

    col_map = {c.get("name"): c for c in columns}
    assert "Schedule" in col_map
    assert col_map["Schedule"].get("type") == "string"
    assert col_map["Schedule"].get("jsonPath") == ".spec.schedule"

    assert "Status" in col_map
    assert col_map["Status"].get("type") == "string"
    assert col_map["Status"].get("jsonPath") == ".status.phase"

    assert "Age" in col_map
    assert col_map["Age"].get("type") == "date"
    assert col_map["Age"].get("jsonPath") == ".metadata.creationTimestamp"

    print("✓ crd02 passed!")


if __name__ == "__main__":
    verify()

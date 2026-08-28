"""
Exercise: exercises/12_crds_and_operators/crd02.py
Topic: CRD Subresources & Printer Columns

Context & Why:
CustomResourceDefinitions become first-class cluster primitives when equipped with subresources
and printer column definitions. Enabling `subresources.status: {}` creates an isolated `/status`
endpoint, ensuring controller status updates cannot inadvertently mutate user-managed `spec` fields
and allowing fine-grained RBAC for operator service accounts. Enabling `subresources.scale` exposes
JSONPath mappings (`specReplicasPath`, `statusReplicasPath`) to core autoscaling systems (HPA and
`kubectl scale`). Furthermore, `additionalPrinterColumns` renders domain-specific metadata (such as
backup schedule and phase) directly in standard `kubectl get` commands, dramatically improving operator UX.

Instructions:
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
        # TODO: Set specReplicasPath to '.spec.replicas'.
        # WHY: Maps the desired replica count field in the custom resource to HPA and kubectl scale.
        specReplicasPath: ???
        # TODO: Set statusReplicasPath to '.status.replicas'.
        # WHY: Maps the observed replica count field in status for controller reconciliation.
        statusReplicasPath: ???
    additionalPrinterColumns:
    - name: Schedule
      type: string
      # TODO: Set jsonPath for Schedule column to '.spec.schedule'.
      # WHY: Extracts the cron schedule expression from spec to display in kubectl get output.
      jsonPath: ???
    - name: Status
      type: string
      # TODO: Set jsonPath for Status column to '.status.phase'.
      # WHY: Surfaces the high-level operational status (e.g. Running, Completed, Failed) to cluster operators.
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

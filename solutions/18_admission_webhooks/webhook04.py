"""
Chapter 18: Advanced Admission Webhooks & Dynamic Interception
Exercise 18.4: CRD Conversion Webhook Strategy (Solution)
"""

from typing import Any, Dict
import yaml


def get_crd_conversion_manifest() -> Dict[str, Any]:
    manifest_yaml = """
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: appdeployments.example.com
spec:
  group: example.com
  names:
    kind: AppDeployment
    plural: appdeployments
    singular: appdeployment
  scope: Namespaced
  conversion:
    strategy: Webhook
    webhook:
      conversionReviewVersions: ["v1", "v1alpha1"]
      clientConfig:
        service:
          namespace: custom-operators
          name: app-converter-svc
          path: /crdconvert
  versions:
    - name: v1
      served: true
      storage: true
      schema:
        openAPIV3Schema:
          type: object
    - name: v1alpha1
      served: true
      storage: false
      schema:
        openAPIV3Schema:
          type: object
"""
    return yaml.safe_load(manifest_yaml)


if __name__ == "__main__":
    crd = get_crd_conversion_manifest()
    assert crd.get("kind") == "CustomResourceDefinition"
    conversion = crd.get("spec", {}).get("conversion", {})
    assert conversion.get("strategy") == "Webhook"
    assert "v1" in conversion.get("webhook", {}).get("conversionReviewVersions", [])
    print("✓ CRD conversion webhook validation passed!")

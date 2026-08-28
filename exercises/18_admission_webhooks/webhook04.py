"""
Chapter 18: Advanced Admission Webhooks & Dynamic Interception
Exercise 18.4: CRD Conversion Webhook Strategy

Context & Why:
CustomResourceDefinitions (CRDs) frequently undergo API evolution as platforms mature,
introducing breaking changes between versions (e.g. migrating from `v1alpha1` to `v1`).
However, in production environments, multiple API versions must be served simultaneously:
older client controllers continue writing `v1alpha1` manifests while new components adopt `v1`.

Kubernetes supports multi-version CRDs via CRD Conversion Webhooks (`conversion.strategy: Webhook`).
When a client queries or submits an older resource version, the kube-apiserver invokes the
registered conversion service (`app-converter-svc` at `/crdconvert`) with a `ConversionReview`
request. The converter dynamically converts the custom resource between schema representations
in memory while persisting only the canonical storage version (`storage: true`), ensuring zero-downtime
API migrations without schema fragmentation.

Task:
Fix the CustomResourceDefinition manifest function to return the parsed manifest dictionary
specifying a Webhook conversion strategy for migrating between v1alpha1 and v1 of 'AppDeployment'.
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
    # TODO: Parse and return the CustomResourceDefinition manifest dictionary (e.g., using yaml.safe_load).
    # WHY: CRD conversion webhooks enable multi-version custom API evolution by translating custom resource payloads
    #      on the fly between different schema representations during API server read/write operations.
    return {}


if __name__ == "__main__":
    crd = get_crd_conversion_manifest()
    assert crd.get("kind") == "CustomResourceDefinition"
    conversion = crd.get("spec", {}).get("conversion", {})
    assert conversion.get("strategy") == "Webhook"
    assert "v1" in conversion.get("webhook", {}).get("conversionReviewVersions", [])
    print("✓ CRD conversion webhook validation passed!")

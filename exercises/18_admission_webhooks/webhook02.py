"""
Chapter 18: Advanced Admission Webhooks & Dynamic Interception
Exercise 18.2: ValidatingWebhookConfiguration Manifest

Fix the ValidatingWebhookConfiguration manifest to validate namespace and pod
updates with URL endpoint targets and namespaceSelectors.
"""

from typing import Any, Dict

import yaml


def get_validating_webhook_manifest() -> Dict[str, Any]:
    manifest_yaml = """
apiVersion: admissionregistration.k8s.io/v1
kind: ValidatingWebhookConfiguration
metadata:
  name: security-validator
webhooks:
  - name: validate-security.kubelings.io
    rules:
      - apiGroups: [""]
        apiVersions: ["v1"]
        operations: ["CREATE", "UPDATE"]
        resources: ["pods"]
        scope: "Namespaced"
    clientConfig:
      service:
        namespace: security-system
        name: validator-svc
        path: /validate
      caBundle: "QWxhZGRpbjpvcGVuIHNlc2FtZQ=="
    admissionReviewVersions: ["v1"]
    sideEffects: None
    failurePolicy: Ignore
    namespaceSelector:
      matchExpressions:
        - key: environment
          operator: In
          values: ["prod", "stage"]
"""
    # Fix the return dictionary
    return {}


if __name__ == "__main__":
    hook = get_validating_webhook_manifest()
    assert hook.get("kind") == "ValidatingWebhookConfiguration"
    assert hook.get("apiVersion") == "admissionregistration.k8s.io/v1"
    webhooks = hook.get("webhooks", [])
    assert len(webhooks) == 1
    assert "prod" in webhooks[0]["namespaceSelector"]["matchExpressions"][0]["values"]
    print("✓ Validating webhook configuration validation passed!")

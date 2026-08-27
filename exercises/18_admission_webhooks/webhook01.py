# I AM NOT DONE
"""
Chapter 18: Advanced Admission Webhooks & Dynamic Interception
Exercise 18.1: MutatingWebhookConfiguration Manifest

Fix the MutatingWebhookConfiguration manifest to route pod creation requests
to the admission controller service 'mutator-svc' in 'webhook-system'.
"""

from typing import Any, Dict

import yaml


def get_mutating_webhook_manifest() -> Dict[str, Any]:
    manifest_yaml = """
apiVersion: admissionregistration.k8s.io/v1
kind: MutatingWebhookConfiguration
metadata:
  name: pod-defaults-mutator
webhooks:
  - name: mutate-pods.kubelings.io
    rules:
      - apiGroups: [""]
        apiVersions: ["v1"]
        operations: ["CREATE"]
        resources: ["pods"]
        scope: "Namespaced"
    clientConfig:
      service:
        namespace: webhook-system
        name: mutator-svc
        path: /mutate
        port: 443
      caBundle: "QWxhZGRpbjpvcGVuIHNlc2FtZQ=="
    admissionReviewVersions: ["v1"]
    sideEffects: None
    timeoutSeconds: 5
    failurePolicy: Fail
"""
    # Fix the return dictionary
    return {}


if __name__ == "__main__":
    hook = get_mutating_webhook_manifest()
    assert hook.get("kind") == "MutatingWebhookConfiguration"
    assert hook.get("apiVersion") == "admissionregistration.k8s.io/v1"
    webhooks = hook.get("webhooks", [])
    assert len(webhooks) == 1
    assert webhooks[0]["failurePolicy"] == "Fail"
    print("✓ Mutating webhook configuration validation passed!")

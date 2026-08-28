"""
Chapter 18: Advanced Admission Webhooks & Dynamic Interception
Exercise 18.2: ValidatingWebhookConfiguration Manifest

Context & Why:
Validating admission webhooks execute as the final security gate before any object is written
to etcd. Unlike mutating webhooks, validating webhooks cannot alter the resource payload; they
only emit a binary allow/deny decision along with a human-readable rejection message.

In enterprise platforms, not all namespaces require the same strict validation, and non-critical
validations should not cause cluster outages if the validator service goes down.
A `ValidatingWebhookConfiguration` leverages `namespaceSelector` (e.g. `matchExpressions` targeting
`environment in [prod, stage]`) to scope validation strictly to critical environments.
Setting `failurePolicy: Ignore` ensures fail-open resilience for non-blocking advisory policies,
preventing cluster admission bottlenecks during webhook outages.

Task:
Fix the ValidatingWebhookConfiguration manifest function to return the parsed manifest dictionary
validating Pod CREATE and UPDATE requests in 'prod' and 'stage' namespaces.
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
    # TODO: Parse and return the ValidatingWebhookConfiguration manifest dictionary (e.g., using yaml.safe_load).
    # WHY: ValidatingWebhookConfigurations enforce targeted custom admission guardrails across specific
    #      environments using namespaceSelectors, preventing non-compliant resource submissions.
    return {}


if __name__ == "__main__":
    hook = get_validating_webhook_manifest()
    assert hook.get("kind") == "ValidatingWebhookConfiguration"
    assert hook.get("apiVersion") == "admissionregistration.k8s.io/v1"
    webhooks = hook.get("webhooks", [])
    assert len(webhooks) == 1
    assert "prod" in webhooks[0]["namespaceSelector"]["matchExpressions"][0]["values"]
    print("✓ Validating webhook configuration validation passed!")

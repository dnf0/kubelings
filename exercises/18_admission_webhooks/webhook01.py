"""
Chapter 18: Advanced Admission Webhooks & Dynamic Interception
Exercise 18.1: MutatingWebhookConfiguration Manifest

Context & Why:
Kubernetes admission processing occurs in two sequential phases: mutating admission
followed by validating admission. Mutating webhooks allow platform operators to intercept
API requests before object schema validation and persistence to etcd, dynamically modifying
or injecting configurations (such as sidecar containers, environment variables, or security contexts).

A `MutatingWebhookConfiguration` instructs the kube-apiserver to send an `AdmissionReview`
payload over TLS to an internal Service (`mutator-svc` in `webhook-system`). Setting `failurePolicy: Fail`
enforces fail-closed security semantics: if the webhook endpoint is unreachable or fails to respond
within `timeoutSeconds: 5`, the pod creation request is blocked, preventing un-mutated workloads from
bypassing organizational standards.

Task:
Fix the MutatingWebhookConfiguration manifest function to return the parsed manifest dictionary
routing namespaced pod CREATE operations to the admission controller service 'mutator-svc'.
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
    # TODO: Parse and return the MutatingWebhookConfiguration manifest dictionary (e.g., using yaml.safe_load).
    # WHY: MutatingWebhookConfigurations register dynamic admission controllers with the API server, enabling
    #      transparent workload mutation and policy enforcement prior to resource validation and storage.
    return {}


if __name__ == "__main__":
    hook = get_mutating_webhook_manifest()
    assert hook.get("kind") == "MutatingWebhookConfiguration"
    assert hook.get("apiVersion") == "admissionregistration.k8s.io/v1"
    webhooks = hook.get("webhooks", [])
    assert len(webhooks) == 1
    assert webhooks[0]["failurePolicy"] == "Fail"
    print("✓ Mutating webhook configuration validation passed!")

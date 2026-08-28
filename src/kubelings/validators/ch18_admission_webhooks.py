"""
Validators for Chapter 18: Advanced Admission Webhooks
"""

import base64
import json
from typing import Any, Dict

import yaml

from kubelings.validators import register_validator


def get_mutating_webhook_manifest() -> Dict[str, Any]:
    manifest_yaml = '\napiVersion: admissionregistration.k8s.io/v1\nkind: MutatingWebhookConfiguration\nmetadata:\n  name: pod-defaults-mutator\nwebhooks:\n  - name: mutate-pods.kubelings.io\n    rules:\n      - apiGroups: [""]\n        apiVersions: ["v1"]\n        operations: ["CREATE"]\n        resources: ["pods"]\n        scope: "Namespaced"\n    clientConfig:\n      service:\n        namespace: webhook-system\n        name: mutator-svc\n        path: /mutate\n        port: 443\n      caBundle: "QWxhZGRpbjpvcGVuIHNlc2FtZQ=="\n    admissionReviewVersions: ["v1"]\n    sideEffects: None\n    timeoutSeconds: 5\n    failurePolicy: Fail\n'
    return yaml.safe_load(manifest_yaml)


@register_validator("webhook01")
def validate_webhook01(manifest: Any, raw_yaml: str = "") -> None:
    hook = manifest
    assert hook.get("kind") == "MutatingWebhookConfiguration"
    assert hook.get("apiVersion") == "admissionregistration.k8s.io/v1"
    webhooks = hook.get("webhooks", [])
    assert len(webhooks) == 1
    assert webhooks[0]["failurePolicy"] == "Fail"


def get_validating_webhook_manifest() -> Dict[str, Any]:
    manifest_yaml = '\napiVersion: admissionregistration.k8s.io/v1\nkind: ValidatingWebhookConfiguration\nmetadata:\n  name: security-validator\nwebhooks:\n  - name: validate-security.kubelings.io\n    rules:\n      - apiGroups: [""]\n        apiVersions: ["v1"]\n        operations: ["CREATE", "UPDATE"]\n        resources: ["pods"]\n        scope: "Namespaced"\n    clientConfig:\n      service:\n        namespace: security-system\n        name: validator-svc\n        path: /validate\n      caBundle: "QWxhZGRpbjpvcGVuIHNlc2FtZQ=="\n    admissionReviewVersions: ["v1"]\n    sideEffects: None\n    failurePolicy: Ignore\n    namespaceSelector:\n      matchExpressions:\n        - key: environment\n          operator: In\n          values: ["prod", "stage"]\n'
    return yaml.safe_load(manifest_yaml)


@register_validator("webhook02")
def validate_webhook02(manifest: Any, raw_yaml: str = "") -> None:
    hook = manifest
    assert hook.get("kind") == "ValidatingWebhookConfiguration"
    assert hook.get("apiVersion") == "admissionregistration.k8s.io/v1"
    webhooks = hook.get("webhooks", [])
    assert len(webhooks) == 1
    assert "prod" in webhooks[0]["namespaceSelector"]["matchExpressions"][0]["values"]


def build_admission_review_response(uid: str) -> Dict[str, Any]:
    patch = [
        {
            "op": "add",
            "path": "/spec/containers/-",
            "value": {"name": "telemetry-agent", "image": "otel/opentelemetry-collector:latest"},
        }
    ]
    patch_bytes = json.dumps(patch).encode("utf-8")
    patch_b64 = base64.b64encode(patch_bytes).decode("utf-8")
    return {
        "apiVersion": "admission.k8s.io/v1",
        "kind": "AdmissionReview",
        "response": {"uid": uid, "allowed": True, "patchType": "JSONPatch", "patch": patch_b64},
    }


@register_validator("webhook03")
def validate_webhook03(manifest: Any, raw_yaml: str = "") -> None:
    resp = manifest
    assert resp.get("apiVersion") == "admission.k8s.io/v1"
    assert resp.get("kind") == "AdmissionReview"
    res = resp.get("response", {})
    assert res.get("uid") == "test-uid-123"
    assert res.get("allowed") is True
    assert res.get("patchType") == "JSONPatch"
    assert "patch" in res


def get_crd_conversion_manifest() -> Dict[str, Any]:
    manifest_yaml = '\napiVersion: apiextensions.k8s.io/v1\nkind: CustomResourceDefinition\nmetadata:\n  name: appdeployments.example.com\nspec:\n  group: example.com\n  names:\n    kind: AppDeployment\n    plural: appdeployments\n    singular: appdeployment\n  scope: Namespaced\n  conversion:\n    strategy: Webhook\n    webhook:\n      conversionReviewVersions: ["v1", "v1alpha1"]\n      clientConfig:\n        service:\n          namespace: custom-operators\n          name: app-converter-svc\n          path: /crdconvert\n  versions:\n    - name: v1\n      served: true\n      storage: true\n      schema:\n        openAPIV3Schema:\n          type: object\n    - name: v1alpha1\n      served: true\n      storage: false\n      schema:\n        openAPIV3Schema:\n          type: object\n'
    return yaml.safe_load(manifest_yaml)


@register_validator("webhook04")
def validate_webhook04(manifest: Any, raw_yaml: str = "") -> None:
    crd = manifest
    assert crd.get("kind") == "CustomResourceDefinition"
    conversion = crd.get("spec", {}).get("conversion", {})
    assert conversion.get("strategy") == "Webhook"
    assert "v1" in conversion.get("webhook", {}).get("conversionReviewVersions", [])

"""
Exercise: exercises/12_crds_and_operators/crd04.py
Topic: Dynamic Admission Webhooks

Context & Why:
Dynamic Admission Control allows cluster administrators to intercept, validate, or mutate API requests
before objects are persisted to etcd. While standard RBAC controls *who* can make a request, Admission
Webhooks control *what* content is permissible within the request payload. `ValidatingWebhookConfiguration`
registers HTTPS endpoints that receive `AdmissionReview` JSON payloads from the API server. In security-conscious
enterprises, validating webhooks enforce strict organizational policies—such as rejecting any container requesting
root execution (`runAsUser: 0`) or privileged capability overrides—returning descriptive 403 Forbidden responses.

Instructions:
Kubernetes Dynamic Admission Webhooks intercept API requests prior to persistence
in etcd. Validating Webhooks evaluate custom policies and can accept or reject
the operation with custom status codes and messages.

1. Define a ValidatingWebhookConfiguration 'pod-security-webhook':
   - apiVersion: admissionregistration.k8s.io/v1
   - metadata.name: 'pod-security-webhook'
   - webhooks:
     - name: 'validate-security.example.com'
     - admissionReviewVersions: ['v1']
     - sideEffects: 'None'
     - rules:
       - operations: ['CREATE', 'UPDATE']
         apiGroups: ['']
         apiVersions: ['v1']
         resources: ['pods']
     - clientConfig:
       - service:
           name: 'security-webhook-svc'
           namespace: 'kube-system'
           path: '/validate-pods'
           port: 443

2. Implement `handle_admission_review(review: dict) -> dict`:
   - Inspects the pod spec in `review["request"]["object"]`.
   - Rejects the request (`allowed: False`, `code: 403`, `message: "Root or privileged containers are forbidden."`)
     if:
     - Any container has `securityContext.privileged: True`, OR
     - Pod and container fail non-root checks (i.e. not `runAsNonRoot: True` and not `runAsUser > 0`).
   - Otherwise, accepts the request (`allowed: True`).
"""

from typing import Any, Dict

import yaml

from kubelings.validator import validate_manifest

WEBHOOK_CONFIG_MANIFEST = """
apiVersion: admissionregistration.k8s.io/v1
kind: ValidatingWebhookConfiguration
metadata:
  name: pod-security-webhook
webhooks:
- name: validate-security.example.com
  admissionReviewVersions:
  - v1
  # TODO: Declare sideEffects as 'None'.
  # WHY: Asserts the webhook does not mutate out-of-band state, enabling safe dry-run calls.
  sideEffects: ???
  rules:
  - operations:
    - CREATE
    - UPDATE
    apiGroups:
    - ""
    apiVersions:
    - v1
    # TODO: Intercept 'pods' resources.
    # WHY: Targets pod creation and mutation events for security validation.
    resources:
    - ???
  clientConfig:
    service:
      name: security-webhook-svc
      namespace: kube-system
      # TODO: Set the webhook HTTPS service path to '/validate-pods'.
      # WHY: Routes API server admission evaluation requests to the handler endpoint.
      path: ???
      port: 443
"""


def handle_admission_review(review: Dict[str, Any]) -> Dict[str, Any]:
    req = review.get("request", {})
    uid = req.get("uid", "")

    # TODO: Implement admission review validation logic inspecting container securityContext (reject privileged or root containers with HTTP 403).
    # WHY: Dynamic admission webhooks enforce runtime compliance invariants on raw manifests before admission into etcd.
    return {
        "apiVersion": "admission.k8s.io/v1",
        "kind": "AdmissionReview",
        "response": {
            "uid": uid,
            "allowed": False,
        },
    }


def verify():
    manifest = yaml.safe_load(WEBHOOK_CONFIG_MANIFEST)
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(
        manifest,
        expected_kind="ValidatingWebhookConfiguration",
        expected_api_version="admissionregistration.k8s.io/v1",
    )

    metadata = manifest.get("metadata", {})
    assert metadata.get("name") == "pod-security-webhook"

    webhooks = manifest.get("webhooks", [])
    assert len(webhooks) == 1
    wh = webhooks[0]
    assert wh.get("name") == "validate-security.example.com"
    assert wh.get("sideEffects") == "None"
    assert wh.get("admissionReviewVersions") == ["v1"]

    rule = wh.get("rules", [])[0]
    assert set(rule.get("operations", [])) == {"CREATE", "UPDATE"}
    assert rule.get("resources") == ["pods"]

    svc = wh.get("clientConfig", {}).get("service", {})
    assert svc.get("name") == "security-webhook-svc"
    assert svc.get("namespace") == "kube-system"
    assert svc.get("path") == "/validate-pods"
    assert svc.get("port") == 443

    # Test Webhook Handler - Scenario 1: Privileged container -> REJECT (403)
    bad_req_privileged = {
        "request": {
            "uid": "req-111",
            "object": {
                "spec": {
                    "containers": [
                        {
                            "name": "app",
                            "securityContext": {"privileged": True, "runAsNonRoot": True},
                        }
                    ]
                }
            },
        }
    }
    resp1 = handle_admission_review(bad_req_privileged)
    assert resp1["response"]["uid"] == "req-111"
    assert resp1["response"]["allowed"] is False
    assert resp1["response"].get("status", {}).get("code") == 403

    # Test Webhook Handler - Scenario 2: Root container (no runAsNonRoot) -> REJECT (403)
    bad_req_root = {
        "request": {
            "uid": "req-222",
            "object": {"spec": {"containers": [{"name": "app", "image": "nginx"}]}},
        }
    }
    resp2 = handle_admission_review(bad_req_root)
    assert resp2["response"]["uid"] == "req-222"
    assert resp2["response"]["allowed"] is False
    assert resp2["response"].get("status", {}).get("code") == 403

    # Test Webhook Handler - Scenario 3: Valid non-root pod -> ALLOW
    good_req = {
        "request": {
            "uid": "req-333",
            "object": {
                "spec": {
                    "securityContext": {"runAsNonRoot": True, "runAsUser": 10001},
                    "containers": [
                        {
                            "name": "app",
                            "image": "nginx:alpine",
                            "securityContext": {"allowPrivilegeEscalation": False},
                        }
                    ],
                }
            },
        }
    }
    resp3 = handle_admission_review(good_req)
    assert resp3["response"]["uid"] == "req-333"
    assert resp3["response"]["allowed"] is True

    print("✓ crd04 passed!")


if __name__ == "__main__":
    verify()

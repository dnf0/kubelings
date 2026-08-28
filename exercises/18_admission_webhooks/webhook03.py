"""
Chapter 18: Advanced Admission Webhooks & Dynamic Interception
Exercise 18.3: Dynamic Sidecar Injection AdmissionReview Response

Context & Why:
When a Kubernetes mutating admission webhook intercepts an API request, the API server
expects a structured JSON response conforming to the `admission.k8s.io/v1` `AdmissionReview`
schema. To modify the incoming resource, the webhook response must declare `allowed: true`,
`patchType: "JSONPatch"`, and supply a base64-encoded array of RFC 6902 JSON patch operations.

In sidecar injection workflows (e.g. Istio sidecars, Vault agents, OpenTelemetry collectors),
the webhook server crafts an RFC 6902 "add" operation on `/spec/containers/-` to append the
sidecar container spec to the Pod. Generating a correctly structured AdmissionReview response
ensures that the API server can decode and apply the patch seamlessly before persisting the Pod.

Task:
Fix `build_admission_review_response(uid)` to return a valid `AdmissionReview` dictionary with
`apiVersion: "admission.k8s.io/v1"`, `kind: "AdmissionReview"`, and response fields containing
the provided `uid`, `allowed: True`, `patchType: "JSONPatch"`, and the base64-encoded `patch_b64`.
"""

import base64
import json
from typing import Any, Dict


def build_admission_review_response(uid: str) -> Dict[str, Any]:
    patch = [
        {
            "op": "add",
            "path": "/spec/containers/-",
            "value": {
                "name": "telemetry-agent",
                "image": "otel/opentelemetry-collector:latest",
            },
        }
    ]
    patch_bytes = json.dumps(patch).encode("utf-8")
    patch_b64 = base64.b64encode(patch_bytes).decode("utf-8")

    # TODO: Construct and return the dictionary representation of an AdmissionReview v1 response
    #       containing uid, allowed status (True), patchType ('JSONPatch'), and the base64-encoded patch.
    # WHY: The Kubernetes API server expects mutating webhook responses to adhere to the AdmissionReview v1 schema
    #      with mutations encoded as base64 RFC 6902 JSONPatch operations.
    return {}


if __name__ == "__main__":
    resp = build_admission_review_response("test-uid-123")
    assert resp.get("apiVersion") == "admission.k8s.io/v1"
    assert resp.get("kind") == "AdmissionReview"
    res = resp.get("response", {})
    assert res.get("uid") == "test-uid-123"
    assert res.get("allowed") is True
    assert res.get("patchType") == "JSONPatch"
    assert "patch" in res
    print("✓ AdmissionReview response validation passed!")

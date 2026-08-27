# I AM NOT DONE
"""
Chapter 18: Advanced Admission Webhooks & Dynamic Interception
Exercise 18.3: Dynamic Sidecar Injection AdmissionReview Response

Fix the AdmissionReview response function to generate a valid base64-encoded
JSONPatch adding a telemetry sidecar container to intercepted pods.
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

    # Fix the AdmissionReview response structure
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

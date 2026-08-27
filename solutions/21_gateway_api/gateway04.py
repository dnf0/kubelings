"""
Solution: gateway04.py
Topic: Gateway API - ReferenceGrant Cross-Namespace Security
"""


def build_reference_grant() -> dict:
    return {
        "apiVersion": "gateway.networking.k8s.io/v1beta1",
        "kind": "ReferenceGrant",
        "metadata": {
            "name": "allow-edge-to-backend",
            "namespace": "backend",
        },
        "spec": {
            "from": [
                {
                    "group": "gateway.networking.k8s.io",
                    "kind": "HTTPRoute",
                    "namespace": "edge",
                },
            ],
            "to": [
                {
                    "group": "",
                    "kind": "Service",
                    "name": "account-service",
                },
            ],
        },
    }


def verify():
    grant = build_reference_grant()
    assert grant.get("apiVersion") in [
        "gateway.networking.k8s.io/v1beta1",
        "gateway.networking.k8s.io/v1alpha2",
    ]
    assert grant.get("kind") == "ReferenceGrant"
    assert grant.get("metadata", {}).get("name") == "allow-edge-to-backend"
    assert grant.get("metadata", {}).get("namespace") == "backend"

    from_list = grant.get("spec", {}).get("from", [])
    assert len(from_list) == 1, f"Expected 1 from entry, found {len(from_list)}"
    f0 = from_list[0]
    assert f0.get("group") == "gateway.networking.k8s.io"
    assert f0.get("kind") == "HTTPRoute"
    assert f0.get("namespace") == "edge"

    to_list = grant.get("spec", {}).get("to", [])
    assert len(to_list) == 1, f"Expected 1 to entry, found {len(to_list)}"
    t0 = to_list[0]
    assert t0.get("group") == "" or t0.get("group") is None
    assert t0.get("kind") == "Service"
    assert t0.get("name") == "account-service"

    print("✓ Gateway API ReferenceGrant cross-namespace authorization successfully validated!")


if __name__ == "__main__":
    verify()

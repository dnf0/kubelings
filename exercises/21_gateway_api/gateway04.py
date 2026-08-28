"""
Exercise: gateway04.py
Topic: Gateway API - ReferenceGrant Cross-Namespace Security

Context & Why:
In multi-tenant Kubernetes clusters, routing traffic across namespace boundaries introduces
significant security risks. If a Gateway or Route in an ingress namespace (such as `infra-gateway`
or `edge`) could arbitrarily forward traffic to any Service in the `backend` namespace without
permission, rogue or compromised routes could bypass network policies and access internal services.

To enforce least-privilege boundary controls, Gateway API introduces `ReferenceGrant`:
- By default, cross-namespace references between Gateways, Routes, and Services are forbidden.
- The administrator or owner of the target namespace (`backend`) creates a `ReferenceGrant` to
  explicitly specify which source namespaces and resource kinds (e.g. `HTTPRoute` in namespace `edge`)
  are authorized to reference specific local resources (e.g. `Service` named `account-service`).
- This establishes bidirectional trust: the Route attempts the reference, and the ReferenceGrant authorizes it.

Task:
Define a ReferenceGrant resource to permit cross-namespace routing:
In Kubernetes Gateway API, a Gateway or Route in namespace 'infra-gateway' or 'edge' cannot forward
traffic to a Service in 'backend' namespace unless the target namespace explicitly grants access via a ReferenceGrant.

1. 'apiVersion': 'gateway.networking.k8s.io/v1beta1', 'kind': 'ReferenceGrant'
2. Named 'allow-edge-to-backend' in namespace 'backend'
3. 'spec.from': Allow from group 'gateway.networking.k8s.io', kind 'HTTPRoute', namespace 'edge'
4. 'spec.to': Grant access to core group '' (or empty string), kind 'Service', name 'account-service'
"""

import yaml


def build_reference_grant() -> dict:
    # TODO: Define and return the ReferenceGrant manifest explicitly authorizing cross-namespace routing from edge HTTPRoutes to the backend Service.
    # WHY: In multi-tenant architectures, cross-namespace references present a security boundary vulnerability; ReferenceGrant enforces
    #      explicit opt-in access control by the target namespace owner before external Gateways or Routes can bind to internal Services.
    return {}


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

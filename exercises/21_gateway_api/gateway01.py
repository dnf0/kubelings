"""
Exercise: gateway01.py
Topic: Gateway API - GatewayClass and Gateway Declaration

Context & Why:
The Kubernetes Gateway API is the modern, role-oriented evolution of Ingress networking.
Traditional Ingress bundled infrastructure provisioning, listener configuration, and routing
into a single monolithic resource, forcing cluster operators and application developers into
conflicting workflows and relying heavily on non-portable vendor annotations.

Gateway API cleanly separates concerns across organizational personas:
- Infrastructure Providers & Platform Engineers define `GatewayClass` resources specifying the
  underlying controller implementation (e.g. Envoy Gateway, Cilium, Istio).
- Cluster Operators instantiate `Gateway` resources to define network entrypoints, ports, protocols,
  and namespace routing boundaries.
- Application Developers attach routing resources (such as `HTTPRoute` or `GRPCRoute`) without
  needing administrative privileges to modify physical listeners or load balancers.

Task:
Define a GatewayClass and a Gateway resource according to the Kubernetes Gateway API standard:
1. The GatewayClass named 'envoy-gateway-class' with controllerName 'gateway.envoyproxy.io/gatewayclass-controller'.
2. The Gateway named 'main-gateway' in namespace 'infra-gateway' referencing 'envoy-gateway-class'.
3. The Gateway must configure an HTTP listener on port 80 named 'http' with protocol 'HTTP' allowing routes from 'Same' namespace.
"""

import yaml


def build_gateway_resources() -> list[dict]:
    # TODO: Define and return a list containing the GatewayClass and Gateway resource manifests.
    # WHY: GatewayClass separates infrastructure provider configuration (managed by platform teams)
    #      from Gateway instances (provisioned by cluster operators), establishing a clean role-oriented
    #      separation of concerns compared to monolithic Ingress resources.
    return []


def verify():
    manifests = build_gateway_resources()
    assert len(manifests) == 2, f"Expected 2 manifests, found {len(manifests)}"

    gc = next((m for m in manifests if m.get("kind") == "GatewayClass"), None)
    assert gc is not None, "Missing GatewayClass manifest"
    assert gc.get("apiVersion") == "gateway.networking.k8s.io/v1"
    assert gc.get("metadata", {}).get("name") == "envoy-gateway-class"
    assert (
        gc.get("spec", {}).get("controllerName") == "gateway.envoyproxy.io/gatewayclass-controller"
    )

    gw = next((m for m in manifests if m.get("kind") == "Gateway"), None)
    assert gw is not None, "Missing Gateway manifest"
    assert gw.get("apiVersion") == "gateway.networking.k8s.io/v1"
    assert gw.get("metadata", {}).get("name") == "main-gateway"
    assert gw.get("metadata", {}).get("namespace") == "infra-gateway"
    assert gw.get("spec", {}).get("gatewayClassName") == "envoy-gateway-class"

    listeners = gw.get("spec", {}).get("listeners", [])
    assert len(listeners) == 1, f"Expected 1 listener, found {len(listeners)}"
    l0 = listeners[0]
    assert l0.get("name") == "http"
    assert l0.get("port") == 80
    assert l0.get("protocol") == "HTTP"
    assert l0.get("allowedRoutes", {}).get("namespaces", {}).get("from") == "Same"

    print("✓ GatewayClass and Gateway successfully validated!")


if __name__ == "__main__":
    verify()

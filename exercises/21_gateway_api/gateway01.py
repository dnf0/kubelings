# I AM NOT DONE
"""
Exercise: gateway01.py
Topic: Gateway API - GatewayClass and Gateway Declaration

Task:
Define a GatewayClass and a Gateway resource according to the Kubernetes Gateway API standard.
1. The GatewayClass named 'envoy-gateway-class' with controllerName 'gateway.envoyproxy.io/gatewayclass-controller'.
2. The Gateway named 'main-gateway' in namespace 'infra-gateway' referencing 'envoy-gateway-class'.
3. The Gateway must configure an HTTP listener on port 80 named 'http' with protocol 'HTTP' allowing routes from 'Same' namespace.
"""

import yaml


def build_gateway_resources() -> list[dict]:
    # TODO: Define and return list containing GatewayClass and Gateway manifests
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

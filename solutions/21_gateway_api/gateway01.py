"""
Solution: gateway01.py
Topic: Gateway API - GatewayClass and Gateway Declaration
"""


def build_gateway_resources() -> list[dict]:
    gateway_class = {
        "apiVersion": "gateway.networking.k8s.io/v1",
        "kind": "GatewayClass",
        "metadata": {
            "name": "envoy-gateway-class",
        },
        "spec": {
            "controllerName": "gateway.envoyproxy.io/gatewayclass-controller",
        },
    }

    gateway = {
        "apiVersion": "gateway.networking.k8s.io/v1",
        "kind": "Gateway",
        "metadata": {
            "name": "main-gateway",
            "namespace": "infra-gateway",
        },
        "spec": {
            "gatewayClassName": "envoy-gateway-class",
            "listeners": [
                {
                    "name": "http",
                    "port": 80,
                    "protocol": "HTTP",
                    "allowedRoutes": {
                        "namespaces": {
                            "from": "Same",
                        },
                    },
                },
            ],
        },
    }

    return [gateway_class, gateway]


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

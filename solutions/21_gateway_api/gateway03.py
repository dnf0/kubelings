"""
Solution: gateway03.py
Topic: Gateway API - Weighted Canary Traffic Splitting and URL Rewrite Filters
"""


def build_canary_route() -> dict:
    return {
        "apiVersion": "gateway.networking.k8s.io/v1",
        "kind": "HTTPRoute",
        "metadata": {
            "name": "frontend-canary-route",
            "namespace": "frontend",
        },
        "spec": {
            "parentRefs": [
                {
                    "name": "main-gateway",
                    "namespace": "infra-gateway",
                },
            ],
            "rules": [
                {
                    "matches": [
                        {
                            "path": {
                                "type": "PathPrefix",
                                "value": "/app",
                            },
                        },
                    ],
                    "filters": [
                        {
                            "type": "URLRewrite",
                            "urlRewrite": {
                                "path": {
                                    "type": "ReplacePrefixMatch",
                                    "replacePrefixMatch": "/",
                                },
                            },
                        },
                        {
                            "type": "RequestHeaderModifier",
                            "requestHeaderModifier": {
                                "set": [
                                    {
                                        "name": "X-Forwarded-By",
                                        "value": "GatewayAPI",
                                    },
                                ],
                            },
                        },
                    ],
                    "backendRefs": [
                        {
                            "name": "frontend-v1",
                            "port": 80,
                            "weight": 80,
                        },
                        {
                            "name": "frontend-v2",
                            "port": 80,
                            "weight": 20,
                        },
                    ],
                },
            ],
        },
    }


def verify():
    route = build_canary_route()
    assert route.get("apiVersion") == "gateway.networking.k8s.io/v1"
    assert route.get("kind") == "HTTPRoute"
    assert route.get("metadata", {}).get("name") == "frontend-canary-route"
    assert route.get("metadata", {}).get("namespace") == "frontend"

    rules = route.get("spec", {}).get("rules", [])
    assert len(rules) == 1
    r = rules[0]

    # Filters check
    filters = r.get("filters", [])
    assert len(filters) >= 2, f"Expected at least 2 filters, found {len(filters)}"

    rewrite = next((f for f in filters if f.get("type") == "URLRewrite"), None)
    assert rewrite is not None, "Missing URLRewrite filter"
    assert rewrite.get("urlRewrite", {}).get("path", {}).get("type") == "ReplacePrefixMatch"
    assert rewrite.get("urlRewrite", {}).get("path", {}).get("replacePrefixMatch") == "/"

    header_mod = next((f for f in filters if f.get("type") == "RequestHeaderModifier"), None)
    assert header_mod is not None, "Missing RequestHeaderModifier filter"
    headers_set = header_mod.get("requestHeaderModifier", {}).get("set", [])
    h0 = headers_set[0]
    assert h0.get("name") == "X-Forwarded-By"
    assert h0.get("value") == "GatewayAPI"

    # Backend weights check
    backends = r.get("backendRefs", [])
    assert len(backends) == 2, f"Expected 2 backendRefs for canary split, found {len(backends)}"
    b_v1 = next((b for b in backends if b.get("name") == "frontend-v1"), None)
    b_v2 = next((b for b in backends if b.get("name") == "frontend-v2"), None)
    assert b_v1 is not None and b_v1.get("weight") == 80
    assert b_v2 is not None and b_v2.get("weight") == 20
    assert b_v1.get("port") == 80 and b_v2.get("port") == 80

    print("✓ Weighted canary traffic splitting and URL rewrite successfully validated!")


if __name__ == "__main__":
    verify()

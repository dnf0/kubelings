"""
Solution: gateway02.py
Topic: Gateway API - HTTPRoute Path Matching and Backend Routing
"""


def build_http_route() -> dict:
    return {
        "apiVersion": "gateway.networking.k8s.io/v1",
        "kind": "HTTPRoute",
        "metadata": {
            "name": "api-service-route",
            "namespace": "apps",
        },
        "spec": {
            "parentRefs": [
                {
                    "name": "main-gateway",
                    "namespace": "infra-gateway",
                },
            ],
            "hostnames": [
                "api.example.com",
            ],
            "rules": [
                {
                    "matches": [
                        {
                            "path": {
                                "type": "PathPrefix",
                                "value": "/v1/users",
                            },
                        },
                    ],
                    "backendRefs": [
                        {
                            "name": "users-v1-svc",
                            "port": 8080,
                        },
                    ],
                },
                {
                    "matches": [
                        {
                            "path": {
                                "type": "PathPrefix",
                                "value": "/v1/orders",
                            },
                            "headers": [
                                {
                                    "name": "X-Beta-Features",
                                    "value": "enabled",
                                },
                            ],
                        },
                    ],
                    "backendRefs": [
                        {
                            "name": "orders-beta-svc",
                            "port": 9090,
                        },
                    ],
                },
            ],
        },
    }


def verify():
    route = build_http_route()
    assert route.get("apiVersion") == "gateway.networking.k8s.io/v1"
    assert route.get("kind") == "HTTPRoute"
    assert route.get("metadata", {}).get("name") == "api-service-route"
    assert route.get("metadata", {}).get("namespace") == "apps"

    parent_refs = route.get("spec", {}).get("parentRefs", [])
    assert len(parent_refs) == 1
    p0 = parent_refs[0]
    assert p0.get("name") == "main-gateway"
    assert p0.get("namespace") == "infra-gateway"

    hostnames = route.get("spec", {}).get("hostnames", [])
    assert "api.example.com" in hostnames

    rules = route.get("spec", {}).get("rules", [])
    assert len(rules) == 2, f"Expected 2 routing rules, found {len(rules)}"

    # Rule 1: Users service
    r1 = rules[0]
    m1 = r1.get("matches", [])[0]
    assert m1.get("path", {}).get("type") == "PathPrefix"
    assert m1.get("path", {}).get("value") == "/v1/users"
    b1 = r1.get("backendRefs", [])[0]
    assert b1.get("name") == "users-v1-svc"
    assert b1.get("port") == 8080

    # Rule 2: Beta orders service
    r2 = rules[1]
    m2 = r2.get("matches", [])[0]
    assert m2.get("path", {}).get("value") == "/v1/orders"
    h2 = m2.get("headers", [])[0]
    assert h2.get("name") == "X-Beta-Features"
    assert h2.get("value") == "enabled"
    b2 = r2.get("backendRefs", [])[0]
    assert b2.get("name") == "orders-beta-svc"
    assert b2.get("port") == 9090

    print("✓ HTTPRoute path and header matching successfully validated!")


if __name__ == "__main__":
    verify()

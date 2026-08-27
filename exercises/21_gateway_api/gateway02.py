# I AM NOT DONE
"""
Exercise: gateway02.py
Topic: Gateway API - HTTPRoute Path Matching and Backend Routing

Task:
Define an HTTPRoute resource attached to a Gateway:
1. 'apiVersion': 'gateway.networking.k8s.io/v1', 'kind': 'HTTPRoute'
2. Named 'api-service-route' in namespace 'apps'
3. Attach to parentRef Gateway named 'main-gateway' in namespace 'infra-gateway'
4. Specify hostnames: ['api.example.com']
5. Define two rules:
   a. Rule 1: Match path prefix '/v1/users', routes to backendRef 'users-v1-svc' on port 8080
   b. Rule 2: Match header 'X-Beta-Features' == 'enabled' AND path prefix '/v1/orders', routes to backendRef 'orders-beta-svc' on port 9090
"""

import yaml


def build_http_route() -> dict:
    # TODO: Define and return HTTPRoute manifest
    return {}


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

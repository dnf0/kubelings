"""
Exercise: gateway03.py
Topic: Gateway API - Weighted Canary Traffic Splitting and URL Rewrite Filters

Context & Why:
Progressive delivery strategies (such as canary rollouts and blue/green deployments) require
fine-grained control over traffic distribution and request modification before requests hit
backend pods.

Traditional Ingress controllers required vendor-specific annotations (e.g. `nginx.ingress.kubernetes.io/canary-weight`)
which led to fragmented configurations across cloud environments. The Gateway API elevates these
capabilities into native, standardized API primitives:
- `backendRefs[*].weight`: Enables declarative weighted traffic shifting across multiple backend
  services (e.g., 80% to stable `frontend-v1` and 20% to canary `frontend-v2`).
- `filters`: Provides standard request/response mutations directly in the data plane:
  * `URLRewrite`: Modifies incoming URI paths (e.g. rewriting `/app` prefix to `/`) before passing to upstream services.
  * `RequestHeaderModifier`: Injects, mutates, or removes HTTP headers (e.g., adding `X-Forwarded-By: GatewayAPI`)
    to maintain traceability across service boundaries.

Task:
Define an HTTPRoute configured for advanced canary traffic management:
1. 'apiVersion': 'gateway.networking.k8s.io/v1', 'kind': 'HTTPRoute'
2. Named 'frontend-canary-route' in namespace 'frontend'
3. Attach to parentRef Gateway 'main-gateway' in namespace 'infra-gateway'
4. Define a single rule matching path prefix '/app':
   a. Filter 1: 'URLRewrite' with path 'ReplacePrefixMatch' set to '/'
   b. Filter 2: 'RequestHeaderModifier' setting header 'X-Forwarded-By' to 'GatewayAPI'
   c. Split traffic across 2 backendRefs:
      - 'frontend-v1' service on port 80 with weight 80
      - 'frontend-v2' service on port 80 with weight 20
"""

import yaml


def build_canary_route() -> dict:
    # TODO: Define and return the HTTPRoute manifest configured with URL rewrite filters, request header modifiers, and weighted backend canary traffic splitting.
    # WHY: Gateway API standardizes advanced traffic manipulation (URL rewriting and header mutation) and weighted multi-backend routing
    #      as first-class core primitives, enabling reliable canary rollouts without proprietary ingress controller annotations.
    return {}


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

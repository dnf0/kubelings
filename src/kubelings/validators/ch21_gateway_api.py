"""
Validators for Chapter 21: Next-Gen Traffic Routing with Kubernetes Gateway API
"""

from typing import Any

from kubelings.validators import register_validator


def build_gateway_resources() -> list[dict]:
    gateway_class = {
        "apiVersion": "gateway.networking.k8s.io/v1",
        "kind": "GatewayClass",
        "metadata": {"name": "envoy-gateway-class"},
        "spec": {"controllerName": "gateway.envoyproxy.io/gatewayclass-controller"},
    }
    gateway = {
        "apiVersion": "gateway.networking.k8s.io/v1",
        "kind": "Gateway",
        "metadata": {"name": "main-gateway", "namespace": "infra-gateway"},
        "spec": {
            "gatewayClassName": "envoy-gateway-class",
            "listeners": [
                {
                    "name": "http",
                    "port": 80,
                    "protocol": "HTTP",
                    "allowedRoutes": {"namespaces": {"from": "Same"}},
                }
            ],
        },
    }
    return [gateway_class, gateway]


@register_validator("gateway01")
def validate_gateway01(manifest: Any, raw_yaml: str = "") -> None:
    manifests = manifest
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


def build_http_route() -> dict:
    return {
        "apiVersion": "gateway.networking.k8s.io/v1",
        "kind": "HTTPRoute",
        "metadata": {"name": "api-service-route", "namespace": "apps"},
        "spec": {
            "parentRefs": [{"name": "main-gateway", "namespace": "infra-gateway"}],
            "hostnames": ["api.example.com"],
            "rules": [
                {
                    "matches": [{"path": {"type": "PathPrefix", "value": "/v1/users"}}],
                    "backendRefs": [{"name": "users-v1-svc", "port": 8080}],
                },
                {
                    "matches": [
                        {
                            "path": {"type": "PathPrefix", "value": "/v1/orders"},
                            "headers": [{"name": "X-Beta-Features", "value": "enabled"}],
                        }
                    ],
                    "backendRefs": [{"name": "orders-beta-svc", "port": 9090}],
                },
            ],
        },
    }


@register_validator("gateway02")
def validate_gateway02(manifest: Any, raw_yaml: str = "") -> None:
    route = manifest
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
    r1 = rules[0]
    m1 = r1.get("matches", [])[0]
    assert m1.get("path", {}).get("type") == "PathPrefix"
    assert m1.get("path", {}).get("value") == "/v1/users"
    b1 = r1.get("backendRefs", [])[0]
    assert b1.get("name") == "users-v1-svc"
    assert b1.get("port") == 8080
    r2 = rules[1]
    m2 = r2.get("matches", [])[0]
    assert m2.get("path", {}).get("value") == "/v1/orders"
    h2 = m2.get("headers", [])[0]
    assert h2.get("name") == "X-Beta-Features"
    assert h2.get("value") == "enabled"
    b2 = r2.get("backendRefs", [])[0]
    assert b2.get("name") == "orders-beta-svc"
    assert b2.get("port") == 9090


def build_canary_route() -> dict:
    return {
        "apiVersion": "gateway.networking.k8s.io/v1",
        "kind": "HTTPRoute",
        "metadata": {"name": "frontend-canary-route", "namespace": "frontend"},
        "spec": {
            "parentRefs": [{"name": "main-gateway", "namespace": "infra-gateway"}],
            "rules": [
                {
                    "matches": [{"path": {"type": "PathPrefix", "value": "/app"}}],
                    "filters": [
                        {
                            "type": "URLRewrite",
                            "urlRewrite": {
                                "path": {"type": "ReplacePrefixMatch", "replacePrefixMatch": "/"}
                            },
                        },
                        {
                            "type": "RequestHeaderModifier",
                            "requestHeaderModifier": {
                                "set": [{"name": "X-Forwarded-By", "value": "GatewayAPI"}]
                            },
                        },
                    ],
                    "backendRefs": [
                        {"name": "frontend-v1", "port": 80, "weight": 80},
                        {"name": "frontend-v2", "port": 80, "weight": 20},
                    ],
                }
            ],
        },
    }


@register_validator("gateway03")
def validate_gateway03(manifest: Any, raw_yaml: str = "") -> None:
    route = manifest
    assert route.get("apiVersion") == "gateway.networking.k8s.io/v1"
    assert route.get("kind") == "HTTPRoute"
    assert route.get("metadata", {}).get("name") == "frontend-canary-route"
    assert route.get("metadata", {}).get("namespace") == "frontend"
    rules = route.get("spec", {}).get("rules", [])
    assert len(rules) == 1
    r = rules[0]
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
    backends = r.get("backendRefs", [])
    assert len(backends) == 2, f"Expected 2 backendRefs for canary split, found {len(backends)}"
    b_v1 = next((b for b in backends if b.get("name") == "frontend-v1"), None)
    b_v2 = next((b for b in backends if b.get("name") == "frontend-v2"), None)
    assert b_v1 is not None and b_v1.get("weight") == 80
    assert b_v2 is not None and b_v2.get("weight") == 20
    assert b_v1.get("port") == 80 and b_v2.get("port") == 80


def build_reference_grant() -> dict:
    return {
        "apiVersion": "gateway.networking.k8s.io/v1beta1",
        "kind": "ReferenceGrant",
        "metadata": {"name": "allow-edge-to-backend", "namespace": "backend"},
        "spec": {
            "from": [
                {"group": "gateway.networking.k8s.io", "kind": "HTTPRoute", "namespace": "edge"}
            ],
            "to": [{"group": "", "kind": "Service", "name": "account-service"}],
        },
    }


@register_validator("gateway04")
def validate_gateway04(manifest: Any, raw_yaml: str = "") -> None:
    grant = manifest
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

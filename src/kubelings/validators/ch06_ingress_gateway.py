"""
Validators for Chapter 06: Ingress & Gateway API
"""

import re
from typing import Any, Dict, Optional

import yaml

from kubelings.validator import validate_manifest, validate_manifests
from kubelings.validators import register_validator


def route_ingress_request(ingress_manifest: Dict[str, Any], host: str, path: str) -> Optional[str]:
    """Find the destination backend service for a given incoming host and request path."""
    rules = ingress_manifest.get("spec", {}).get("rules", [])
    matching_services = []
    for r in rules:
        if r.get("host") == host:
            paths = r.get("http", {}).get("paths", [])
            for p in paths:
                prefix = p.get("path", "")
                if path.startswith(prefix):
                    matching_services.append(
                        (len(prefix), p.get("backend", {}).get("service", {}).get("name"))
                    )
    if not matching_services:
        return None
    matching_services.sort(key=lambda x: x[0], reverse=True)
    return matching_services[0][1]


@register_validator("ingress01")
def validate_ingress01(manifest: Any, raw_yaml: str = "") -> None:
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(
        manifest, expected_kind="Ingress", expected_api_version="networking.k8s.io/v1"
    )
    assert manifest["metadata"]["name"] == "api-gateway-ingress"
    assert manifest["spec"]["ingressClassName"] == "nginx"
    rules = manifest["spec"]["rules"]
    assert len(rules) == 2
    assert route_ingress_request(manifest, "api.example.com", "/v1/users") == "api-v1-service"
    assert route_ingress_request(manifest, "api.example.com", "/v2/products") == "api-v2-service"
    assert (
        route_ingress_request(manifest, "admin.example.com", "/dashboard") == "admin-portal-service"
    )
    assert route_ingress_request(manifest, "unknown.example.com", "/") is None


MANIFESTS = "\napiVersion: networking.k8s.io/v1\nkind: Ingress\nmetadata:\n  name: secure-ingress\nspec:\n  tls:\n  - hosts:\n    - secure.example.com\n    - api.secure.example.com\n    secretName: wildcard-tls-secret\n  rules:\n  - host: secure.example.com\n    http:\n      paths:\n      - path: /\n        pathType: Prefix\n        backend:\n          service:\n            name: secure-web-service\n            port:\n              number: 443\n---\napiVersion: v1\nkind: Secret\nmetadata:\n  name: wildcard-tls-secret\ntype: kubernetes.io/tls\ndata:\n  tls.crt: LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCg==\n  tls.key: LS0tLS1CRUdJTiBQUklWQVRFIEtFWS0tLS0tCg==\n"


def verify_ingress_tls_coverage(ingress: Dict[str, Any], secret: Dict[str, Any]) -> bool:
    """Verify that all Ingress hosts are securely covered by the TLS configuration."""
    if secret.get("type") != "kubernetes.io/tls":
        return False
    secret_data = secret.get("data", {})
    if "tls.crt" not in secret_data or "tls.key" not in secret_data:
        return False
    tls_configs = ingress.get("spec", {}).get("tls", [])
    covered_hosts = set()
    secret_matched = False
    for item in tls_configs:
        if item.get("secretName") == secret.get("metadata", {}).get("name"):
            secret_matched = True
            for h in item.get("hosts", []):
                covered_hosts.add(h)
    if not secret_matched:
        return False
    rules = ingress.get("spec", {}).get("rules", [])
    for r in rules:
        host = r.get("host")
        if host and host not in covered_hosts:
            return False
    return True


@register_validator("ingress02")
def validate_ingress02(manifest: Any, raw_yaml: str = "") -> None:
    manifests = manifest if isinstance(manifest, list) else [manifest]
    assert len(manifests) == 2, "Must define 2 manifests (Ingress and TLS Secret)"
    validate_manifests(manifests, expected_kinds=["Ingress", "Secret"])
    ing, sec = (manifests[0], manifests[1])
    assert ing["metadata"]["name"] == "secure-ingress"
    tls_entry = ing["spec"]["tls"][0]
    assert "secure.example.com" in tls_entry["hosts"]
    assert "api.secure.example.com" in tls_entry["hosts"]
    assert tls_entry["secretName"] == "wildcard-tls-secret"
    assert sec["metadata"]["name"] == "wildcard-tls-secret"
    assert sec["type"] == "kubernetes.io/tls"
    assert "tls.crt" in sec["data"]
    assert "tls.key" in sec["data"]
    assert verify_ingress_tls_coverage(ing, sec) is True
    bad_ing = yaml.safe_load(yaml.dump(ing))
    bad_ing["spec"]["rules"].append(
        {
            "host": "unprotected.example.com",
            "http": {
                "paths": [
                    {
                        "path": "/",
                        "pathType": "Prefix",
                        "backend": {"service": {"name": "app", "port": {"number": 80}}},
                    }
                ]
            },
        }
    )
    assert verify_ingress_tls_coverage(bad_ing, sec) is False, (
        "Should fail when rule host not listed in tls.hosts"
    )


def apply_rewrite_rule(path_regex: str, rewrite_template: str, request_path: str) -> Optional[str]:
    """Simulate nginx rewrite-target behavior for a request path."""
    match = re.match(path_regex, request_path)
    if not match:
        return None
    return re.sub(path_regex, rewrite_template, request_path)


@register_validator("ingress03")
def validate_ingress03(manifest: Any, raw_yaml: str = "") -> None:
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(
        manifest, expected_kind="Ingress", expected_api_version="networking.k8s.io/v1"
    )
    ann = manifest["metadata"]["annotations"]
    assert str(ann.get("nginx.ingress.kubernetes.io/rewrite-target")) == "/$2"
    assert str(ann.get("nginx.ingress.kubernetes.io/ssl-redirect")) == "true"
    assert str(ann.get("nginx.ingress.kubernetes.io/proxy-body-size")) == "50m"
    rule_path = manifest["spec"]["rules"][0]["http"]["paths"][0]
    assert rule_path["path"] == "/payments(/|$)(.*)"
    assert rule_path["pathType"] == "ImplementationSpecific"
    assert rule_path["backend"]["service"]["name"] == "payments-service"
    pattern = "^/payments(/|$)(.*)"
    assert apply_rewrite_rule(pattern, "/\\2", "/payments/v1/charge") == "/v1/charge"
    assert apply_rewrite_rule(pattern, "/\\2", "/payments") == "/"
    assert apply_rewrite_rule(pattern, "/\\2", "/other/path") is None


def calculate_canary_traffic_split(http_route: Dict[str, Any]) -> Dict[str, float]:
    """Calculate the percentage share of traffic directed to each backend service."""
    rules = http_route.get("spec", {}).get("rules", [])
    if not rules:
        return {}
    backends = rules[0].get("backendRefs", [])
    total_weight = sum((b.get("weight", 1) for b in backends))
    if total_weight == 0:
        return {}
    return {b["name"]: round(b.get("weight", 1) / total_weight * 100.0, 2) for b in backends}


@register_validator("ingress04")
def validate_ingress04(manifest: Any, raw_yaml: str = "") -> None:
    manifests = manifest if isinstance(manifest, list) else [manifest]
    assert len(manifests) == 2, "Must define 2 manifests (Gateway and HTTPRoute)"
    validate_manifests(manifests, expected_kinds=["Gateway", "HTTPRoute"])
    gw, route = (manifests[0], manifests[1])
    assert gw["metadata"]["name"] == "prod-edge-gw"
    assert gw["spec"]["gatewayClassName"] == "envoy-gateway"
    assert gw["spec"]["listeners"][0]["allowedRoutes"]["namespaces"]["from"] == "Same"
    assert route["metadata"]["name"] == "orders-traffic-route"
    assert route["spec"]["parentRefs"][0]["name"] == "prod-edge-gw"
    assert "orders.production.com" in route["spec"]["hostnames"]
    backends = route["spec"]["rules"][0]["backendRefs"]
    assert len(backends) == 2
    split = calculate_canary_traffic_split(route)
    assert split.get("orders-v1") == 90.0
    assert split.get("orders-v2-canary") == 10.0

"""
Exercise: solutions/06_ingress_gateway/ingress04.py
Topic: Gateway API Fundamentals

Reference Solution
"""

from typing import Any, Dict
import yaml
from kubelings.validator import validate_manifests

MANIFESTS = """
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: prod-edge-gw
spec:
  gatewayClassName: envoy-gateway
  listeners:
  - name: http
    protocol: HTTP
    port: 80
    allowedRoutes:
      namespaces:
        from: Same
---
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: orders-traffic-route
spec:
  parentRefs:
  - name: prod-edge-gw
  hostnames:
  - orders.production.com
  rules:
  - matches:
    - path:
        type: PathPrefix
        value: /orders
    backendRefs:
    - name: orders-v1
      port: 8080
      weight: 90
    - name: orders-v2-canary
      port: 8080
      weight: 10
"""


def calculate_canary_traffic_split(http_route: Dict[str, Any]) -> Dict[str, float]:
    """Calculate the percentage share of traffic directed to each backend service."""
    rules = http_route.get("spec", {}).get("rules", [])
    if not rules:
        return {}
    backends = rules[0].get("backendRefs", [])
    total_weight = sum(b.get("weight", 1) for b in backends)
    if total_weight == 0:
        return {}

    return {
        b["name"]: round((b.get("weight", 1) / total_weight) * 100.0, 2)
        for b in backends
    }


def verify():
    manifests = list(yaml.safe_load_all(MANIFESTS))
    assert len(manifests) == 2, "Must define 2 manifests (Gateway and HTTPRoute)"
    validate_manifests(manifests, expected_kinds=["Gateway", "HTTPRoute"])

    gw, route = manifests[0], manifests[1]

    assert gw["metadata"]["name"] == "prod-edge-gw"
    assert gw["spec"]["gatewayClassName"] == "envoy-gateway"
    assert gw["spec"]["listeners"][0]["allowedRoutes"]["namespaces"]["from"] == "Same"

    assert route["metadata"]["name"] == "orders-traffic-route"
    assert route["spec"]["parentRefs"][0]["name"] == "prod-edge-gw"
    assert "orders.production.com" in route["spec"]["hostnames"]

    backends = route["spec"]["rules"][0]["backendRefs"]
    assert len(backends) == 2

    # Verify canary split calculation
    split = calculate_canary_traffic_split(route)
    assert split.get("orders-v1") == 90.0
    assert split.get("orders-v2-canary") == 10.0

    print("✓ ingress04 passed!")


if __name__ == "__main__":
    verify()

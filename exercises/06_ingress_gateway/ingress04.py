"""
Exercise: exercises/06_ingress_gateway/ingress04.py
Topic: Gateway API Fundamentals

Instructions:
The Kubernetes Gateway API (`gateway.networking.k8s.io/v1`) is the modern evolution
of Ingress, featuring role-oriented resource separation:
- GatewayClass (Infrastructure Provider)
- Gateway (Cluster Operator)
- HTTPRoute / GRPCRoute (Application Developer)

1. Complete the Gateway manifest:
   - name: 'prod-edge-gw'
   - gatewayClassName: 'envoy-gateway'
   - listener 'http': protocol HTTP, port 80, allowedRoutes from 'Same' namespace
2. Complete the HTTPRoute manifest with weighted canary traffic splitting:
   - name: 'orders-traffic-route'
   - parentRefs pointing to Gateway 'prod-edge-gw'
   - hostnames: ['orders.production.com']
   - rule matching path PathPrefix '/orders'
   - backendRefs:
     - 'orders-v1': port 8080, weight 90
     - 'orders-v2-canary': port 8080, weight 10
3. Implement `calculate_canary_traffic_split(http_route)`:
   - Returns a dict mapping each backend service name to its percentage of total traffic (0.0 to 100.0).
"""

# I AM NOT DONE

from typing import Any, Dict

import yaml

from kubelings.validator import validate_manifests

MANIFESTS = """
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: prod-edge-gw
spec:
  gatewayClassName: ???
  listeners:
  - name: http
    protocol: HTTP
    port: 80
    allowedRoutes:
      namespaces:
        from: ???
---
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: orders-traffic-route
spec:
  parentRefs:
  - name: ???
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
    # TODO: Implement traffic weight calculation
    return {}


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

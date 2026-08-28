"""
Exercise: Cilium L7 HTTP NetworkPolicy (mesh01)

Context & Why:
Standard Kubernetes `NetworkPolicy` resources operate exclusively at Layer 3 (IP addresses)
and Layer 4 (TCP/UDP port numbers). In microservice architectures, this coarse granularity
is insufficient: it cannot distinguish between safe read endpoints (such as `GET /api/v1/public/.*`)
and state-modifying or privileged endpoints (such as `POST /api/v1/orders`), nor can it enforce
required HTTP authentication headers.

Cilium leverages Linux kernel eBPF (extended Berkeley Packet Filter) and integrated Envoy
data path proxies to enforce Layer 7 (L7) application-aware security policies. A `CiliumNetworkPolicy`
allows platform engineers to specify HTTP verbs, URI regex paths, and header constraints.
Because packet inspection happens at the kernel and local socket layers, fine-grained L7 zero-trust
security is achieved without injecting intrusive sidecar containers into every application pod.

Task:
Complete `get_cilium_l7_policy()` to return a `CiliumNetworkPolicy` dictionary:
1. apiVersion: "cilium.io/v2"
2. kind: "CiliumNetworkPolicy"
3. metadata:
   - name: "secure-api-l7"
4. spec:
   - endpointSelector:
     - matchLabels:
       - app: "secure-backend"
   - ingress:
     - fromEndpoints:
       - matchLabels:
         - app: "frontend"
     - toPorts:
       - ports:
         - port: "8080"
           protocol: "TCP"
         rules:
           http:
             - method: "GET"
               path: "/api/v1/public/.*"
             - method: "POST"
               path: "/api/v1/orders"
               headers:
                 - "X-Client-Role: authorized"
"""

from typing import Any, Dict


def get_cilium_l7_policy() -> Dict[str, Any]:
    # TODO: Construct and return the dictionary representation of a CiliumNetworkPolicy CRD
    #       specifying endpointSelector, ingress source endpoints, and L7 HTTP method/path/header rules.
    # WHY: Layer 7 network policies extend security beyond L3/L4 port-level controls, enabling granular
    #      HTTP route and header authorization enforced directly via eBPF without requiring sidecar containers.
    return {}


def verify() -> None:
    policy = get_cilium_l7_policy()
    assert policy, "Policy cannot be empty"
    assert policy.get("apiVersion") == "cilium.io/v2"
    assert policy.get("kind") == "CiliumNetworkPolicy"

    meta = policy.get("metadata", {})
    assert meta.get("name") == "secure-api-l7"

    spec = policy.get("spec", {})
    endpoint = spec.get("endpointSelector", {})
    assert endpoint.get("matchLabels", {}).get("app") == "secure-backend"

    ingress = spec.get("ingress", [])
    assert len(ingress) > 0

    from_ep = ingress[0].get("fromEndpoints", [])
    assert from_ep[0].get("matchLabels", {}).get("app") == "frontend"

    to_ports = ingress[0].get("toPorts", [])
    assert len(to_ports) > 0
    ports = to_ports[0].get("ports", [])
    assert ports[0].get("port") == "8080"
    assert ports[0].get("protocol") == "TCP"

    http_rules = to_ports[0].get("rules", {}).get("http", [])
    assert len(http_rules) == 2
    assert http_rules[0].get("method") == "GET"
    assert http_rules[1].get("method") == "POST"

    print("✓ Cilium L7 Network Policy validated successfully!")


if __name__ == "__main__":
    verify()

"""
Exercise: CiliumClusterwideNetworkPolicy with DNS Inspection (mesh03)

Context & Why:
Standard Kubernetes NetworkPolicies are namespace-scoped and rely on static IP or CIDR
blocks. In modern cloud environments, egress destinations (such as GitHub, AWS S3, or third-party
APIs) use dynamic, rotating IP pools behind CDNs and load balancers. Attempting to manage
egress using static CIDRs leads to frequent outages or overly permissive CIDR rules (e.g. `0.0.0.0/0`).

Cilium solves this with `CiliumClusterwideNetworkPolicy` and live DNS proxy inspection.
When a pod performs a DNS query (e.g. for `api.github.com` or `*.amazonaws.com`), the eBPF datapath
intercepts the response, maps the resolved IPs dynamically to the authorized FQDN (Fully Qualified
Domain Name), and opens temporary egress on designated ports (like port 443 TCP). Because the policy
is cluster-scoped (`CiliumClusterwideNetworkPolicy`), baseline egress security guards every node
and namespace uniformly.

Task:
Complete `get_clusterwide_egress_policy()` returning a `CiliumClusterwideNetworkPolicy`:
1. apiVersion: "cilium.io/v2"
2. kind: "CiliumClusterwideNetworkPolicy"
3. metadata:
   - name: "secure-external-egress"
4. spec:
   - nodeSelector:
     - matchLabels: {}
   - egress:
     - toFQDNs:
       - matchName: "api.github.com"
       - matchPattern: "*.amazonaws.com"
     - toPorts:
       - ports:
         - port: "443"
           protocol: "TCP"
         rules:
           dns:
             - matchPattern: "*"
"""

from typing import Any, Dict


def get_clusterwide_egress_policy() -> Dict[str, Any]:
    # TODO: Construct and return the dictionary representation of a CiliumClusterwideNetworkPolicy CRD
    #       defining clusterwide FQDN egress rules (matchName and matchPattern) with DNS proxy inspection.
    # WHY: Cluster-wide FQDN egress policies protect nodes from data exfiltration and C2 attacks by dynamically
    #      resolving allowed external domains through DNS proxy inspection instead of brittle, hardcoded IP blocks.
    return {}


def verify() -> None:
    policy = get_clusterwide_egress_policy()
    assert policy, "Policy cannot be empty"
    assert policy.get("apiVersion") == "cilium.io/v2"
    assert policy.get("kind") == "CiliumClusterwideNetworkPolicy"

    meta = policy.get("metadata", {})
    assert meta.get("name") == "secure-external-egress"

    spec = policy.get("spec", {})
    egress = spec.get("egress", [])
    assert len(egress) > 0

    to_fqdns = egress[0].get("toFQDNs", [])
    assert any(f.get("matchName") == "api.github.com" for f in to_fqdns)
    assert any(f.get("matchPattern") == "*.amazonaws.com" for f in to_fqdns)

    to_ports = egress[0].get("toPorts", [])
    assert len(to_ports) > 0
    assert to_ports[0].get("ports", [{}])[0].get("port") == "443"

    print("✓ CiliumClusterwideNetworkPolicy FQDN Egress validated successfully!")


if __name__ == "__main__":
    verify()

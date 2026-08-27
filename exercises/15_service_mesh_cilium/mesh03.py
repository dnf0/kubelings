"""
Exercise: CiliumClusterwideNetworkPolicy with DNS Inspection (mesh03)

Cilium cluster-wide network policies protect the entire cluster across all namespaces
and can enforce egress rules by domain names (FQDNs) via live DNS proxy inspection.

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
    # TODO: Define and return the CiliumClusterwideNetworkPolicy manifest dictionary
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

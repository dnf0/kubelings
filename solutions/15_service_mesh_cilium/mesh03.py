"""
Solution: CiliumClusterwideNetworkPolicy with DNS Inspection (mesh03)
"""

from typing import Any, Dict


def get_clusterwide_egress_policy() -> Dict[str, Any]:
    return {
        "apiVersion": "cilium.io/v2",
        "kind": "CiliumClusterwideNetworkPolicy",
        "metadata": {
            "name": "secure-external-egress",
        },
        "spec": {
            "nodeSelector": {
                "matchLabels": {},
            },
            "egress": [
                {
                    "toFQDNs": [
                        {"matchName": "api.github.com"},
                        {"matchPattern": "*.amazonaws.com"},
                    ],
                    "toPorts": [
                        {
                            "ports": [
                                {
                                    "port": "443",
                                    "protocol": "TCP",
                                }
                            ],
                            "rules": {
                                "dns": [
                                    {"matchPattern": "*"}
                                ]
                            },
                        }
                    ],
                }
            ],
        },
    }


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

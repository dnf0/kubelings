"""
Exercise: solutions/09_network_policies/netpol04.py
Topic: Named Ports & IPBlock CIDR Exceptions

Reference Solution
"""

import ipaddress
from typing import List

import yaml

from kubelings.validator import validate_manifest

POLICY_MANIFEST = """
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: external-api-egress
  namespace: default
spec:
  podSelector:
    matchLabels:
      app: gateway
  policyTypes:
  - Egress
  egress:
  - to:
    - ipBlock:
        cidr: 192.168.0.0/16
        except:
        - 192.168.1.0/24
    ports:
    - protocol: TCP
      port: http
"""


def is_ip_in_ipblock(ip_str: str, cidr_str: str, except_cidrs: List[str]) -> bool:
    """Check if an IP address is inside the cidr range and outside all except ranges."""
    ip = ipaddress.ip_address(ip_str)
    main_network = ipaddress.ip_network(cidr_str)
    if ip not in main_network:
        return False
    for exc in except_cidrs:
        if ip in ipaddress.ip_network(exc):
            return False
    return True


def verify():
    manifest = yaml.safe_load(POLICY_MANIFEST)
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(
        manifest, expected_kind="NetworkPolicy", expected_api_version="networking.k8s.io/v1"
    )

    assert manifest["metadata"]["name"] == "external-api-egress"
    assert manifest["metadata"]["namespace"] == "default"

    spec = manifest.get("spec", {})
    assert spec.get("podSelector", {}).get("matchLabels", {}).get("app") == "gateway"
    assert spec.get("policyTypes") == ["Egress"]

    egress = spec.get("egress", [])
    assert len(egress) == 1

    rule = egress[0]
    to_block = rule["to"][0]["ipBlock"]
    assert to_block["cidr"] == "192.168.0.0/16"
    assert to_block["except"] == ["192.168.1.0/24"]

    port = rule["ports"][0]
    assert port["protocol"] == "TCP"
    assert port["port"] == "http"

    # Test IPBlock checker logic
    assert is_ip_in_ipblock("192.168.0.50", "192.168.0.0/16", ["192.168.1.0/24"]) is True
    assert is_ip_in_ipblock("192.168.2.100", "192.168.0.0/16", ["192.168.1.0/24"]) is True
    assert is_ip_in_ipblock("192.168.1.15", "192.168.0.0/16", ["192.168.1.0/24"]) is False, (
        "Excluded by exception subnet"
    )
    assert is_ip_in_ipblock("10.0.0.1", "192.168.0.0/16", ["192.168.1.0/24"]) is False, (
        "Outside CIDR"
    )

    print("✓ netpol04 passed!")


if __name__ == "__main__":
    verify()

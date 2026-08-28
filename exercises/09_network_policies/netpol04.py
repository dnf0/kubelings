"""
Exercise: exercises/09_network_policies/netpol04.py
Topic: Named Ports & IPBlock CIDR Exceptions

Context & Why:
Kubernetes NetworkPolicies can control traffic beyond the cluster perimeter by defining `ipBlock`
CIDR ranges for external destinations (e.g., third-party payment APIs, legacy on-premises databases).
The `except` block enables fine-grained network segmentation by carving out sensitive internal subnets
from broader CIDR ranges. Furthermore, referencing `ports.port` as a named port string (e.g. 'http')
rather than a numeric literal decouples the security policy from container port remapping, allowing
developers to modify application container ports without modifying network security manifests.

Instructions:
1. Configure NetworkPolicy 'external-api-egress' in namespace 'default':
   - Targets pods with label `app: gateway`.
   - Egress rule: Allow TCP traffic to named port 'http' for IP range '192.168.0.0/16',
     EXCEPT subnet '192.168.1.0/24'.
2. Implement `is_ip_in_ipblock(ip_str, cidr_str, except_cidrs)`:
   - Uses python's standard `ipaddress` module to check if `ip_str` falls within `cidr_str`
     and is NOT in any of the subnets listed in `except_cidrs`.
"""

import ipaddress  # noqa: F401
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
        # TODO: Set the target network CIDR '192.168.0.0/16'.
        # WHY: Authorizes egress to the entire corporate external private network block.
        cidr: ???
        except:
        # TODO: Carve out the restricted management subnet '192.168.1.0/24'.
        # WHY: Blocks access to sensitive management and database subnets within the wider CIDR.
        - ???
    ports:
    - protocol: TCP
      # TODO: Specify the named port 'http'.
      # WHY: Allows port indirection so changes to container port numbers do not break network policy enforcement.
      port: ???
"""


def is_ip_in_ipblock(ip_str: str, cidr_str: str, except_cidrs: List[str]) -> bool:
    """Check if an IP address is inside the cidr range and outside all except ranges."""
    # TODO: Implement ipaddress checking logic to verify IP inclusion in cidr_str and exclusion from except_cidrs.
    # WHY: Simulates the CNI packet filter matching algorithm for CIDR boundary evaluation.
    return False


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

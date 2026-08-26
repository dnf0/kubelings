"""
Exercise: solutions/09_network_policies/netpol03.py
Topic: Egress Traffic & DNS Access

Reference Solution
"""

import yaml

from kubelings.validator import validate_manifest

POLICY_MANIFEST = """
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-frontend-egress
  namespace: default
spec:
  podSelector:
    matchLabels:
      app: frontend
  policyTypes:
  - Egress
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: kube-system
    ports:
    - protocol: UDP
      port: 53
    - protocol: TCP
      port: 53
  - to:
    - podSelector:
        matchLabels:
          app: backend
    ports:
    - protocol: TCP
      port: 8080
"""


def verify():
    manifest = yaml.safe_load(POLICY_MANIFEST)
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(
        manifest, expected_kind="NetworkPolicy", expected_api_version="networking.k8s.io/v1"
    )

    assert manifest["metadata"]["name"] == "allow-frontend-egress"
    assert manifest["metadata"]["namespace"] == "default"

    spec = manifest.get("spec", {})
    assert spec.get("podSelector", {}).get("matchLabels", {}).get("app") == "frontend"
    assert spec.get("policyTypes") == ["Egress"]

    egress_rules = spec.get("egress", [])
    assert len(egress_rules) == 2, "Must define exactly 2 egress rules (DNS and Backend API)"

    # Rule 1: DNS
    r1 = egress_rules[0]
    assert (
        r1["to"][0]["namespaceSelector"]["matchLabels"]["kubernetes.io/metadata.name"]
        == "kube-system"
    )
    dns_ports = {(p["protocol"], p["port"]) for p in r1["ports"]}
    assert ("UDP", 53) in dns_ports, "DNS rule must allow UDP port 53"
    assert ("TCP", 53) in dns_ports, "DNS rule must allow TCP port 53"

    # Rule 2: Backend API
    r2 = egress_rules[1]
    assert r2["to"][0]["podSelector"]["matchLabels"]["app"] == "backend"
    assert r2["ports"][0]["port"] == 8080
    assert r2["ports"][0]["protocol"] == "TCP"

    print("✓ netpol03 passed!")


if __name__ == "__main__":
    verify()

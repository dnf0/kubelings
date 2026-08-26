"""
Exercise: exercises/09_network_policies/netpol03.py
Topic: Egress Traffic & DNS Access

Instructions:
When egress filtering is enabled in a Kubernetes namespace, pods cannot initiate outbound
connections—including DNS resolution via CoreDNS—unless explicitly allowed.

1. Configure NetworkPolicy 'allow-frontend-egress' in namespace 'default':
   - Targets pods with label `app: frontend`.
   - Egress Rule 1 (DNS): Allow port 53 (UDP and TCP) to namespace labeled
     `kubernetes.io/metadata.name: kube-system`.
   - Egress Rule 2 (Backend API): Allow TCP port 8080 to pods with label `app: backend` (same namespace).
"""

# I AM NOT DONE

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
          kubernetes.io/metadata.name: ???
    ports:
    - protocol: UDP
      port: ???
    - protocol: TCP
      port: ???
  - to:
    - podSelector:
        matchLabels:
          app: ???
    ports:
    - protocol: TCP
      port: ???
"""


def verify():
    manifest = yaml.safe_load(POLICY_MANIFEST)
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(manifest, expected_kind="NetworkPolicy", expected_api_version="networking.k8s.io/v1")

    assert manifest["metadata"]["name"] == "allow-frontend-egress"
    assert manifest["metadata"]["namespace"] == "default"

    spec = manifest.get("spec", {})
    assert spec.get("podSelector", {}).get("matchLabels", {}).get("app") == "frontend"
    assert spec.get("policyTypes") == ["Egress"]

    egress_rules = spec.get("egress", [])
    assert len(egress_rules) == 2, "Must define exactly 2 egress rules (DNS and Backend API)"

    # Rule 1: DNS
    r1 = egress_rules[0]
    assert r1["to"][0]["namespaceSelector"]["matchLabels"]["kubernetes.io/metadata.name"] == "kube-system"
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

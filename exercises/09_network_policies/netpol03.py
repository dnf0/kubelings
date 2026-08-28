"""
Exercise: exercises/09_network_policies/netpol03.py
Topic: Egress Traffic & DNS Access

Context & Why:
When Egress filtering is activated on a workload, the CNI network plugin blocks all outbound packets
not matching an explicit allow rule. A notorious production incident pattern occurs when egress policies
are applied without whitelisting cluster DNS: pods immediately lose the ability to resolve service names
(such as `database.default.svc.cluster.local`), causing catastrophic application timeouts. To avoid outages,
egress-filtered pods must explicitly allow port 53 (over both UDP and TCP) to CoreDNS pods in the
`kube-system` namespace, alongside application-specific egress rules to downstream backend services.

Instructions:
1. Configure NetworkPolicy 'allow-frontend-egress' in namespace 'default':
   - Targets pods with label `app: frontend`.
   - Egress Rule 1 (DNS): Allow port 53 (UDP and TCP) to namespace labeled
     `kubernetes.io/metadata.name: kube-system`.
   - Egress Rule 2 (Backend API): Allow TCP port 8080 to pods with label `app: backend` (same namespace).
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
          # TODO: Match the 'kube-system' namespace name label.
          # WHY: CoreDNS instances run in the kube-system namespace to provide in-cluster DNS resolution.
          kubernetes.io/metadata.name: ???
    ports:
    # TODO: Allow DNS traffic on UDP port 53.
    # WHY: Standard DNS query packets are transmitted over UDP port 53.
    - protocol: UDP
      port: ???
    # TODO: Allow DNS traffic on TCP port 53.
    # WHY: Large DNS responses or zone transfers fall back to TCP port 53.
    - protocol: TCP
      port: ???
  - to:
    - podSelector:
        matchLabels:
          # TODO: Match destination pods with label 'app: backend'.
          # WHY: Restricts frontend outbound application calls strictly to the backend API service.
          app: ???
    ports:
    # TODO: Allow backend API port 8080 over TCP.
    # WHY: Authorizes the HTTP REST API transport channel between frontend and backend.
    - protocol: TCP
      port: ???
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

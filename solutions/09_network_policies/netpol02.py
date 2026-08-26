"""
Exercise: solutions/09_network_policies/netpol02.py
Topic: Ingress Traffic Filtering

Reference Solution
"""

from typing import Any, Dict
import yaml
from kubelings.validator import validate_manifest

POLICY_MANIFEST = """
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-database-ingress
  namespace: production
spec:
  podSelector:
    matchLabels:
      role: database
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          role: backend-api
    ports:
    - protocol: TCP
      port: 5432
  - from:
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: monitoring
    ports:
    - protocol: TCP
      port: 9187
"""


def check_ingress_allowed(
    policy: Dict[str, Any],
    source_pod_labels: Dict[str, str],
    source_namespace_labels: Dict[str, str],
    destination_port: int,
    protocol: str = "TCP",
) -> bool:
    """Determine whether an ingress rule in the policy allows traffic from the source."""
    spec = policy.get("spec", {})
    ingress_rules = spec.get("ingress", [])

    for rule in ingress_rules:
        # Check ports
        ports = rule.get("ports", [])
        port_matched = True
        if ports:
            port_matched = any(
                p.get("port") == destination_port and p.get("protocol", "TCP").upper() == protocol.upper()
                for p in ports
            )

        if not port_matched:
            continue

        # Check from sources
        from_list = rule.get("from", [])
        if not from_list:
            return True

        for from_entry in from_list:
            pod_sel = from_entry.get("podSelector")
            ns_sel = from_entry.get("namespaceSelector")

            pod_matches = True
            if pod_sel is not None:
                match_labels = pod_sel.get("matchLabels", {})
                pod_matches = all(source_pod_labels.get(k) == v for k, v in match_labels.items())

            ns_matches = True
            if ns_sel is not None:
                match_labels = ns_sel.get("matchLabels", {})
                ns_matches = all(source_namespace_labels.get(k) == v for k, v in match_labels.items())

            if pod_matches and ns_matches:
                return True

    return False


def verify():
    manifest = yaml.safe_load(POLICY_MANIFEST)
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(manifest, expected_kind="NetworkPolicy", expected_api_version="networking.k8s.io/v1")

    assert manifest["metadata"]["name"] == "allow-database-ingress"
    assert manifest["metadata"]["namespace"] == "production"

    spec = manifest.get("spec", {})
    assert spec.get("podSelector", {}).get("matchLabels", {}).get("role") == "database"
    assert spec.get("policyTypes") == ["Ingress"]

    ingress_rules = spec.get("ingress", [])
    assert len(ingress_rules) == 2

    r1 = ingress_rules[0]
    assert r1["from"][0]["podSelector"]["matchLabels"]["role"] == "backend-api"
    assert r1["ports"][0]["port"] == 5432
    assert r1["ports"][0]["protocol"] == "TCP"

    r2 = ingress_rules[1]
    assert r2["from"][0]["namespaceSelector"]["matchLabels"]["kubernetes.io/metadata.name"] == "monitoring"
    assert r2["ports"][0]["port"] == 9187
    assert r2["ports"][0]["protocol"] == "TCP"

    # Test ingress evaluation
    backend_pod = {"role": "backend-api", "app": "store"}
    prod_ns = {"kubernetes.io/metadata.name": "production"}
    mon_pod = {"app": "prometheus"}
    mon_ns = {"kubernetes.io/metadata.name": "monitoring"}
    unauthorized_pod = {"role": "guest", "app": "public"}

    # Allowed cases
    assert check_ingress_allowed(manifest, backend_pod, prod_ns, 5432, "TCP") is True
    assert check_ingress_allowed(manifest, mon_pod, mon_ns, 9187, "TCP") is True

    # Denied cases
    assert check_ingress_allowed(manifest, backend_pod, prod_ns, 8080, "TCP") is False, "Wrong port"
    assert check_ingress_allowed(manifest, backend_pod, prod_ns, 5432, "UDP") is False, "Wrong protocol"
    assert check_ingress_allowed(manifest, unauthorized_pod, prod_ns, 5432, "TCP") is False, "Unauthorized pod label"
    assert check_ingress_allowed(manifest, mon_pod, prod_ns, 9187, "TCP") is False, "Wrong namespace for monitoring port"

    print("✓ netpol02 passed!")


if __name__ == "__main__":
    verify()

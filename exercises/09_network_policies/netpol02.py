"""
Exercise: exercises/09_network_policies/netpol02.py
Topic: Ingress Traffic Filtering

Context & Why:
In multi-tier Kubernetes architectures, stateful components like relational databases should never
be directly reachable from all pods in a cluster. NetworkPolicy Ingress rules define explicit ingress
filters for selected workloads. Traffic sources can be scoped to specific pods within the same namespace
via `podSelector`, across namespaces via `namespaceSelector`, or both. Restricting ingress by label,
transport protocol (TCP/UDP), and destination port ensures only verified backend API servers and authorized
monitoring agents can establish network connections to sensitive database ports.

Instructions:
1. Configure NetworkPolicy 'allow-database-ingress' in namespace 'production':
   - Targets pods with label `role: database`.
   - Ingress Rule 1: Allow TCP port 5432 from pods with label `role: backend-api` (same namespace).
   - Ingress Rule 2: Allow TCP port 9187 from any pod in namespaces labeled `kubernetes.io/metadata.name: monitoring`.
2. Implement `check_ingress_allowed(policy, source_pod_labels, source_namespace_labels, destination_port, protocol)`:
   - Returns True if any ingress rule allows the given source labels, destination port, and protocol.
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
          # TODO: Match source pods with role 'backend-api'.
          # WHY: Restricts application traffic exclusively to verified backend tier services.
          role: ???
    ports:
    - protocol: TCP
      # TODO: Specify target PostgreSQL port 5432.
      # WHY: Prevents source pods from connecting to unintended management or debug ports.
      port: ???
  - from:
    - namespaceSelector:
        matchLabels:
          # TODO: Match source namespaces with name 'monitoring'.
          # WHY: Allows Prometheus or monitoring scrapers in the monitoring namespace to connect across namespace boundaries.
          kubernetes.io/metadata.name: ???
    ports:
    - protocol: TCP
      # TODO: Specify target Postgres metrics exporter port 9187.
      # WHY: Isolates monitoring telemetry scraping to its dedicated metrics endpoint.
      port: ???
"""


def check_ingress_allowed(
    policy: Dict[str, Any],
    source_pod_labels: Dict[str, str],
    source_namespace_labels: Dict[str, str],
    destination_port: int,
    protocol: str = "TCP",
) -> bool:
    """Determine whether an ingress rule in the policy allows traffic from the source."""
    # TODO: Implement ingress rule evaluation that checks if any rule matches the source pod/namespace labels and port/protocol.
    # WHY: CNI packet filtering engines evaluate ingress rules in sequential disjunction (OR) to allow matching traffic streams.
    return False


def verify():
    manifest = yaml.safe_load(POLICY_MANIFEST)
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(
        manifest, expected_kind="NetworkPolicy", expected_api_version="networking.k8s.io/v1"
    )

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
    assert (
        r2["from"][0]["namespaceSelector"]["matchLabels"]["kubernetes.io/metadata.name"]
        == "monitoring"
    )
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
    assert check_ingress_allowed(manifest, backend_pod, prod_ns, 5432, "UDP") is False, (
        "Wrong protocol"
    )
    assert check_ingress_allowed(manifest, unauthorized_pod, prod_ns, 5432, "TCP") is False, (
        "Unauthorized pod label"
    )
    assert check_ingress_allowed(manifest, mon_pod, prod_ns, 9187, "TCP") is False, (
        "Wrong namespace for monitoring port"
    )

    print("✓ netpol02 passed!")


if __name__ == "__main__":
    verify()

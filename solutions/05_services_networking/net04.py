"""
Exercise: solutions/05_services_networking/net04.py
Topic: CoreDNS Internal Service Resolution

Reference Solution
"""

from typing import Optional
import yaml
from kubelings.validator import validate_manifest

POD_MANIFEST = """
apiVersion: v1
kind: Pod
metadata:
  name: dns-client-pod
spec:
  dnsPolicy: ClusterFirst
  dnsConfig:
    searches:
      - custom.corp.local
      - default.svc.cluster.local
    options:
      - name: ndots
        value: "2"
  containers:
  - name: client
    image: curlimages/curl:8.6.0
    command: ["sh", "-c", "sleep 3600"]
"""


def build_kubernetes_dns_query(
    service_name: str,
    namespace: str = "default",
    port_name: Optional[str] = None,
    protocol: Optional[str] = None,
    cluster_domain: str = "cluster.local",
) -> str:
    """Build the expected CoreDNS query hostname for a service or SRV endpoint."""
    if port_name and protocol:
        return f"_{port_name}._{protocol.lower()}.{service_name}.{namespace}.svc.{cluster_domain}"
    return f"{service_name}.{namespace}.svc.{cluster_domain}"


def verify():
    manifest = yaml.safe_load(POD_MANIFEST)
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(manifest, expected_kind="Pod", expected_api_version="v1")

    assert manifest["metadata"]["name"] == "dns-client-pod"
    assert manifest["spec"]["dnsPolicy"] == "ClusterFirst"
    searches = manifest["spec"]["dnsConfig"]["searches"]
    assert "custom.corp.local" in searches
    assert "default.svc.cluster.local" in searches

    # Test standard A-record query
    a_rec = build_kubernetes_dns_query(service_name="payment-api", namespace="billing")
    assert a_rec == "payment-api.billing.svc.cluster.local"

    # Test SRV-record query
    srv_rec = build_kubernetes_dns_query(
        service_name="grpc-orders",
        namespace="sales",
        port_name="grpc",
        protocol="tcp",
    )
    assert srv_rec == "_grpc._tcp.grpc-orders.sales.svc.cluster.local"

    print("✓ net04 passed!")


if __name__ == "__main__":
    verify()

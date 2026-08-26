"""
Exercise: exercises/05_services_networking/net04.py
Topic: CoreDNS Internal Service Resolution

Instructions:
CoreDNS provides internal service discovery.
1. Standard Service A-record format:
   `<service-name>.<namespace>.svc.<cluster-domain>`
2. Named port SRV-record format:
   `_<port-name>._<protocol>.<service-name>.<namespace>.svc.<cluster-domain>`

1. Complete the Pod manifest with custom DNS configuration:
   - name: 'dns-client-pod'
   - dnsPolicy: 'ClusterFirst'
   - dnsConfig.searches: ['custom.corp.local', 'default.svc.cluster.local']
   - dnsConfig.options: [{name: 'ndots', value: '2'}]
2. Implement `build_kubernetes_dns_query`:
   - If `port_name` and `protocol` are provided, return the SRV record format.
   - Otherwise, return the standard Service FQDN.
"""

# I AM NOT DONE

from typing import Optional

import yaml

from kubelings.validator import validate_manifest

POD_MANIFEST = """
apiVersion: v1
kind: Pod
metadata:
  name: dns-client-pod
spec:
  dnsPolicy: ???
  dnsConfig:
    searches:
      - ???
      - ???
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
    # TODO: Implement DNS query builder
    return ""


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

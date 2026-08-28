"""
Exercise: exercises/05_services_networking/net02.py
Topic: Headless Services & Stateful Addressing

Context & Why:
Standard Services provide a single virtual ClusterIP that randomly proxies connections across pods.
However, distributed stateful clusters (such as Cassandra, Kafka, Elasticsearch, Redis Sentinel, or Zookeeper)
need direct peer-to-peer communication and discovery between specific cluster members.
Setting `spec.clusterIP: "None"` defines a "Headless" Service. Instead of allocating a virtual IP,
CoreDNS answers queries for a headless service with A/AAAA records pointing directly to the individual backing Pod IPs.
When linked with a StatefulSet, every ordinal pod receives a stable, globally resolvable Fully Qualified Domain Name (FQDN)
formatted as `<pod-name>.<service-name>.<namespace>.svc.<cluster-domain>`.

Instructions:
A Headless Service is created by setting `spec.clusterIP: "None"`.
Instead of load balancing through a single virtual IP, CoreDNS directly returns
A/AAAA DNS records for individual backing Pod IPs.

When paired with a StatefulSet, each Pod receives a predictable, stable FQDN:
`<pod-name>.<service-name>.<namespace>.svc.<cluster-domain>`

1. Complete the Headless Service manifest:
   - name: 'cassandra-headless' in namespace 'databases'
   - clusterIP: 'None'
   - selector: {app: 'cassandra'}
   - ports: name 'cql', port 9042, targetPort 9042
2. Implement `generate_stateful_dns_records`:
   - Returns a list of FQDN strings for `replicas` statefulset pods (index 0 to replicas-1).
"""

from typing import List

import yaml

from kubelings.validator import validate_manifest

HEADLESS_SERVICE_MANIFEST = """
apiVersion: v1
kind: Service
metadata:
  name: cassandra-headless
  namespace: databases
spec:
  # TODO: Set clusterIP to 'None'
  # WHY: Setting clusterIP: None disables the virtual IP proxy and configures CoreDNS to return direct A-records for member pods.
  clusterIP: ???
  selector:
    app: cassandra
  ports:
  - name: cql
    protocol: TCP
    # TODO: Set both port and targetPort to 9042
    # WHY: Standard native CQL protocol port used for peer communication in Apache Cassandra clusters.
    port: 0
    targetPort: 0
"""


def generate_stateful_dns_records(
    service_name: str,
    statefulset_name: str,
    replicas: int,
    namespace: str = "default",
    cluster_domain: str = "cluster.local",
) -> List[str]:
    """Generate predictable DNS hostnames for StatefulSet pods with a headless service."""
    # TODO: Implement DNS record generation formatted as <pod>.<service>.<namespace>.svc.<domain>
    # WHY: Models the exact Kubernetes DNS convention for StatefulSet headless service resolution.
    return []


def verify():
    manifest = yaml.safe_load(HEADLESS_SERVICE_MANIFEST)
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(manifest, expected_kind="Service", expected_api_version="v1")

    assert manifest["metadata"]["name"] == "cassandra-headless"
    assert manifest["metadata"]["namespace"] == "databases"
    assert manifest["spec"]["clusterIP"] == "None", (
        "Headless service requires spec.clusterIP: 'None'"
    )
    assert manifest["spec"]["selector"] == {"app": "cassandra"}

    port = manifest["spec"]["ports"][0]
    assert port["name"] == "cql"
    assert port["port"] == 9042
    assert port["targetPort"] == 9042

    records = generate_stateful_dns_records(
        service_name="cassandra-headless",
        statefulset_name="cassandra",
        replicas=3,
        namespace="databases",
    )
    expected = [
        "cassandra-0.cassandra-headless.databases.svc.cluster.local",
        "cassandra-1.cassandra-headless.databases.svc.cluster.local",
        "cassandra-2.cassandra-headless.databases.svc.cluster.local",
    ]
    assert records == expected, f"Expected {expected}, got {records}"

    print("✓ net02 passed!")


if __name__ == "__main__":
    verify()

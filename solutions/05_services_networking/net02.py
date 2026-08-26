"""
Exercise: solutions/05_services_networking/net02.py
Topic: Headless Services & Stateful Addressing

Reference Solution
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
  clusterIP: "None"
  selector:
    app: cassandra
  ports:
  - name: cql
    protocol: TCP
    port: 9042
    targetPort: 9042
"""


def generate_stateful_dns_records(
    service_name: str,
    statefulset_name: str,
    replicas: int,
    namespace: str = "default",
    cluster_domain: str = "cluster.local",
) -> List[str]:
    """Generate predictable DNS hostnames for StatefulSet pods with a headless service."""
    return [
        f"{statefulset_name}-{i}.{service_name}.{namespace}.svc.{cluster_domain}"
        for i in range(replicas)
    ]


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

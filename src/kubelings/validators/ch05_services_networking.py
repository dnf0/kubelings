"""
Validators for Chapter 05: Services & Networking
"""

from typing import Any, Dict, List, Optional

import yaml

from kubelings.validator import validate_manifest, validate_manifests
from kubelings.validators import register_validator


def resolve_endpoint_target(
    service_manifest: Dict[str, Any], pod_manifest: Dict[str, Any]
) -> Optional[int]:
    """Check if a pod matches the service selector and return the targetPort."""
    selector = service_manifest.get("spec", {}).get("selector", {})
    if not selector:
        return None
    pod_labels = pod_manifest.get("metadata", {}).get("labels", {})
    for k, v in selector.items():
        if pod_labels.get(k) != v:
            return None
    ports = service_manifest.get("spec", {}).get("ports", [])
    if ports:
        return ports[0].get("targetPort", ports[0].get("port"))
    return None


@register_validator("net01")
def validate_net01(manifest: Any, raw_yaml: str = "") -> None:
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(manifest, expected_kind="Service", expected_api_version="v1")
    assert manifest["metadata"]["name"] == "backend-service"
    assert manifest["spec"]["type"] == "ClusterIP"
    assert manifest["spec"]["selector"] == {"app": "backend", "tier": "api"}
    ports = manifest["spec"]["ports"]
    assert len(ports) == 1
    assert ports[0]["name"] == "http"
    assert ports[0]["protocol"] == "TCP"
    assert ports[0]["port"] == 80
    assert ports[0]["targetPort"] == 8080
    matching_pod = {
        "metadata": {
            "name": "backend-pod-1",
            "labels": {"app": "backend", "tier": "api", "version": "v1.2"},
        }
    }
    non_matching_pod = {
        "metadata": {"name": "frontend-pod-1", "labels": {"app": "frontend", "tier": "ui"}}
    }
    assert resolve_endpoint_target(manifest, matching_pod) == 8080
    assert resolve_endpoint_target(manifest, non_matching_pod) is None


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


@register_validator("net02")
def validate_net02(manifest: Any, raw_yaml: str = "") -> None:
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


def validate_node_port_range(port: int) -> bool:
    """Validate whether port falls within standard Kubernetes NodePort range (30000-32767)."""
    return 30000 <= port <= 32767


@register_validator("net03")
def validate_net03(manifest: Any, raw_yaml: str = "") -> None:
    manifests = manifest if isinstance(manifest, list) else [manifest]
    assert len(manifests) == 2, "Must define 2 services (NodePort and LoadBalancer)"
    validate_manifests(manifests, expected_kinds=["Service", "Service"])
    np_svc, lb_svc = (manifests[0], manifests[1])
    assert np_svc["metadata"]["name"] == "frontend-np"
    assert np_svc["spec"]["type"] == "NodePort"
    assert np_svc["spec"]["ports"][0]["nodePort"] == 30080
    assert validate_node_port_range(np_svc["spec"]["ports"][0]["nodePort"]) is True
    assert lb_svc["metadata"]["name"] == "frontend-lb"
    assert lb_svc["spec"]["type"] == "LoadBalancer"
    assert lb_svc["spec"]["ports"][0]["port"] == 443
    assert lb_svc["spec"]["ports"][0]["targetPort"] == 8443
    assert "192.168.0.0/16" in lb_svc["spec"]["loadBalancerSourceRanges"]
    assert validate_node_port_range(30000) is True
    assert validate_node_port_range(32767) is True
    assert validate_node_port_range(80) is False
    assert validate_node_port_range(29999) is False
    assert validate_node_port_range(32768) is False


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


@register_validator("net04")
def validate_net04(manifest: Any, raw_yaml: str = "") -> None:
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(manifest, expected_kind="Pod", expected_api_version="v1")
    assert manifest["metadata"]["name"] == "dns-client-pod"
    assert manifest["spec"]["dnsPolicy"] == "ClusterFirst"
    searches = manifest["spec"]["dnsConfig"]["searches"]
    assert "custom.corp.local" in searches
    assert "default.svc.cluster.local" in searches
    a_rec = build_kubernetes_dns_query(service_name="payment-api", namespace="billing")
    assert a_rec == "payment-api.billing.svc.cluster.local"
    srv_rec = build_kubernetes_dns_query(
        service_name="grpc-orders", namespace="sales", port_name="grpc", protocol="tcp"
    )
    assert srv_rec == "_grpc._tcp.grpc-orders.sales.svc.cluster.local"


MANIFESTS = "\napiVersion: v1\nkind: Service\nmetadata:\n  name: external-database\nspec:\n  type: ExternalName\n  externalName: db.production.aws.rds.com\n---\napiVersion: v1\nkind: Service\nmetadata:\n  name: legacy-crm\nspec:\n  ports:\n  - name: http\n    port: 80\n    targetPort: 8080\n---\napiVersion: v1\nkind: Endpoints\nmetadata:\n  name: legacy-crm\nsubsets:\n- addresses:\n  - ip: 10.240.0.15\n  - ip: 10.240.0.16\n  ports:\n  - name: http\n    port: 8080\n"


def validate_endpoints_match_service(service: Dict[str, Any], endpoints: Dict[str, Any]) -> bool:
    """Verify that a manual Endpoints object matches its corresponding Service definition."""
    svc_name = service.get("metadata", {}).get("name")
    ep_name = endpoints.get("metadata", {}).get("name")
    if not svc_name or svc_name != ep_name:
        return False
    svc_ports = {
        p.get("targetPort", p.get("port")) for p in service.get("spec", {}).get("ports", [])
    }
    ep_ports = set()
    for subset in endpoints.get("subsets", []):
        for p in subset.get("ports", []):
            ep_ports.add(p.get("port"))
    return bool(svc_ports.intersection(ep_ports))


@register_validator("net05")
def validate_net05(manifest: Any, raw_yaml: str = "") -> None:
    manifests = manifest if isinstance(manifest, list) else [manifest]
    assert len(manifests) == 3, (
        "Must define 3 manifests (ExternalName Svc, Selectorless Svc, Endpoints)"
    )
    validate_manifests(manifests, expected_kinds=["Service", "Service", "Endpoints"])
    ext_svc, crm_svc, endpoints = (manifests[0], manifests[1], manifests[2])
    assert ext_svc["metadata"]["name"] == "external-database"
    assert ext_svc["spec"]["type"] == "ExternalName"
    assert ext_svc["spec"]["externalName"] == "db.production.aws.rds.com"
    assert crm_svc["metadata"]["name"] == "legacy-crm"
    assert "selector" not in crm_svc.get("spec", {}), "Service must be selectorless"
    assert endpoints["metadata"]["name"] == "legacy-crm"
    addresses = [a["ip"] for a in endpoints["subsets"][0]["addresses"]]
    assert "10.240.0.15" in addresses
    assert "10.240.0.16" in addresses
    assert endpoints["subsets"][0]["ports"][0]["port"] == 8080
    assert validate_endpoints_match_service(crm_svc, endpoints) is True
    bad_ep = yaml.safe_load(yaml.dump(endpoints))
    bad_ep["metadata"]["name"] = "other-service"
    assert validate_endpoints_match_service(crm_svc, bad_ep) is False

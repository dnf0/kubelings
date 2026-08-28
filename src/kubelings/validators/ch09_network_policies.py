"""
Validators for Chapter 09: Network Policies & Traffic Segmentation
"""

import ipaddress
from typing import Any, Dict, List

from kubelings.validator import validate_manifest
from kubelings.validators import register_validator


@register_validator("netpol01")
def validate_netpol01(manifest: Any, raw_yaml: str = "") -> None:
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(
        manifest, expected_kind="NetworkPolicy", expected_api_version="networking.k8s.io/v1"
    )
    assert manifest["metadata"]["name"] == "default-deny-all"
    assert manifest["metadata"]["namespace"] == "production"
    spec = manifest.get("spec", {})
    assert spec.get("podSelector") == {}, (
        "podSelector must be an empty dict {} to match all pods in namespace"
    )
    assert set(spec.get("policyTypes", [])) == {"Ingress", "Egress"}, (
        "policyTypes must include both 'Ingress' and 'Egress'"
    )
    assert "ingress" not in spec or len(spec.get("ingress", [])) == 0, (
        "Default deny must not define allow ingress rules"
    )
    assert "egress" not in spec or len(spec.get("egress", [])) == 0, (
        "Default deny must not define allow egress rules"
    )


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
        ports = rule.get("ports", [])
        port_matched = True
        if ports:
            port_matched = any(
                (
                    p.get("port") == destination_port
                    and p.get("protocol", "TCP").upper() == protocol.upper()
                    for p in ports
                )
            )
        if not port_matched:
            continue
        from_list = rule.get("from", [])
        if not from_list:
            return True
        for from_entry in from_list:
            pod_sel = from_entry.get("podSelector")
            ns_sel = from_entry.get("namespaceSelector")
            pod_matches = True
            if pod_sel is not None:
                match_labels = pod_sel.get("matchLabels", {})
                pod_matches = all((source_pod_labels.get(k) == v for k, v in match_labels.items()))
            ns_matches = True
            if ns_sel is not None:
                match_labels = ns_sel.get("matchLabels", {})
                ns_matches = all(
                    (source_namespace_labels.get(k) == v for k, v in match_labels.items())
                )
            if pod_matches and ns_matches:
                return True
    return False


@register_validator("netpol02")
def validate_netpol02(manifest: Any, raw_yaml: str = "") -> None:
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
    backend_pod = {"role": "backend-api", "app": "store"}
    prod_ns = {"kubernetes.io/metadata.name": "production"}
    mon_pod = {"app": "prometheus"}
    mon_ns = {"kubernetes.io/metadata.name": "monitoring"}
    unauthorized_pod = {"role": "guest", "app": "public"}
    assert check_ingress_allowed(manifest, backend_pod, prod_ns, 5432, "TCP") is True
    assert check_ingress_allowed(manifest, mon_pod, mon_ns, 9187, "TCP") is True
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


@register_validator("netpol03")
def validate_netpol03(manifest: Any, raw_yaml: str = "") -> None:
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
    r1 = egress_rules[0]
    assert (
        r1["to"][0]["namespaceSelector"]["matchLabels"]["kubernetes.io/metadata.name"]
        == "kube-system"
    )
    dns_ports = {(p["protocol"], p["port"]) for p in r1["ports"]}
    assert ("UDP", 53) in dns_ports, "DNS rule must allow UDP port 53"
    assert ("TCP", 53) in dns_ports, "DNS rule must allow TCP port 53"
    r2 = egress_rules[1]
    assert r2["to"][0]["podSelector"]["matchLabels"]["app"] == "backend"
    assert r2["ports"][0]["port"] == 8080
    assert r2["ports"][0]["protocol"] == "TCP"


def is_ip_in_ipblock(ip_str: str, cidr_str: str, except_cidrs: List[str]) -> bool:
    """Check if an IP address is inside the cidr range and outside all except ranges."""
    ip = ipaddress.ip_address(ip_str)
    main_network = ipaddress.ip_network(cidr_str)
    if ip not in main_network:
        return False
    for exc in except_cidrs:
        if ip in ipaddress.ip_network(exc):
            return False
    return True


@register_validator("netpol04")
def validate_netpol04(manifest: Any, raw_yaml: str = "") -> None:
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(
        manifest, expected_kind="NetworkPolicy", expected_api_version="networking.k8s.io/v1"
    )
    assert manifest["metadata"]["name"] == "external-api-egress"
    assert manifest["metadata"]["namespace"] == "default"
    spec = manifest.get("spec", {})
    assert spec.get("podSelector", {}).get("matchLabels", {}).get("app") == "gateway"
    assert spec.get("policyTypes") == ["Egress"]
    egress = spec.get("egress", [])
    assert len(egress) == 1
    rule = egress[0]
    to_block = rule["to"][0]["ipBlock"]
    assert to_block["cidr"] == "192.168.0.0/16"
    assert to_block["except"] == ["192.168.1.0/24"]
    port = rule["ports"][0]
    assert port["protocol"] == "TCP"
    assert port["port"] == "http"
    assert is_ip_in_ipblock("192.168.0.50", "192.168.0.0/16", ["192.168.1.0/24"]) is True
    assert is_ip_in_ipblock("192.168.2.100", "192.168.0.0/16", ["192.168.1.0/24"]) is True
    assert is_ip_in_ipblock("192.168.1.15", "192.168.0.0/16", ["192.168.1.0/24"]) is False, (
        "Excluded by exception subnet"
    )
    assert is_ip_in_ipblock("10.0.0.1", "192.168.0.0/16", ["192.168.1.0/24"]) is False, (
        "Outside CIDR"
    )

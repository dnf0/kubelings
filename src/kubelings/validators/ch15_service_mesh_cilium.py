"""
Validators for Chapter 15: Service Mesh, eBPF & Cilium
"""

from typing import Any, Dict

from kubelings.validators import register_validator


def get_cilium_l7_policy() -> Dict[str, Any]:
    return {
        "apiVersion": "cilium.io/v2",
        "kind": "CiliumNetworkPolicy",
        "metadata": {"name": "secure-api-l7"},
        "spec": {
            "endpointSelector": {"matchLabels": {"app": "secure-backend"}},
            "ingress": [
                {
                    "fromEndpoints": [{"matchLabels": {"app": "frontend"}}],
                    "toPorts": [
                        {
                            "ports": [{"port": "8080", "protocol": "TCP"}],
                            "rules": {
                                "http": [
                                    {"method": "GET", "path": "/api/v1/public/.*"},
                                    {
                                        "method": "POST",
                                        "path": "/api/v1/orders",
                                        "headers": ["X-Client-Role: authorized"],
                                    },
                                ]
                            },
                        }
                    ],
                }
            ],
        },
    }


@register_validator("mesh01")
def validate_mesh01(manifest: Any, raw_yaml: str = "") -> None:
    policy = manifest
    assert policy, "Policy cannot be empty"
    assert policy.get("apiVersion") == "cilium.io/v2"
    assert policy.get("kind") == "CiliumNetworkPolicy"
    meta = policy.get("metadata", {})
    assert meta.get("name") == "secure-api-l7"
    spec = policy.get("spec", {})
    endpoint = spec.get("endpointSelector", {})
    assert endpoint.get("matchLabels", {}).get("app") == "secure-backend"
    ingress = spec.get("ingress", [])
    assert len(ingress) > 0
    from_ep = ingress[0].get("fromEndpoints", [])
    assert from_ep[0].get("matchLabels", {}).get("app") == "frontend"
    to_ports = ingress[0].get("toPorts", [])
    assert len(to_ports) > 0
    ports = to_ports[0].get("ports", [])
    assert ports[0].get("port") == "8080"
    assert ports[0].get("protocol") == "TCP"
    http_rules = to_ports[0].get("rules", {}).get("http", [])
    assert len(http_rules) == 2
    assert http_rules[0].get("method") == "GET"
    assert http_rules[1].get("method") == "POST"


def get_peer_authentication_manifest() -> Dict[str, Any]:
    return {
        "apiVersion": "security.istio.io/v1beta1",
        "kind": "PeerAuthentication",
        "metadata": {"name": "default", "namespace": "production"},
        "spec": {"mtls": {"mode": "STRICT"}},
    }


@register_validator("mesh02")
def validate_mesh02(manifest: Any, raw_yaml: str = "") -> None:
    manifest = manifest
    assert manifest, "Manifest cannot be empty"
    assert manifest.get("apiVersion") == "security.istio.io/v1beta1"
    assert manifest.get("kind") == "PeerAuthentication"
    meta = manifest.get("metadata", {})
    assert meta.get("name") == "default"
    assert meta.get("namespace") == "production"
    spec = manifest.get("spec", {})
    mtls = spec.get("mtls", {})
    assert mtls.get("mode") == "STRICT", "Expected mtls.mode to be 'STRICT'"


def get_clusterwide_egress_policy() -> Dict[str, Any]:
    return {
        "apiVersion": "cilium.io/v2",
        "kind": "CiliumClusterwideNetworkPolicy",
        "metadata": {"name": "secure-external-egress"},
        "spec": {
            "nodeSelector": {"matchLabels": {}},
            "egress": [
                {
                    "toFQDNs": [
                        {"matchName": "api.github.com"},
                        {"matchPattern": "*.amazonaws.com"},
                    ],
                    "toPorts": [
                        {
                            "ports": [{"port": "443", "protocol": "TCP"}],
                            "rules": {"dns": [{"matchPattern": "*"}]},
                        }
                    ],
                }
            ],
        },
    }


@register_validator("mesh03")
def validate_mesh03(manifest: Any, raw_yaml: str = "") -> None:
    policy = manifest
    assert policy, "Policy cannot be empty"
    assert policy.get("apiVersion") == "cilium.io/v2"
    assert policy.get("kind") == "CiliumClusterwideNetworkPolicy"
    meta = policy.get("metadata", {})
    assert meta.get("name") == "secure-external-egress"
    spec = policy.get("spec", {})
    egress = spec.get("egress", [])
    assert len(egress) > 0
    to_fqdns = egress[0].get("toFQDNs", [])
    assert any((f.get("matchName") == "api.github.com" for f in to_fqdns))
    assert any((f.get("matchPattern") == "*.amazonaws.com" for f in to_fqdns))
    to_ports = egress[0].get("toPorts", [])
    assert len(to_ports) > 0
    assert to_ports[0].get("ports", [{}])[0].get("port") == "443"


def get_observable_pod_manifest() -> Dict[str, Any]:
    return {
        "apiVersion": "v1",
        "kind": "Pod",
        "metadata": {
            "name": "order-service",
            "annotations": {
                "sidecar.istio.io/inject": "false",
                "prometheus.io/scrape": "true",
                "prometheus.io/port": "9090",
                "telemetry.cilium.io/trace": "b3",
            },
        },
        "spec": {
            "containers": [
                {"name": "order-api", "image": "orders:v1.0", "ports": [{"containerPort": 9090}]}
            ]
        },
    }


@register_validator("mesh04")
def validate_mesh04(manifest: Any, raw_yaml: str = "") -> None:
    manifest = manifest
    assert manifest, "Manifest cannot be empty"
    assert manifest.get("apiVersion") == "v1"
    assert manifest.get("kind") == "Pod"
    meta = manifest.get("metadata", {})
    assert meta.get("name") == "order-service"
    annotations = meta.get("annotations", {})
    assert annotations.get("prometheus.io/scrape") == "true"
    assert annotations.get("prometheus.io/port") == "9090"
    assert annotations.get("telemetry.cilium.io/trace") == "b3"
    spec = manifest.get("spec", {})
    containers = spec.get("containers", [])
    assert len(containers) == 1
    assert containers[0].get("ports", [{}])[0].get("containerPort") == 9090

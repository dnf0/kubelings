"""
Validators for Chapter 17: Multi-Tenancy & Virtual Clusters
"""

from typing import Any, Dict, List

import yaml

from kubelings.validators import register_validator


def get_subnamespace_anchor_manifest() -> Dict[str, Any]:
    manifest_yaml = "\napiVersion: hnc.x-k8s.io/v1alpha2\nkind: SubnamespaceAnchor\nmetadata:\n  name: team-a-dev\n  namespace: team-a\nspec: {}\n"
    return yaml.safe_load(manifest_yaml)


@register_validator("tenant01")
def validate_tenant01(manifest: Any, raw_yaml: str = "") -> None:
    anchor = manifest
    assert anchor.get("kind") == "SubnamespaceAnchor"
    assert anchor.get("apiVersion") == "hnc.x-k8s.io/v1alpha2"
    assert anchor.get("metadata", {}).get("name") == "team-a-dev"
    assert anchor.get("metadata", {}).get("namespace") == "team-a"


def get_tenant_isolation_manifests() -> List[Dict[str, Any]]:
    manifest_yaml = '\napiVersion: v1\nkind: ResourceQuota\nmetadata:\n  name: tenant-b-quota\n  namespace: tenant-b\nspec:\n  hard:\n    requests.cpu: "4"\n    requests.memory: 8Gi\n    limits.cpu: "8"\n    limits.memory: 16Gi\n    pods: "10"\n---\napiVersion: v1\nkind: LimitRange\nmetadata:\n  name: tenant-b-limits\n  namespace: tenant-b\nspec:\n  limits:\n  - default:\n      cpu: 500m\n      memory: 512Mi\n    defaultRequest:\n      cpu: 100m\n      memory: 128Mi\n    type: Container\n'
    return list(yaml.safe_load_all(manifest_yaml))


@register_validator("tenant02")
def validate_tenant02(manifest: Any, raw_yaml: str = "") -> None:
    docs = manifest
    assert len(docs) == 2
    kinds = {d.get("kind") for d in docs}
    assert kinds == {"ResourceQuota", "LimitRange"}
    quota = next((d for d in docs if d.get("kind") == "ResourceQuota"))
    assert quota["spec"]["hard"]["pods"] == "10"


def get_vcluster_manifest() -> Dict[str, Any]:
    manifest_yaml = "\napiVersion: vcluster.loft.sh/v1alpha1\nkind: VirtualCluster\nmetadata:\n  name: dev-vcluster\n  namespace: team-c\nspec:\n  distro:\n    k3s:\n      enabled: true\n  sync:\n    toHost:\n      ingresses:\n        enabled: true\n      services:\n        enabled: true\n    fromHost:\n      nodes:\n        enabled: true\n"
    return yaml.safe_load(manifest_yaml)


@register_validator("tenant03")
def validate_tenant03(manifest: Any, raw_yaml: str = "") -> None:
    vcluster = manifest
    assert vcluster.get("kind") == "VirtualCluster"
    assert vcluster.get("apiVersion") == "vcluster.loft.sh/v1alpha1"
    sync = vcluster.get("spec", {}).get("sync", {})
    assert sync.get("toHost", {}).get("services", {}).get("enabled") is True


def get_tenant_network_isolation_policy() -> Dict[str, Any]:
    manifest_yaml = "\napiVersion: networking.k8s.io/v1\nkind: NetworkPolicy\nmetadata:\n  name: tenant-isolation\n  namespace: tenant-secure\nspec:\n  podSelector: {}\n  policyTypes:\n  - Ingress\n  - Egress\n  ingress:\n  - from:\n    - podSelector: {}\n  egress:\n  - to:\n    - podSelector: {}\n  - to:\n    - namespaceSelector:\n        matchLabels:\n          kubernetes.io/metadata.name: kube-system\n    ports:\n    - protocol: UDP\n      port: 53\n"
    return yaml.safe_load(manifest_yaml)


@register_validator("tenant04")
def validate_tenant04(manifest: Any, raw_yaml: str = "") -> None:
    policy = manifest
    assert policy.get("kind") == "NetworkPolicy"
    assert policy.get("metadata", {}).get("namespace") == "tenant-secure"
    egress = policy.get("spec", {}).get("egress", [])
    assert len(egress) == 2

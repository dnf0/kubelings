"""
Validators for Chapter 07: Scheduling, Affinity & Advanced Placement
"""

from typing import Any, Dict, List, Tuple

from kubelings.validator import validate_manifest, validate_manifests
from kubelings.validators import register_validator


def match_node_selector(
    pod_manifest: Dict[str, Any], node_name: str, node_labels: Dict[str, str]
) -> bool:
    """Evaluate whether a candidate node satisfies the pod placement constraints."""
    spec = pod_manifest.get("spec", {})
    if "nodeName" in spec:
        return spec["nodeName"] == node_name
    selector = spec.get("nodeSelector", {})
    for k, v in selector.items():
        if node_labels.get(k) != v:
            return False
    return True


@register_validator("sched01")
def validate_sched01(manifest: Any, raw_yaml: str = "") -> None:
    manifests = manifest if isinstance(manifest, list) else [manifest]
    assert len(manifests) == 2, "Must define 2 pods"
    validate_manifests(manifests, expected_kinds=["Pod", "Pod"])
    pinned, gpu = (manifests[0], manifests[1])
    assert pinned["metadata"]["name"] == "pinned-pod"
    assert pinned["spec"]["nodeName"] == "worker-node-03"
    assert gpu["metadata"]["name"] == "gpu-pod"
    assert gpu["spec"]["nodeSelector"]["accelerator"] == "nvidia-tesla-v100"
    assert gpu["spec"]["nodeSelector"]["disktype"] == "nvme"
    node_a = {"accelerator": "nvidia-tesla-v100", "disktype": "nvme", "zone": "us-east-1a"}
    node_b = {"accelerator": "tpu-v3", "disktype": "ssd", "zone": "us-east-1b"}
    assert match_node_selector(pinned, "worker-node-03", node_b) is True
    assert match_node_selector(pinned, "worker-node-01", node_a) is False
    assert match_node_selector(gpu, "worker-gpu-01", node_a) is True
    assert match_node_selector(gpu, "worker-gpu-02", node_b) is False


def evaluate_node_affinity_score(
    node_labels: Dict[str, str], node_affinity: Dict[str, Any]
) -> Tuple[bool, int]:
    """Calculate whether a node is eligible and compute its preference affinity score."""
    req = node_affinity.get("requiredDuringSchedulingIgnoredDuringExecution", {})
    terms = req.get("nodeSelectorTerms", [])
    if terms:
        term_matched = False
        for term in terms:
            expressions = term.get("matchExpressions", [])
            all_expr_matched = True
            for expr in expressions:
                key = expr.get("key")
                op = expr.get("operator")
                values = expr.get("values", [])
                val_on_node = node_labels.get(key)
                if op == "In" and val_on_node not in values:
                    all_expr_matched = False
                    break
                elif op == "NotIn" and val_on_node in values:
                    all_expr_matched = False
                    break
                elif op == "Exists" and key not in node_labels:
                    all_expr_matched = False
                    break
                elif op == "DoesNotExist" and key in node_labels:
                    all_expr_matched = False
                    break
            if all_expr_matched:
                term_matched = True
                break
        if not term_matched:
            return (False, 0)
    score = 0
    prefs = node_affinity.get("preferredDuringSchedulingIgnoredDuringExecution", [])
    for pref in prefs:
        weight = pref.get("weight", 0)
        expressions = pref.get("preference", {}).get("matchExpressions", [])
        matched = True
        for expr in expressions:
            key = expr.get("key")
            op = expr.get("operator")
            values = expr.get("values", [])
            val_on_node = node_labels.get(key)
            if op == "In" and val_on_node not in values:
                matched = False
                break
        if matched:
            score += weight
    return (True, score)


@register_validator("sched02")
def validate_sched02(manifest: Any, raw_yaml: str = "") -> None:
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(manifest, expected_kind="Pod", expected_api_version="v1")
    node_aff = manifest["spec"]["affinity"]["nodeAffinity"]
    terms = node_aff["requiredDuringSchedulingIgnoredDuringExecution"]["nodeSelectorTerms"]
    expr = terms[0]["matchExpressions"][0]
    assert expr["key"] == "topology.kubernetes.io/zone"
    assert expr["operator"] == "In"
    assert "us-east-1a" in expr["values"]
    assert "us-east-1b" in expr["values"]
    pref = node_aff["preferredDuringSchedulingIgnoredDuringExecution"][0]
    assert pref["weight"] == 80
    node_optimal = {"topology.kubernetes.io/zone": "us-east-1a", "instance-type": "c5.2xlarge"}
    node_valid_unpreferred = {
        "topology.kubernetes.io/zone": "us-east-1b",
        "instance-type": "t3.medium",
    }
    node_ineligible = {
        "topology.kubernetes.io/zone": "eu-central-1a",
        "instance-type": "c5.2xlarge",
    }
    assert evaluate_node_affinity_score(node_optimal, node_aff) == (True, 80)
    assert evaluate_node_affinity_score(node_valid_unpreferred, node_aff) == (True, 0)
    assert evaluate_node_affinity_score(node_ineligible, node_aff) == (False, 0)


def can_coexist_on_host(
    running_pod_labels_on_node: List[Dict[str, str]], pod_manifest: Dict[str, Any]
) -> bool:
    """Check if placing the candidate pod violates host-level podAntiAffinity."""
    aff = pod_manifest.get("spec", {}).get("affinity", {})
    anti_terms = aff.get("podAntiAffinity", {}).get(
        "requiredDuringSchedulingIgnoredDuringExecution", []
    )
    for term in anti_terms:
        if term.get("topologyKey") == "kubernetes.io/hostname":
            match_labels = term.get("labelSelector", {}).get("matchLabels", {})
            for pod_labels in running_pod_labels_on_node:
                if all((pod_labels.get(k) == v for k, v in match_labels.items())):
                    return False
    return True


@register_validator("sched03")
def validate_sched03(manifest: Any, raw_yaml: str = "") -> None:
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(manifest, expected_kind="Pod", expected_api_version="v1")
    aff = manifest["spec"]["affinity"]
    anti_terms = aff["podAntiAffinity"]["requiredDuringSchedulingIgnoredDuringExecution"]
    assert anti_terms[0]["labelSelector"]["matchLabels"]["app"] == "web-frontend"
    assert anti_terms[0]["topologyKey"] == "kubernetes.io/hostname"
    pref_terms = aff["podAffinity"]["preferredDuringSchedulingIgnoredDuringExecution"]
    assert pref_terms[0]["weight"] == 100
    assert pref_terms[0]["podAffinityTerm"]["labelSelector"]["matchLabels"]["app"] == "redis-cache"
    assert pref_terms[0]["podAffinityTerm"]["topologyKey"] == "topology.kubernetes.io/zone"
    node_with_web = [{"app": "web-frontend", "version": "1.0"}, {"tier": "backend"}]
    node_with_cache = [{"app": "redis-cache"}, {"tier": "backend"}]
    assert can_coexist_on_host(node_with_web, manifest) is False, (
        "Cannot co-locate on same host as another web-frontend"
    )
    assert can_coexist_on_host(node_with_cache, manifest) is True


def can_schedule_on_tainted_node(
    pod_tolerations: List[Dict[str, Any]], node_taints: List[Dict[str, Any]]
) -> bool:
    """Check whether a pod tolerates all blocking taints (NoSchedule/NoExecute) on a node."""
    for taint in node_taints:
        effect = taint.get("effect")
        if effect not in ("NoSchedule", "NoExecute"):
            continue
        taint_key = taint.get("key")
        taint_value = taint.get("value")
        tolerated = False
        for tol in pod_tolerations:
            tol_effect = tol.get("effect")
            if tol_effect and tol_effect != effect:
                continue
            tol_key = tol.get("key")
            tol_op = tol.get("operator", "Equal")
            tol_val = tol.get("value")
            if tol_op == "Exists":
                if not tol_key or tol_key == taint_key:
                    tolerated = True
                    break
            elif tol_op == "Equal":
                if tol_key == taint_key and tol_val == taint_value:
                    tolerated = True
                    break
        if not tolerated:
            return False
    return True


@register_validator("sched04")
def validate_sched04(manifest: Any, raw_yaml: str = "") -> None:
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(manifest, expected_kind="Pod", expected_api_version="v1")
    tolerations = manifest["spec"]["tolerations"]
    assert len(tolerations) == 2
    t1 = tolerations[0]
    assert t1["key"] == "gpu-type"
    assert t1["operator"] == "Equal"
    assert t1["value"] == "h100"
    assert t1["effect"] == "NoSchedule"
    t2 = tolerations[1]
    assert t2["key"] == "node.kubernetes.io/unreachable"
    assert t2["operator"] == "Exists"
    assert t2["effect"] == "NoExecute"
    assert t2["tolerationSeconds"] == 120
    h100_taints = [{"key": "gpu-type", "value": "h100", "effect": "NoSchedule"}]
    a100_taints = [{"key": "gpu-type", "value": "a100", "effect": "NoSchedule"}]
    unreachable_taints = [
        {"key": "node.kubernetes.io/unreachable", "value": "true", "effect": "NoExecute"}
    ]
    no_taints = []
    assert can_schedule_on_tainted_node(tolerations, h100_taints) is True
    assert can_schedule_on_tainted_node(tolerations, no_taints) is True
    assert can_schedule_on_tainted_node(tolerations, unreachable_taints) is True
    assert can_schedule_on_tainted_node(tolerations, a100_taints) is False, (
        "A100 taint not tolerated"
    )


def is_placement_skew_acceptable(
    current_zone_counts: Dict[str, int], candidate_zone: str, max_skew: int = 1
) -> bool:
    """Calculate if placing a new pod in candidate_zone satisfies the maxSkew constraint."""
    updated_counts = dict(current_zone_counts)
    updated_counts[candidate_zone] = updated_counts.get(candidate_zone, 0) + 1
    values = list(updated_counts.values())
    if not values:
        return True
    skew = max(values) - min(values)
    return skew <= max_skew


@register_validator("sched05")
def validate_sched05(manifest: Any, raw_yaml: str = "") -> None:
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(manifest, expected_kind="Pod", expected_api_version="v1")
    tsc = manifest["spec"]["topologySpreadConstraints"][0]
    assert tsc["maxSkew"] == 1
    assert tsc["topologyKey"] == "topology.kubernetes.io/zone"
    assert tsc["whenUnsatisfiable"] == "DoNotSchedule"
    assert tsc["labelSelector"]["matchLabels"]["app"] == "payment-processor"
    zones = {"zoneA": 2, "zoneB": 2, "zoneC": 1}
    assert is_placement_skew_acceptable(zones, "zoneC", max_skew=1) is True
    assert is_placement_skew_acceptable(zones, "zoneA", max_skew=1) is False
    balanced = {"zoneA": 1, "zoneB": 1}
    assert is_placement_skew_acceptable(balanced, "zoneA", max_skew=1) is True

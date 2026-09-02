"""
Validators for Chapter 27: AWS EKS & Cloud Architecture
"""

from typing import Any

from kubelings.validator import validate_manifest_text
from kubelings.validators import register_validator


@register_validator("eks01")
def validate_eks01(manifest: Any, raw_yaml: str = "") -> None:
    passed, errors = validate_manifest_text(raw_yaml, "eks01")
    assert passed, f"EKS IRSA manifest validation failed: {errors}"
    docs = manifest if isinstance(manifest, list) else [manifest]
    assert len(docs) == 2, "Manifest must define exactly 2 documents (ServiceAccount and Pod)"

    sa_doc = next((d for d in docs if d.get("kind") == "ServiceAccount"), None)
    assert sa_doc is not None, "Missing ServiceAccount document"
    assert sa_doc["metadata"]["name"] == "s3-reader-sa", (
        "ServiceAccount name must be 's3-reader-sa'"
    )
    annotations = sa_doc["metadata"].get("annotations", {})
    assert (
        annotations.get("eks.amazonaws.com/role-arn")
        == "arn:aws:iam::123456789012:role/s3-reader-role"
    ), (
        "ServiceAccount must have annotation 'eks.amazonaws.com/role-arn: arn:aws:iam::123456789012:role/s3-reader-role'"
    )

    pod_doc = next((d for d in docs if d.get("kind") == "Pod"), None)
    assert pod_doc is not None, "Missing Pod document"
    assert pod_doc["metadata"]["name"] == "s3-worker-pod", "Pod name must be 's3-worker-pod'"
    assert pod_doc["spec"].get("serviceAccountName") == "s3-reader-sa", (
        "Pod spec.serviceAccountName must be 's3-reader-sa'"
    )
    container = pod_doc["spec"]["containers"][0]
    assert container["name"] == "worker", "Container name must be 'worker'"
    assert container["image"] == "amazon/aws-cli:latest", (
        "Container image must be 'amazon/aws-cli:latest'"
    )


@register_validator("eks02")
def validate_eks02(manifest: Any, raw_yaml: str = "") -> None:
    passed, errors = validate_manifest_text(raw_yaml, "eks02")
    assert passed, f"ALB Ingress manifest validation failed: {errors}"
    assert manifest["kind"] == "Ingress", "Kind must be 'Ingress'"
    assert manifest["metadata"]["name"] == "alb-ingress", "Ingress name must be 'alb-ingress'"
    annotations = manifest["metadata"].get("annotations", {})
    assert annotations.get("alb.ingress.kubernetes.io/scheme") == "internet-facing", (
        "Annotation 'alb.ingress.kubernetes.io/scheme' must be 'internet-facing'"
    )
    assert annotations.get("alb.ingress.kubernetes.io/target-type") == "ip", (
        "Annotation 'alb.ingress.kubernetes.io/target-type' must be 'ip'"
    )
    assert manifest["spec"].get("ingressClassName") == "alb", "spec.ingressClassName must be 'alb'"
    rules = manifest["spec"].get("rules", [])
    assert len(rules) > 0, "Ingress must have at least one rule"
    assert rules[0]["host"] == "api.example.com", "Rule host must be 'api.example.com'"


@register_validator("eks03")
def validate_eks03(manifest: Any, raw_yaml: str = "") -> None:
    passed, errors = validate_manifest_text(raw_yaml, "eks03")
    assert passed, f"SecurityGroupPolicy manifest validation failed: {errors}"
    assert manifest["kind"] == "SecurityGroupPolicy", "Kind must be 'SecurityGroupPolicy'"
    assert manifest["metadata"]["name"] == "payment-sg-policy", (
        "Name must be 'payment-sg-policy'"
    )
    pod_sel = manifest["spec"]["podSelector"]["matchLabels"]
    assert pod_sel.get("app") == "payment-gateway", (
        "podSelector.matchLabels must specify 'app: payment-gateway'"
    )
    group_ids = manifest["spec"]["securityGroups"]["groupIds"]
    assert "sg-0123456789abcdef0" in group_ids, "groupIds must contain 'sg-0123456789abcdef0'"
    assert "sg-0987654321fedcba0" in group_ids, "groupIds must contain 'sg-0987654321fedcba0'"


@register_validator("eks04")
def validate_eks04(manifest: Any, raw_yaml: str = "") -> None:
    passed, errors = validate_manifest_text(raw_yaml, "eks04")
    assert passed, f"Karpenter NodePool manifest validation failed: {errors}"
    docs = manifest if isinstance(manifest, list) else [manifest]
    assert len(docs) == 2, "Manifest must define exactly 2 documents (NodePool and EC2NodeClass)"

    pool_doc = next((d for d in docs if d.get("kind") == "NodePool"), None)
    assert pool_doc is not None, "Missing NodePool document"
    assert pool_doc["metadata"]["name"] == "default-pool", "NodePool name must be 'default-pool'"
    node_ref = pool_doc["spec"]["template"]["spec"]["nodeClassRef"]
    assert node_ref["name"] == "default-nodeclass", "nodeClassRef name must be 'default-nodeclass'"

    class_doc = next((d for d in docs if d.get("kind") == "EC2NodeClass"), None)
    assert class_doc is not None, "Missing EC2NodeClass document"
    assert class_doc["metadata"]["name"] == "default-nodeclass", (
        "EC2NodeClass name must be 'default-nodeclass'"
    )
    assert class_doc["spec"]["amiFamily"] == "AL2023", "amiFamily must be 'AL2023'"

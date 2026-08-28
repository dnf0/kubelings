"""
Validators for Chapter 11: Autoscaling (HPA, VPA, KEDA)
"""

from typing import Any

from kubelings.validator import validate_manifest
from kubelings.validators import register_validator


@register_validator("autoscale01")
def validate_autoscale01(manifest: Any, raw_yaml: str = "") -> None:
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(
        manifest, expected_kind="HorizontalPodAutoscaler", expected_api_version="autoscaling/v2"
    )
    metadata = manifest.get("metadata", {})
    assert metadata.get("name") == "api-scaler", "HPA name must be 'api-scaler'"
    assert metadata.get("namespace") == "production", "HPA namespace must be 'production'"
    spec = manifest.get("spec", {})
    scale_target = spec.get("scaleTargetRef", {})
    assert scale_target.get("apiVersion") == "apps/v1", (
        "scaleTargetRef apiVersion must be 'apps/v1'"
    )
    assert scale_target.get("kind") == "Deployment", "scaleTargetRef kind must be 'Deployment'"
    assert scale_target.get("name") == "api-service", "scaleTargetRef name must be 'api-service'"
    assert spec.get("minReplicas") == 2, "minReplicas must be 2"
    assert spec.get("maxReplicas") == 10, "maxReplicas must be 10"
    metrics = spec.get("metrics", [])
    assert isinstance(metrics, list) and len(metrics) == 2, (
        "Must specify exactly 2 resource metrics"
    )
    cpu_metric = next((m for m in metrics if m.get("resource", {}).get("name") == "cpu"), None)
    assert cpu_metric is not None, "Must define CPU resource metric"
    assert cpu_metric.get("type") == "Resource"
    assert cpu_metric["resource"]["target"]["type"] == "Utilization"
    assert cpu_metric["resource"]["target"]["averageUtilization"] == 75
    mem_metric = next((m for m in metrics if m.get("resource", {}).get("name") == "memory"), None)
    assert mem_metric is not None, "Must define memory resource metric"
    assert mem_metric.get("type") == "Resource"
    assert mem_metric["resource"]["target"]["type"] == "Utilization"
    assert mem_metric["resource"]["target"]["averageUtilization"] == 80


@register_validator("autoscale02")
def validate_autoscale02(manifest: Any, raw_yaml: str = "") -> None:
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(
        manifest, expected_kind="HorizontalPodAutoscaler", expected_api_version="autoscaling/v2"
    )
    metadata = manifest.get("metadata", {})
    assert metadata.get("name") == "checkout-hpa", "HPA name must be 'checkout-hpa'"
    assert metadata.get("namespace") == "ecommerce", "HPA namespace must be 'ecommerce'"
    spec = manifest.get("spec", {})
    assert spec.get("minReplicas") == 3
    assert spec.get("maxReplicas") == 25
    metrics = spec.get("metrics", [])
    assert len(metrics) == 1
    assert metrics[0]["resource"]["target"]["averageUtilization"] == 70
    behavior = spec.get("behavior", {})
    assert isinstance(behavior, dict), "spec.behavior must be defined"
    scale_down = behavior.get("scaleDown", {})
    assert scale_down.get("stabilizationWindowSeconds") == 300
    assert scale_down.get("selectPolicy") == "Min"
    down_policies = scale_down.get("policies", [])
    assert len(down_policies) == 2
    down_types = {p.get("type"): p for p in down_policies}
    assert "Percent" in down_types and down_types["Percent"].get("value") == 10
    assert "Pods" in down_types and down_types["Pods"].get("value") == 2
    scale_up = behavior.get("scaleUp", {})
    assert scale_up.get("stabilizationWindowSeconds") == 0
    assert scale_up.get("selectPolicy") == "Max"
    up_policies = scale_up.get("policies", [])
    assert len(up_policies) == 2
    up_types = {p.get("type"): p for p in up_policies}
    assert "Percent" in up_types and up_types["Percent"].get("value") == 100
    assert "Pods" in up_types and up_types["Pods"].get("value") == 4


@register_validator("autoscale03")
def validate_autoscale03(manifest: Any, raw_yaml: str = "") -> None:
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(
        manifest,
        expected_kind="VerticalPodAutoscaler",
        expected_api_version="autoscaling.k8s.io/v1",
    )
    metadata = manifest.get("metadata", {})
    assert metadata.get("name") == "analytics-vpa", "VPA name must be 'analytics-vpa'"
    assert metadata.get("namespace") == "data-platform", "VPA namespace must be 'data-platform'"
    spec = manifest.get("spec", {})
    target_ref = spec.get("targetRef", {})
    assert target_ref.get("apiVersion") == "apps/v1"
    assert target_ref.get("kind") == "Deployment"
    assert target_ref.get("name") == "analytics-worker"
    update_policy = spec.get("updatePolicy", {})
    assert update_policy.get("updateMode") == "Auto", "updatePolicy.updateMode must be 'Auto'"
    resource_policy = spec.get("resourcePolicy", {})
    container_policies = resource_policy.get("containerPolicies", [])
    assert len(container_policies) == 1, "Must define exactly one containerPolicy"
    cp = container_policies[0]
    assert cp.get("containerName") == "worker", "containerName must be 'worker'"
    assert cp.get("minAllowed") == {"cpu": "100m", "memory": "128Mi"}
    assert cp.get("maxAllowed") == {"cpu": "2", "memory": "4Gi"}
    assert set(cp.get("controlledResources", [])) == {"cpu", "memory"}


@register_validator("autoscale04")
def validate_autoscale04(manifest: Any, raw_yaml: str = "") -> None:
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(
        manifest, expected_kind="ScaledObject", expected_api_version="keda.sh/v1alpha1"
    )
    metadata = manifest.get("metadata", {})
    assert metadata.get("name") == "orders-queue-scaler"
    assert metadata.get("namespace") == "messaging"
    spec = manifest.get("spec", {})
    scale_target = spec.get("scaleTargetRef", {})
    assert scale_target.get("apiVersion") == "apps/v1"
    assert scale_target.get("kind") == "Deployment"
    assert scale_target.get("name") == "order-consumer"
    assert spec.get("minReplicaCount") == 0, (
        "minReplicaCount must be 0 for scale-to-zero capability"
    )
    assert spec.get("maxReplicaCount") == 30, "maxReplicaCount must be 30"
    assert spec.get("pollingInterval") == 15, "pollingInterval must be 15 seconds"
    assert spec.get("cooldownPeriod") == 300, "cooldownPeriod must be 300 seconds"
    triggers = spec.get("triggers", [])
    assert len(triggers) == 1, "Must define exactly 1 trigger"
    trigger = triggers[0]
    assert trigger.get("type") == "rabbitmq"
    trig_meta = trigger.get("metadata", {})
    assert trig_meta.get("queueName") == "orders-queue"
    assert trig_meta.get("queueLength") == "20"
    assert trig_meta.get("mode") == "QueueLength"
    assert "amqp://" in trig_meta.get("host", "")

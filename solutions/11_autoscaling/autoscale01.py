"""
Exercise: solutions/11_autoscaling/autoscale01.py
Topic: Horizontal Pod Autoscaler (HPA v2)

Reference Solution
"""

import yaml

from kubelings.validator import validate_manifest

HPA_MANIFEST = """
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-scaler
  namespace: production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api-service
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 75
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
"""


def verify():
    manifest = yaml.safe_load(HPA_MANIFEST)
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(
        manifest,
        expected_kind="HorizontalPodAutoscaler",
        expected_api_version="autoscaling/v2",
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

    print("✓ autoscale01 passed!")


if __name__ == "__main__":
    verify()

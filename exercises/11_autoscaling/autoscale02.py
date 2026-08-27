"""
Exercise: exercises/11_autoscaling/autoscale02.py
Topic: HPA Custom Scaling Behavior

Instructions:
Kubernetes autoscaling/v2 allows fine-grained control over scaling velocity
using `spec.behavior`. This prevents flapping (thrashing) by introducing
stabilization windows and capping the rate of replica changes for scale-up
and scale-down independently.

1. Define a HorizontalPodAutoscaler 'checkout-hpa' in namespace 'ecommerce':
   - apiVersion: autoscaling/v2
   - scaleTargetRef: Deployment 'checkout-service' (apiVersion: apps/v1)
   - minReplicas: 3, maxReplicas: 25
   - metrics:
     - Resource CPU target averageUtilization: 70%
   - behavior:
     - scaleDown:
       - stabilizationWindowSeconds: 300
       - selectPolicy: Min
       - policies:
         - type: Percent, value: 10, periodSeconds: 60
         - type: Pods, value: 2, periodSeconds: 60
     - scaleUp:
       - stabilizationWindowSeconds: 0
       - selectPolicy: Max
       - policies:
         - type: Percent, value: 100, periodSeconds: 15
         - type: Pods, value: 4, periodSeconds: 15
"""

import yaml

from kubelings.validator import validate_manifest

HPA_MANIFEST = """
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: checkout-hpa
  namespace: ecommerce
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: checkout-service
  minReplicas: 3
  maxReplicas: 25
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: ???
  behavior:
    scaleDown:
      stabilizationWindowSeconds: ???
      selectPolicy: Min
      policies:
      - type: ???
        value: 10
        periodSeconds: 60
      - type: Pods
        value: 2
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0
      selectPolicy: ???
      policies:
      - type: Percent
        value: ???
        periodSeconds: 15
      - type: Pods
        value: 4
        periodSeconds: 15
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

    # Check scaleDown
    scale_down = behavior.get("scaleDown", {})
    assert scale_down.get("stabilizationWindowSeconds") == 300
    assert scale_down.get("selectPolicy") == "Min"
    down_policies = scale_down.get("policies", [])
    assert len(down_policies) == 2
    down_types = {p.get("type"): p for p in down_policies}
    assert "Percent" in down_types and down_types["Percent"].get("value") == 10
    assert "Pods" in down_types and down_types["Pods"].get("value") == 2

    # Check scaleUp
    scale_up = behavior.get("scaleUp", {})
    assert scale_up.get("stabilizationWindowSeconds") == 0
    assert scale_up.get("selectPolicy") == "Max"
    up_policies = scale_up.get("policies", [])
    assert len(up_policies) == 2
    up_types = {p.get("type"): p for p in up_policies}
    assert "Percent" in up_types and up_types["Percent"].get("value") == 100
    assert "Pods" in up_types and up_types["Pods"].get("value") == 4

    print("✓ autoscale02 passed!")


if __name__ == "__main__":
    verify()

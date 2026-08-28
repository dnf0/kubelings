"""
Exercise: exercises/11_autoscaling/autoscale02.py
Topic: HPA Custom Scaling Behavior

Context & Why:
Under bursty or oscillating workloads (such as flash sales or cron-driven webhook processing),
standard autoscaling can suffer from "thrashing" or "flapping"—scaling pods up and down repeatedly,
wasting container spin-up overhead and thrashing cluster nodes. `spec.behavior` provides asymmetric
velocity controls: by adding a 300-second stabilization window on scale-down with restrictive step
policies (`selectPolicy: Min`), the autoscaler waits out brief traffic dips before terminating pods.
Conversely, setting `stabilizationWindowSeconds: 0` and `selectPolicy: Max` on scale-up ensures immediate,
aggressive capacity expansion when traffic surges.

Instructions:
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
        # TODO: Set target CPU averageUtilization to 70.
        # WHY: Establishes the steady-state target CPU threshold across all checkout service pods.
        averageUtilization: ???
  behavior:
    scaleDown:
      # TODO: Set scaleDown stabilization window to 300 seconds.
      # WHY: Holds scale-down actions for 5 minutes to prevent premature pod termination during temporary traffic lulls.
      stabilizationWindowSeconds: ???
      selectPolicy: Min
      policies:
      # TODO: Set scaleDown policy type to 'Percent' (value: 10, periodSeconds: 60).
      # WHY: Restricts scale-down to at most 10% of existing replicas per 60-second window.
      - type: ???
        value: 10
        periodSeconds: 60
      - type: Pods
        value: 2
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0
      # TODO: Set scaleUp selectPolicy to 'Max'.
      # WHY: Chooses whichever scaling policy yields the largest replica addition for rapid scale-out.
      selectPolicy: ???
      policies:
      - type: Percent
        # TODO: Set scaleUp percentage value to 100.
        # WHY: Allows doubling the pod count (100% increase) every 15 seconds during severe spikes.
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

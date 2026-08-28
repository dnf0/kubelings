"""
Exercise: exercises/11_autoscaling/autoscale01.py
Topic: Horizontal Pod Autoscaler (HPA v2)

Context & Why:
In production Kubernetes environments, traffic volume varies significantly throughout the day.
Over-provisioning static pod counts wastes cloud infrastructure spend, while under-provisioning
causes latency degradation and cascading service outages during traffic spikes. The Horizontal
Pod Autoscaler (HPA) using `autoscaling/v2` dynamically computes desired replica count based on
metrics server telemetry against container resource requests (e.g., target CPU utilization at 75%).
When actual utilization deviates from the target, the HPA controller scales the underlying Deployment
replicas to stabilize workload performance.

Instructions:
1. Define a HorizontalPodAutoscaler 'api-scaler' in namespace 'production':
   - apiVersion: autoscaling/v2
   - scaleTargetRef:
     - apiVersion: apps/v1
     - kind: Deployment
     - name: api-service
   - minReplicas: 2
   - maxReplicas: 10
   - metrics:
     - Resource metric for CPU target averageUtilization: 75%
     - Resource metric for Memory target averageUtilization: 80%
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
    # TODO: Specify target workload kind 'Deployment' and name 'api-service'.
    # WHY: Binds the autoscaling control loop to the specific Deployment controller managing the pods.
    kind: ???
    name: ???
  # TODO: Set minimum replicas to 2.
  # WHY: Maintains high availability and fault tolerance across nodes even under low load.
  minReplicas: ???
  # TODO: Set maximum replicas to 10.
  # WHY: Bounds cluster compute resource consumption to prevent runaway billing or node exhaustion.
  maxReplicas: ???
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        # TODO: Set target CPU averageUtilization to 75.
        # WHY: Triggers scale-out when average pod CPU consumption across replicas exceeds 75% of requested CPU.
        averageUtilization: ???
  - type: Resource
    resource:
      # TODO: Set resource name to 'memory'.
      # WHY: Adds memory pressure as a second metric dimension for autoscaling decisions.
      name: ???
      target:
        type: Utilization
        # TODO: Set target Memory averageUtilization to 80.
        # WHY: Triggers scale-out when memory consumption reaches 80% of requested memory.
        averageUtilization: ???
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

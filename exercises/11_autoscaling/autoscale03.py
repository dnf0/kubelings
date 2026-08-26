"""
Exercise: exercises/11_autoscaling/autoscale03.py
Topic: Vertical Pod Autoscaler (VPA)

Instructions:
The Vertical Pod Autoscaler (VPA) automatically adjusts the CPU and memory
resource requests and limits for pods based on real-time historical usage.
This frees developers from guessing resource requirements and improves cluster
efficiency.

1. Define a VerticalPodAutoscaler 'analytics-vpa' in namespace 'data-platform':
   - apiVersion: autoscaling.k8s.io/v1
   - targetRef:
     - apiVersion: apps/v1
     - kind: Deployment
     - name: analytics-worker
   - updatePolicy:
     - updateMode: "Auto"
   - resourcePolicy:
     - containerPolicies:
       - containerName: "worker"
         minAllowed:
           cpu: "100m"
           memory: "128Mi"
         maxAllowed:
           cpu: "2"
           memory: "4Gi"
         controlledResources: ["cpu", "memory"]
"""

# I AM NOT DONE

import yaml

from kubelings.validator import validate_manifest

VPA_MANIFEST = """
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: analytics-vpa
  namespace: data-platform
spec:
  targetRef:
    apiVersion: apps/v1
    kind: ???
    name: ???
  updatePolicy:
    updateMode: ???
  resourcePolicy:
    containerPolicies:
    - containerName: "worker"
      minAllowed:
        cpu: ???
        memory: "128Mi"
      maxAllowed:
        cpu: "2"
        memory: ???
      controlledResources:
      - "cpu"
      - "memory"
"""


def verify():
    manifest = yaml.safe_load(VPA_MANIFEST)
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

    print("✓ autoscale03 passed!")


if __name__ == "__main__":
    verify()

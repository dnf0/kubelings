"""
Exercise: exercises/11_autoscaling/autoscale03.py
Topic: Vertical Pod Autoscaler (VPA)

Context & Why:
Setting container CPU and memory requests and limits is notoriously error-prone: over-provisioning
leads to low cluster utilization and astronomical cloud bills, while under-provisioning leads to
CPU throttling and container OOMKills. The Vertical Pod Autoscaler (VPA) analyzes historical resource
utilization and automatically right-sizes container requests and limits. In `Auto` update mode, the VPA
admission controller mutates pod specifications at creation and evicts running pods if their resource
allocations diverge significantly from recommended profiles, keeping allocations within bounded `minAllowed`
and `maxAllowed` safeguards.

Instructions:
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
    # TODO: Specify target workload kind 'Deployment' and name 'analytics-worker'.
    # WHY: Targets the analytics Deployment for vertical resource recommendation and mutation.
    kind: ???
    name: ???
  updatePolicy:
    # TODO: Set updateMode to "Auto".
    # WHY: Allows VPA to automatically assign resource requests on pod creation and evict running pods to apply new recommendations.
    updateMode: ???
  resourcePolicy:
    containerPolicies:
    - containerName: "worker"
      minAllowed:
        # TODO: Set minimum allowed CPU to '100m'.
        # WHY: Guarantees the container receives at least 0.1 CPU core even under low utilization.
        cpu: ???
        memory: "128Mi"
      maxAllowed:
        cpu: "2"
        # TODO: Set maximum allowed Memory to '4Gi'.
        # WHY: Caps memory allocation to prevent a single worker from consuming entire node capacity.
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

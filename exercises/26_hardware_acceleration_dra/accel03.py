"""
Exercise: exercises/26_hardware_acceleration_dra/accel03.py
Topic: Kubernetes Dynamic Resource Allocation (DRA) Standard

Context & Why:
Traditional Kubernetes device allocation models rely on static integer counters (such as `nvidia.com/gpu: 1`),
which fail to represent complex modern accelerator topologies (such as NVLink interconnect meshes,
PCIe switches, FPGA bitstreams, or multi-device shared memory pools).

Kubernetes Dynamic Resource Allocation (DRA, `resource.k8s.io`) replaces static device counting with
a flexible, claim-based architecture:
- `ResourceClaimTemplate`: A declarative template defining device requirements (e.g. `deviceClassName: gpu.example.com`
  and device count).
- `ResourceClaim`: Generated per-pod to represent an allocated slice of hardware that matches the requested topology.
- Pod Integration: Pods reference the claim in `spec.resourceClaims`, and containers consume the claim in
  `spec.containers[*].resources.claims`.
- The scheduler and device driver collaborate to co-allocate interconnected accelerators on the same node with
  optimal interconnect topologies.

Task:
Fix the multi-document manifest below to provision dynamic device resources using Kubernetes DRA:
1. Document 1: Define a 'ResourceClaimTemplate' named 'gpu-dra-claim-template' with 'apiVersion: resource.k8s.io/v1alpha3'.
   - In 'spec.spec.devices.requests', add a request named 'dedicated-gpu' targeting 'deviceClassName: gpu.example.com' with 'count: 1'.
2. Document 2: Define a 'Pod' named 'dra-workload-pod' with 'apiVersion: v1'.
   - In 'spec.resourceClaims', bind a claim named 'gpu-claim' using 'resourceClaimTemplateName: gpu-dra-claim-template'.
   - In container 'workload' (image 'ubuntu:22.04'), bind the allocated device under 'resources.claims' referencing 'name: gpu-claim'.
"""

import yaml

from kubelings.validator import validate_manifest_text

# TODO: Configure the multi-document DRA manifest with a ResourceClaimTemplate requesting dedicated GPU devices and a Pod binding the resource claim.
# WHY: Dynamic Resource Allocation (DRA) provides an expressive, parameter-driven device scheduling framework that moves beyond simple integer counting to support topology-aware, dynamically configured hardware accelerators.
DRA_MANIFEST = """
apiVersion: resource.k8s.io/v1alpha3
kind: ???
metadata:
  name: ???
spec:
  spec:
    devices:
      requests:
        - name: ???
          deviceClassName: ???
          count: 0
---
apiVersion: v1
kind: ???
metadata:
  name: ???
spec:
  resourceClaims:
    - name: ???
      resourceClaimTemplateName: ???
  containers:
    - name: ???
      image: ???
      resources:
        claims:
          - name: ???
"""


def verify():
    passed, errors = validate_manifest_text(DRA_MANIFEST, "accel03")
    assert passed, f"DRA manifest validation failed: {errors}"

    docs = list(yaml.safe_load_all(DRA_MANIFEST))
    assert len(docs) == 2, (
        "Manifest must define exactly 2 documents (ResourceClaimTemplate and Pod)"
    )

    template_doc = next((d for d in docs if d.get("kind") == "ResourceClaimTemplate"), None)
    assert template_doc is not None, "Missing ResourceClaimTemplate document"
    assert template_doc["metadata"]["name"] == "gpu-dra-claim-template", (
        "ResourceClaimTemplate name must be 'gpu-dra-claim-template'"
    )

    req = template_doc["spec"]["spec"]["devices"]["requests"][0]
    assert req["name"] == "dedicated-gpu", "Device request name must be 'dedicated-gpu'"
    assert req["deviceClassName"] == "gpu.example.com", "deviceClassName must be 'gpu.example.com'"
    assert req["count"] == 1, "Device count must be 1"

    pod_doc = next((d for d in docs if d.get("kind") == "Pod"), None)
    assert pod_doc is not None, "Missing Pod document"
    assert pod_doc["metadata"]["name"] == "dra-workload-pod", "Pod name must be 'dra-workload-pod'"

    pod_claims = pod_doc["spec"]["resourceClaims"]
    assert pod_claims[0]["name"] == "gpu-claim", "resourceClaim name must be 'gpu-claim'"
    assert pod_claims[0]["resourceClaimTemplateName"] == "gpu-dra-claim-template", (
        "resourceClaimTemplateName must be 'gpu-dra-claim-template'"
    )

    container = pod_doc["spec"]["containers"][0]
    assert container["name"] == "workload", "Container name must be 'workload'"
    assert container["image"] == "ubuntu:22.04", "Container image must be 'ubuntu:22.04'"

    c_claims = container["resources"]["claims"]
    assert c_claims[0]["name"] == "gpu-claim", "Container resource claim name must be 'gpu-claim'"

    print("✓ accel03 passed!")


if __name__ == "__main__":
    verify()

"""
Solution: solutions/26_hardware_acceleration_dra/accel03.py
Topic: Kubernetes Dynamic Resource Allocation (DRA) Standard
"""

import yaml

from kubelings.validator import validate_manifest_text

DRA_MANIFEST = """
apiVersion: resource.k8s.io/v1alpha3
kind: ResourceClaimTemplate
metadata:
  name: gpu-dra-claim-template
spec:
  spec:
    devices:
      requests:
        - name: dedicated-gpu
          deviceClassName: gpu.example.com
          count: 1
---
apiVersion: v1
kind: Pod
metadata:
  name: dra-workload-pod
spec:
  resourceClaims:
    - name: gpu-claim
      resourceClaimTemplateName: gpu-dra-claim-template
  containers:
    - name: workload
      image: ubuntu:22.04
      resources:
        claims:
          - name: gpu-claim
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

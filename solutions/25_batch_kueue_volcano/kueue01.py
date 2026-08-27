"""
Solution: solutions/25_batch_kueue_volcano/kueue01.py
Topic: Kueue ResourceFlavor & ClusterQueue Cohort Borrowing
"""

import yaml

from kubelings.validator import validate_manifest_text

KUEUE_MANIFEST = """
apiVersion: kueue.x-k8s.io/v1beta1
kind: ResourceFlavor
metadata:
  name: default-flavor
---
apiVersion: kueue.x-k8s.io/v1beta1
kind: ClusterQueue
metadata:
  name: cluster-queue-ai
spec:
  cohort: ai-research-cohort
  resourceGroups:
    - coveredResources:
        - cpu
        - memory
        - nvidia.com/gpu
      flavors:
        - name: default-flavor
          resources:
            - name: cpu
              nominalQuota: "64"
              borrowingLimit: "32"
            - name: memory
              nominalQuota: 256Gi
            - name: nvidia.com/gpu
              nominalQuota: "8"
              borrowingLimit: "4"
"""


def verify():
    passed, errors = validate_manifest_text(KUEUE_MANIFEST, "kueue01")
    assert passed, f"Kueue manifest validation failed: {errors}"

    docs = list(yaml.safe_load_all(KUEUE_MANIFEST))
    assert len(docs) == 2, (
        "Manifest must define exactly 2 documents (ResourceFlavor and ClusterQueue)"
    )

    flavor_doc = next((d for d in docs if d.get("kind") == "ResourceFlavor"), None)
    assert flavor_doc is not None, "Missing ResourceFlavor document"
    assert flavor_doc["metadata"]["name"] == "default-flavor", (
        "ResourceFlavor name must be 'default-flavor'"
    )

    queue_doc = next((d for d in docs if d.get("kind") == "ClusterQueue"), None)
    assert queue_doc is not None, "Missing ClusterQueue document"
    assert queue_doc["metadata"]["name"] == "cluster-queue-ai", (
        "ClusterQueue name must be 'cluster-queue-ai'"
    )
    assert queue_doc["spec"]["cohort"] == "ai-research-cohort", (
        "Cohort must be 'ai-research-cohort'"
    )

    rg = queue_doc["spec"]["resourceGroups"][0]
    covered = set(rg["coveredResources"])
    assert "cpu" in covered, "coveredResources must include 'cpu'"
    assert "memory" in covered, "coveredResources must include 'memory'"
    assert "nvidia.com/gpu" in covered, "coveredResources must include 'nvidia.com/gpu'"

    flavor = rg["flavors"][0]
    assert flavor["name"] == "default-flavor", "Flavor name must be 'default-flavor'"

    res_map = {r["name"]: r for r in flavor["resources"]}
    assert str(res_map["cpu"]["nominalQuota"]) == "64", "cpu nominalQuota must be 64"
    assert str(res_map["cpu"].get("borrowingLimit")) == "32", "cpu borrowingLimit must be 32"
    assert str(res_map["memory"]["nominalQuota"]) == "256Gi", "memory nominalQuota must be 256Gi"
    assert str(res_map["nvidia.com/gpu"]["nominalQuota"]) == "8", (
        "nvidia.com/gpu nominalQuota must be 8"
    )
    assert str(res_map["nvidia.com/gpu"].get("borrowingLimit")) == "4", (
        "nvidia.com/gpu borrowingLimit must be 4"
    )

    print("✓ kueue01 passed!")


if __name__ == "__main__":
    verify()

"""
Exercise: exercises/25_batch_kueue_volcano/volcano02.py
Topic: Volcano Queue & Fair-Share Scheduling

Instructions:
Fix the Volcano Queue manifest below to establish fair-share multi-tenant queue limits:
1. Set 'apiVersion' to 'scheduling.volcano.sh/v1beta1' and 'kind' to 'Queue'.
2. Set 'metadata.name' to 'ai-research-queue'.
3. Set 'spec.weight' to 1 (proportional weight for fair-share capacity sharing).
4. Set 'spec.capability' limits to:
   - 'cpu: "64"'
   - 'memory: 256Gi'
   - 'nvidia.com/gpu: "8"'
5. Set 'spec.reclaimable' to true to allow reclaiming resources when other queues need capacity.
"""

import yaml

from kubelings.validator import validate_manifest_text

VOLCANO_QUEUE_MANIFEST = """
apiVersion: ???
kind: ???
metadata:
  name: ???
spec:
  weight: 0
  capability:
    cpu: "0"
    memory: 0Gi
    nvidia.com/gpu: "0"
  reclaimable: false
"""


def verify():
    passed, errors = validate_manifest_text(VOLCANO_QUEUE_MANIFEST, "volcano02")
    assert passed, f"Volcano Queue manifest validation failed: {errors}"

    manifest = yaml.safe_load(VOLCANO_QUEUE_MANIFEST)
    assert manifest["metadata"]["name"] == "ai-research-queue", (
        "Queue name must be 'ai-research-queue'"
    )
    assert manifest["spec"]["weight"] == 1, "Queue weight must be 1"
    assert manifest["spec"]["reclaimable"] is True, "Queue reclaimable must be true"

    caps = manifest["spec"]["capability"]
    assert str(caps.get("cpu")) == "64", "cpu capability must be 64"
    assert str(caps.get("memory")) == "256Gi", "memory capability must be 256Gi"
    assert str(caps.get("nvidia.com/gpu")) == "8", "nvidia.com/gpu capability must be 8"

    print("✓ volcano02 passed!")


if __name__ == "__main__":
    verify()

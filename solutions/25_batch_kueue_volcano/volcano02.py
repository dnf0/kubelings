"""
Solution: solutions/25_batch_kueue_volcano/volcano02.py
Topic: Volcano Queue & Fair-Share Scheduling
"""

import yaml

from kubelings.validator import validate_manifest_text

VOLCANO_QUEUE_MANIFEST = """
apiVersion: scheduling.volcano.sh/v1beta1
kind: Queue
metadata:
  name: ai-research-queue
spec:
  weight: 1
  capability:
    cpu: "64"
    memory: 256Gi
    nvidia.com/gpu: "8"
  reclaimable: true
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

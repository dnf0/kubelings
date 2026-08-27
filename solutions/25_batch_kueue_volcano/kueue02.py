"""
Solution: solutions/25_batch_kueue_volcano/kueue02.py
Topic: Kueue LocalQueue & Suspended Workload Gating
"""

import yaml

from kubelings.validator import validate_manifest_text

KUEUE_JOB_MANIFEST = """
apiVersion: kueue.x-k8s.io/v1beta1
kind: LocalQueue
metadata:
  name: team-a-queue
  namespace: team-a
spec:
  clusterQueue: cluster-queue-ai
---
apiVersion: batch/v1
kind: Job
metadata:
  name: train-job
  namespace: team-a
  labels:
    kueue.x-k8s.io/queue-name: team-a-queue
spec:
  suspend: true
  template:
    spec:
      restartPolicy: Never
      containers:
        - name: trainer
          image: pytorch/pytorch:2.2.0-cuda12.1-cudnn8-runtime
"""


def verify():
    passed, errors = validate_manifest_text(KUEUE_JOB_MANIFEST, "kueue02")
    assert passed, f"Kueue LocalQueue and Job manifest validation failed: {errors}"

    docs = list(yaml.safe_load_all(KUEUE_JOB_MANIFEST))
    assert len(docs) == 2, "Manifest must define exactly 2 documents (LocalQueue and Job)"

    lq_doc = next((d for d in docs if d.get("kind") == "LocalQueue"), None)
    assert lq_doc is not None, "Missing LocalQueue document"
    assert lq_doc["metadata"]["name"] == "team-a-queue", "LocalQueue name must be 'team-a-queue'"
    assert lq_doc["metadata"]["namespace"] == "team-a", "LocalQueue namespace must be 'team-a'"
    assert lq_doc["spec"]["clusterQueue"] == "cluster-queue-ai", (
        "clusterQueue must be 'cluster-queue-ai'"
    )

    job_doc = next((d for d in docs if d.get("kind") == "Job"), None)
    assert job_doc is not None, "Missing Job document"
    assert job_doc["metadata"]["name"] == "train-job", "Job name must be 'train-job'"
    assert job_doc["metadata"]["namespace"] == "team-a", "Job namespace must be 'team-a'"
    assert (
        job_doc["metadata"].get("labels", {}).get("kueue.x-k8s.io/queue-name") == "team-a-queue"
    ), "Job label 'kueue.x-k8s.io/queue-name' must be 'team-a-queue'"
    assert job_doc["spec"].get("suspend") is True, "Job 'spec.suspend' must be true"

    c = job_doc["spec"]["template"]["spec"]["containers"][0]
    assert c["name"] == "trainer", "Container name must be 'trainer'"
    assert "pytorch" in c["image"], "Container image must be a PyTorch training image"

    print("✓ kueue02 passed!")


if __name__ == "__main__":
    verify()

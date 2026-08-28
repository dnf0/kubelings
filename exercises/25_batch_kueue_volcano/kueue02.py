"""
Exercise: exercises/25_batch_kueue_volcano/kueue02.py
Topic: Kueue LocalQueue & Suspended Workload Gating

Context & Why:
In multi-tenant Kubernetes clusters, developers submit jobs to namespace-scoped `LocalQueue` resources,
which map tenant namespaces to upstream cluster-wide `ClusterQueue` instances.

Workload Admission & Gating Mechanics:
- When developers submit standard Kubernetes `Job`, PyTorchJob, or RayJob resources, they must label the
  workload with `kueue.x-k8s.io/queue-name: <local-queue-name>`.
- The job is authored with `spec.suspend: true`. This prevents the standard Kubernetes job controller
  from spawning pods immediately and overwhelming cluster node resources.
- Kueue evaluates resource quotas in the associated ClusterQueue. Once capacity is available, Kueue's
  admission controller unsuspends the job (`spec.suspend: false`), allowing pods to schedule deterministically
  without causing resource thrashing or OOM issues.

Task:
Fix the Kueue LocalQueue and Batch Job manifests below:
1. Define a 'LocalQueue' named 'team-a-queue' in namespace 'team-a' with 'apiVersion: kueue.x-k8s.io/v1beta1'.
2. Point 'spec.clusterQueue' to 'cluster-queue-ai'.
3. Define a 'batch/v1' 'Job' named 'train-job' in namespace 'team-a'.
4. In 'metadata.labels', add label 'kueue.x-k8s.io/queue-name: team-a-queue' so Kueue intercepts the Job.
5. In Job 'spec', set 'suspend: true' to gate execution until Kueue admits the workload.
6. In 'spec.template.spec', configure container 'trainer' with image
   'pytorch/pytorch:2.2.0-cuda12.1-cudnn8-runtime' and 'restartPolicy: Never'.
"""

import yaml

from kubelings.validator import validate_manifest_text

# TODO: Complete the LocalQueue and suspended batch Job manifests with proper queue routing labels and admission gating flags.
# WHY: Suspended workload gating prevents uncoordinated job flooding, holding batch training jobs in a declarative queue until quota is admitted, avoiding out-of-memory and GPU contention failures on worker nodes.
KUEUE_JOB_MANIFEST = """
apiVersion: ???
kind: ???
metadata:
  name: ???
  namespace: ???
spec:
  clusterQueue: ???
---
apiVersion: ???
kind: ???
metadata:
  name: ???
  namespace: ???
  labels:
    kueue.x-k8s.io/queue-name: ???
spec:
  suspend: false
  template:
    spec:
      restartPolicy: ???
      containers:
        - name: ???
          image: ???
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

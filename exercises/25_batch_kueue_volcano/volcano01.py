"""
Exercise: exercises/25_batch_kueue_volcano/volcano01.py
Topic: Volcano Gang Scheduling & Deadlock Prevention

Instructions:
Fix the Volcano Job manifest below to perform all-or-nothing gang scheduling for distributed training:
1. Set 'apiVersion' to 'batch.volcano.sh/v1alpha1' and 'kind' to 'Job'.
2. Set 'metadata.name' to 'distributed-training-gang'.
3. Set 'spec.minAvailable' to 4 (ensuring all 4 distributed pods are scheduled together to prevent deadlocks).
4. Set 'spec.schedulerName' to 'volcano'.
5. In 'spec.tasks', configure:
   - Task 'master' with replicas: 1, restartPolicy: OnFailure, and container 'train-master'
     using image 'pytorch/pytorch:2.2.0-cuda12.1-cudnn8-runtime'.
   - Task 'worker' with replicas: 3, restartPolicy: OnFailure, and container 'train-worker'
     using image 'pytorch/pytorch:2.2.0-cuda12.1-cudnn8-runtime'.
"""

import yaml

from kubelings.validator import validate_manifest_text

VOLCANO_JOB_MANIFEST = """
apiVersion: ???
kind: ???
metadata:
  name: ???
spec:
  minAvailable: 0
  schedulerName: ???
  tasks:
    - name: master
      replicas: 0
      template:
        spec:
          restartPolicy: ???
          containers:
            - name: ???
              image: ???
    - name: worker
      replicas: 0
      template:
        spec:
          restartPolicy: ???
          containers:
            - name: ???
              image: ???
"""


def verify():
    passed, errors = validate_manifest_text(VOLCANO_JOB_MANIFEST, "volcano01")
    assert passed, f"Volcano Job manifest validation failed: {errors}"

    manifest = yaml.safe_load(VOLCANO_JOB_MANIFEST)
    assert manifest["metadata"]["name"] == "distributed-training-gang", (
        "Job name must be 'distributed-training-gang'"
    )
    assert manifest["spec"]["minAvailable"] == 4, "minAvailable must be 4 for gang scheduling"
    assert manifest["spec"]["schedulerName"] == "volcano", "schedulerName must be 'volcano'"

    tasks = manifest["spec"]["tasks"]
    assert len(tasks) == 2, "Must define 2 task groups (master and worker)"

    task_map = {t["name"]: t for t in tasks}
    assert "master" in task_map, "Must define 'master' task"
    assert "worker" in task_map, "Must define 'worker' task"

    assert task_map["master"]["replicas"] == 1, "Master replicas must be 1"
    assert task_map["worker"]["replicas"] == 3, "Worker replicas must be 3"

    total_replicas = sum(t["replicas"] for t in tasks)
    assert total_replicas == 4, "Total task replicas must sum to 4"

    master_c = task_map["master"]["template"]["spec"]["containers"][0]
    assert master_c["name"] == "train-master", "Master container name must be 'train-master'"

    worker_c = task_map["worker"]["template"]["spec"]["containers"][0]
    assert worker_c["name"] == "train-worker", "Worker container name must be 'train-worker'"

    print("✓ volcano01 passed!")


if __name__ == "__main__":
    verify()

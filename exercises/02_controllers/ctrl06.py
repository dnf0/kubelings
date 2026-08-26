"""
Exercise: exercises/02_controllers/ctrl06.py
Topic: Jobs & CronJobs

Instructions:
Kubernetes Jobs manage finite tasks to completion. CronJobs run Jobs on a time schedule.
Important: Pod templates in Jobs/CronJobs must specify restartPolicy as 'OnFailure' or 'Never'
('Always' is illegal in Jobs).

Complete the multi-document manifest below:
1. Job 'data-migration-job':
   - completions: 5
   - parallelism: 2
   - backoffLimit: 3
   - restartPolicy: 'OnFailure'
2. CronJob 'nightly-cleanup-cron':
   - schedule: '0 0 * * *' (midnight daily)
   - successfulJobsHistoryLimit: 3
   - restartPolicy: 'OnFailure'
"""

# I AM NOT DONE

import yaml
from kubelings.validator import validate_manifests

BATCH_MANIFESTS = """
apiVersion: batch/v1
kind: Job
metadata:
  name: data-migration-job
spec:
  completions: 0
  parallelism: 0
  backoffLimit: 0
  template:
    spec:
      restartPolicy: Always  # ERROR: Jobs do not support restartPolicy: Always
      containers:
      - name: worker
        image: busybox:1.36
---
apiVersion: batch/v1
kind: CronJob
metadata:
  name: nightly-cleanup-cron
spec:
  schedule: "????"
  successfulJobsHistoryLimit: 0
  jobTemplate:
    spec:
      template:
        spec:
          restartPolicy: OnFailure
          containers:
          - name: cleanup
            image: busybox:1.36
"""


def verify():
    manifests = list(yaml.safe_load_all(BATCH_MANIFESTS))
    assert len(manifests) == 2, "Must contain exactly 2 manifests (Job and CronJob)"
    validate_manifests(manifests, expected_kinds=["Job", "CronJob"])

    job, cronjob = manifests[0], manifests[1]

    # Job assertions
    assert job["metadata"]["name"] == "data-migration-job"
    assert job["spec"]["completions"] == 5, "Job completions must be 5"
    assert job["spec"]["parallelism"] == 2, "Job parallelism must be 2"
    assert job["spec"]["backoffLimit"] == 3, "Job backoffLimit must be 3"
    assert job["spec"]["template"]["spec"]["restartPolicy"] in (
        "OnFailure",
        "Never",
    ), "Job restartPolicy must be OnFailure or Never"

    # CronJob assertions
    assert cronjob["metadata"]["name"] == "nightly-cleanup-cron"
    assert cronjob["spec"]["schedule"] == "0 0 * * *", "CronJob schedule must be '0 0 * * *'"
    assert cronjob["spec"]["successfulJobsHistoryLimit"] == 3

    print("✓ ctrl06 passed!")


if __name__ == "__main__":
    verify()

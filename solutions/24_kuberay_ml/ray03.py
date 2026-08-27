"""
Solution: solutions/24_kuberay_ml/ray03.py
Topic: RayJob for Distributed Batch Fine-Tuning
"""

import yaml

from kubelings.validator import validate_manifest_text

RAY_JOB_MANIFEST = """
apiVersion: ray.io/v1
kind: RayJob
metadata:
  name: ray-finetune-job
spec:
  entrypoint: python fine_tune.py --epochs 3
  shutdownAfterJobFinishes: true
  ttlSecondsAfterFinished: 300
  rayClusterSpec:
    rayVersion: '2.35.0'
    headGroupSpec:
      rayStartParams:
        dashboard-host: '0.0.0.0'
      template:
        spec:
          containers:
            - name: ray-head
              image: rayproject/ray:2.35.0
"""


def verify():
    passed, errors = validate_manifest_text(RAY_JOB_MANIFEST, "ray03")
    assert passed, f"RayJob validation failed: {errors}"

    manifest = yaml.safe_load(RAY_JOB_MANIFEST)
    assert manifest["metadata"]["name"] == "ray-finetune-job"
    assert manifest["spec"]["entrypoint"] == "python fine_tune.py --epochs 3"
    assert manifest["spec"]["shutdownAfterJobFinishes"] is True
    assert manifest["spec"]["ttlSecondsAfterFinished"] == 300

    head_container = manifest["spec"]["rayClusterSpec"]["headGroupSpec"]["template"]["spec"][
        "containers"
    ][0]
    assert head_container["name"] == "ray-head"
    assert head_container["image"] == "rayproject/ray:2.35.0"

    print("✓ ray03 passed!")


if __name__ == "__main__":
    verify()

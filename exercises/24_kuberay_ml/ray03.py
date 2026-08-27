"""
Exercise: exercises/24_kuberay_ml/ray03.py
Topic: RayJob for Distributed Batch Fine-Tuning

Instructions:
Author a RayJob manifest named 'ray-finetune-job' for model fine-tuning:
1. Set 'apiVersion' to 'ray.io/v1' and 'kind' to 'RayJob'.
2. Set 'spec.entrypoint' to 'python fine_tune.py --epochs 3'.
3. Set 'spec.shutdownAfterJobFinishes' to True so cluster shuts down after completion.
4. Set 'spec.ttlSecondsAfterFinished' to 300 for automatic garbage collection.
5. In 'spec.rayClusterSpec', define 'rayVersion' as '2.35.0' and configure 'headGroupSpec'
   with container 'ray-head' using image 'rayproject/ray:2.35.0'.
"""

import yaml

from kubelings.validator import validate_manifest_text

RAY_JOB_MANIFEST = """
apiVersion: ray.io/v1
kind: RayJob
metadata:
  name: ray-finetune-job
spec:
  entrypoint: ???
  shutdownAfterJobFinishes: false
  ttlSecondsAfterFinished: 0
  rayClusterSpec:
    rayVersion: '2.35.0'
    headGroupSpec:
      rayStartParams:
        dashboard-host: '0.0.0.0'
      template:
        spec:
          containers:
            - name: ???
              image: ???
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

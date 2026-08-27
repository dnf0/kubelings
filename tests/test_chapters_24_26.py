import importlib.util
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from kubelings.validator import validate_manifest_text


def _load_module_from_path(file_path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(file_path.stem, file_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_ray01_raycluster_validation():
    valid_yaml = """
apiVersion: ray.io/v1
kind: RayCluster
metadata:
  name: ray-cluster-ml
spec:
  rayVersion: '2.35.0'
  headGroupSpec:
    rayStartParams:
      dashboard-host: '0.0.0.0'
      block: 'true'
    template:
      spec:
        containers:
          - name: ray-head
            image: rayproject/ray:2.35.0
            ports:
              - containerPort: 6379
                name: gcs
              - containerPort: 8265
                name: dashboard
  workerGroupSpecs:
    - groupName: worker-group
      replicas: 2
      minReplicas: 1
      maxReplicas: 5
      template:
        spec:
          containers:
            - name: ray-worker
              image: rayproject/ray:2.35.0
              resources:
                limits:
                  cpu: "2"
                  memory: 4Gi
"""
    passed, errors = validate_manifest_text(valid_yaml, "ray01")
    assert passed, f"Expected valid RayCluster to pass, got: {errors}"


def test_ray02_heterogeneous_pools():
    valid_yaml = """
apiVersion: ray.io/v1
kind: RayCluster
metadata:
  name: ray-cluster-heterogeneous
spec:
  headGroupSpec:
    rayStartParams:
      dashboard-host: '0.0.0.0'
    template:
      spec:
        containers:
          - name: ray-head
            image: rayproject/ray:2.35.0
  workerGroupSpecs:
    - groupName: cpu-workers
      replicas: 2
      minReplicas: 2
      maxReplicas: 10
      template:
        spec:
          containers:
            - name: ray-cpu-worker
              image: rayproject/ray:2.35.0
    - groupName: gpu-workers
      replicas: 1
      minReplicas: 0
      maxReplicas: 4
      template:
        spec:
          containers:
            - name: ray-gpu-worker
              image: rayproject/ray:2.35.0-gpu
              resources:
                limits:
                  nvidia.com/gpu: 1
"""
    passed, errors = validate_manifest_text(valid_yaml, "ray02")
    assert passed, f"Expected valid heterogeneous RayCluster to pass, got: {errors}"


def test_ray03_rayjob_validation():
    valid_yaml = """
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
    passed, errors = validate_manifest_text(valid_yaml, "ray03")
    assert passed, f"Expected valid RayJob to pass, got: {errors}"


def test_ray04_rayservice_validation():
    valid_yaml = """
apiVersion: ray.io/v1
kind: RayService
metadata:
  name: ray-llm-service
spec:
  serviceUnhealthyThreshold: 300
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
  serveConfigV2: |
    applications:
      - name: llm_app
        route_prefix: /v1
        import_path: llm_serve:model
        runtime_env: {}
"""
    passed, errors = validate_manifest_text(valid_yaml, "ray04")
    assert passed, f"Expected valid RayService to pass, got: {errors}"


def test_ray_invalid_manifests():
    # Empty manifest
    passed, errors = validate_manifest_text("", "ray01")
    assert not passed
    assert len(errors) > 0

    # RayCluster missing workerGroupSpecs
    invalid_cluster = """
apiVersion: ray.io/v1
kind: RayCluster
metadata:
  name: bad-cluster
spec:
  headGroupSpec:
    template:
      spec:
        containers:
          - name: ray-head
            image: rayproject/ray:2.35.0
"""
    passed, errors = validate_manifest_text(invalid_cluster, "ray01")
    assert not passed
    assert any("workerGroupSpecs" in err for err in errors)

    # RayJob missing entrypoint
    invalid_job = """
apiVersion: ray.io/v1
kind: RayJob
metadata:
  name: bad-job
spec:
  shutdownAfterJobFinishes: true
  ttlSecondsAfterFinished: 300
"""
    passed, errors = validate_manifest_text(invalid_job, "ray03")
    assert not passed
    assert any("entrypoint" in err for err in errors)

    # RayService missing serveConfigV2
    invalid_service = """
apiVersion: ray.io/v1
kind: RayService
metadata:
  name: bad-service
spec:
  serviceUnhealthyThreshold: 300
"""
    passed, errors = validate_manifest_text(invalid_service, "ray04")
    assert not passed
    assert any("serveConfigV2" in err for err in errors)


@pytest.mark.parametrize("ex_num", ["01", "02", "03", "04"])
def test_chapter_24_solutions_pass(ex_num: str):
    sol_path = Path(f"solutions/24_kuberay_ml/ray{ex_num}.py")
    assert sol_path.exists(), f"Solution file missing: {sol_path}"
    mod = _load_module_from_path(sol_path)
    mod.verify()


@pytest.mark.parametrize("ex_num", ["01", "02", "03", "04"])
def test_chapter_24_starters_fail(ex_num: str):
    ex_path = Path(f"exercises/24_kuberay_ml/ray{ex_num}.py")
    assert ex_path.exists(), f"Exercise file missing: {ex_path}"

    env = os.environ.copy()
    env["PYTHONPATH"] = f"{Path.cwd() / 'src'}:{env.get('PYTHONPATH', '')}".strip(":")
    proc = subprocess.run(
        [sys.executable, str(ex_path)],
        capture_output=True,
        text=True,
        timeout=10,
        env=env,
    )
    assert proc.returncode != 0, f"Starter {ex_path} should fail initially but returned 0."

"""
Validators for Chapter 24: Distributed AI & ML Orchestration with KubeRay
"""

from typing import Any

import yaml

from kubelings.validator import validate_manifest_text
from kubelings.validators import register_validator


@register_validator("ray01")
def validate_ray01(manifest: Any, raw_yaml: str = "") -> None:
    passed, errors = validate_manifest_text(raw_yaml, "ray01")
    assert passed, f"RayCluster manifest validation failed: {errors}"
    assert manifest["metadata"]["name"] == "ray-cluster-ml", "Cluster name must be 'ray-cluster-ml'"
    head_params = manifest["spec"]["headGroupSpec"]["rayStartParams"]
    assert head_params.get("dashboard-host") == "0.0.0.0", "dashboard-host must be '0.0.0.0'"
    assert head_params.get("block") == "true", "block must be 'true'"
    head_ports = manifest["spec"]["headGroupSpec"]["template"]["spec"]["containers"][0]["ports"]
    port_map = {p["name"]: p["containerPort"] for p in head_ports}
    assert port_map.get("gcs") == 6379, "GCS port must be 6379"
    assert port_map.get("dashboard") == 8265, "Dashboard port must be 8265"
    worker_spec = manifest["spec"]["workerGroupSpecs"][0]
    assert worker_spec["groupName"] == "worker-group", "Worker group name must be 'worker-group'"
    assert worker_spec["replicas"] == 2, "Worker replicas must be 2"
    assert worker_spec["minReplicas"] == 1, "minReplicas must be 1"
    assert worker_spec["maxReplicas"] == 5, "maxReplicas must be 5"
    worker_limits = worker_spec["template"]["spec"]["containers"][0]["resources"]["limits"]
    assert str(worker_limits.get("cpu")) == "2", "Worker CPU limit must be 2"
    assert str(worker_limits.get("memory")) == "4Gi", "Worker memory limit must be 4Gi"


@register_validator("ray02")
def validate_ray02(manifest: Any, raw_yaml: str = "") -> None:
    passed, errors = validate_manifest_text(raw_yaml, "ray02")
    assert passed, f"Heterogeneous RayCluster validation failed: {errors}"
    worker_groups = manifest["spec"]["workerGroupSpecs"]
    assert len(worker_groups) == 2, "Must have exactly 2 worker groups"
    cpu_group = next((g for g in worker_groups if g.get("groupName") == "cpu-workers"), None)
    assert cpu_group is not None, "Missing 'cpu-workers' group"
    assert cpu_group["replicas"] == 2
    assert cpu_group["minReplicas"] == 2
    assert cpu_group["maxReplicas"] == 10
    gpu_group = next((g for g in worker_groups if g.get("groupName") == "gpu-workers"), None)
    assert gpu_group is not None, "Missing 'gpu-workers' group"
    assert gpu_group["replicas"] == 1
    assert gpu_group["minReplicas"] == 0
    assert gpu_group["maxReplicas"] == 4
    gpu_container = gpu_group["template"]["spec"]["containers"][0]
    assert (
        gpu_container["resources"]["limits"]["nvidia.com/gpu"] == 1
        or gpu_container["resources"]["limits"]["nvidia.com/gpu"] == "1"
    )


@register_validator("ray03")
def validate_ray03(manifest: Any, raw_yaml: str = "") -> None:
    passed, errors = validate_manifest_text(raw_yaml, "ray03")
    assert passed, f"RayJob validation failed: {errors}"
    assert manifest["metadata"]["name"] == "ray-finetune-job"
    assert manifest["spec"]["entrypoint"] == "python fine_tune.py --epochs 3"
    assert manifest["spec"]["shutdownAfterJobFinishes"] is True
    assert manifest["spec"]["ttlSecondsAfterFinished"] == 300
    head_container = manifest["spec"]["rayClusterSpec"]["headGroupSpec"]["template"]["spec"][
        "containers"
    ][0]
    assert head_container["name"] == "ray-head"
    assert head_container["image"] == "rayproject/ray:2.35.0"


@register_validator("ray04")
def validate_ray04(manifest: Any, raw_yaml: str = "") -> None:
    passed, errors = validate_manifest_text(raw_yaml, "ray04")
    assert passed, f"RayService validation failed: {errors}"
    assert manifest["metadata"]["name"] == "ray-llm-service"
    assert manifest["spec"]["serviceUnhealthyThreshold"] == 300
    serve_cfg = yaml.safe_load(manifest["spec"]["serveConfigV2"])
    apps = serve_cfg.get("applications", [])
    assert len(apps) >= 1, "serveConfigV2 must contain at least 1 application"
    app = apps[0]
    assert app.get("name") == "llm_app", "Application name must be 'llm_app'"
    assert app.get("route_prefix") == "/v1", "Route prefix must be '/v1'"
    assert app.get("import_path") == "llm_serve:model", "Import path must be 'llm_serve:model'"

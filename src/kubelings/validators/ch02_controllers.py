"""
Validators for Chapter 02: Controllers & Replication
"""

import copy
from typing import Any, Dict, List

from kubelings.validator import validate_manifest, validate_manifests
from kubelings.validators import register_validator


@register_validator("ctrl01")
def validate_ctrl01(manifest: Any, raw_yaml: str = "") -> None:
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(manifest, expected_kind="ReplicaSet", expected_api_version="apps/v1")
    assert manifest["metadata"]["name"] == "frontend-rs"
    assert manifest["spec"]["replicas"] == 3, "spec.replicas must be 3"
    selector_labels = manifest["spec"]["selector"]["matchLabels"]
    template_labels = manifest["spec"]["template"]["metadata"]["labels"]
    assert selector_labels == {"app": "frontend", "env": "prod"}, (
        "selector.matchLabels must be {app: frontend, env: prod}"
    )
    assert template_labels == selector_labels, "template labels must match selector matchLabels"
    container = manifest["spec"]["template"]["spec"]["containers"][0]
    assert container["image"] == "nginx:alpine"


@register_validator("ctrl02")
def validate_ctrl02(manifest: Any, raw_yaml: str = "") -> None:
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(manifest, expected_kind="Deployment", expected_api_version="apps/v1")
    assert manifest["metadata"]["name"] == "api-deployment"
    assert manifest["spec"]["replicas"] == 4, "Replicas must equal 4"
    strategy = manifest["spec"].get("strategy", {})
    assert strategy.get("type") == "RollingUpdate", "Strategy type must be 'RollingUpdate'"
    rolling_update = strategy.get("rollingUpdate", {})
    assert rolling_update.get("maxSurge") == "25%", "maxSurge must be '25%'"
    assert rolling_update.get("maxUnavailable") == 0, "maxUnavailable must be 0"
    container = manifest["spec"]["template"]["spec"]["containers"][0]
    assert container["image"] == "python:3.12-slim"


def simulate_rollout_history(
    base_manifest: Dict[str, Any], new_images: List[str]
) -> List[Dict[str, Any]]:
    """Simulate deployment image rollouts and return pruned revision history list."""
    limit = base_manifest.get("spec", {}).get("revisionHistoryLimit", 10)
    current_manifest = copy.deepcopy(base_manifest)
    history: List[Dict[str, Any]] = []
    for idx, img in enumerate(new_images, start=1):
        current_manifest["spec"]["template"]["spec"]["containers"][0]["image"] = img
        history.append({"revision": idx, "image": img})
    if len(history) > limit:
        history = history[-limit:]
    return history


@register_validator("ctrl03")
def validate_ctrl03(manifest: Any, raw_yaml: str = "") -> None:
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(manifest, expected_kind="Deployment", expected_api_version="apps/v1")
    assert manifest["metadata"]["name"] == "versioned-app"
    assert manifest["spec"].get("revisionHistoryLimit") == 5, (
        "spec.revisionHistoryLimit must equal 5"
    )
    images = [f"nginx:1.{v}" for v in range(20, 28)]
    history = simulate_rollout_history(manifest, images)
    assert len(history) == 5, f"History should be pruned to 5 revisions, got {len(history)}"
    assert history[-1]["revision"] == 8, "Latest revision number must be 8"
    assert history[-1]["image"] == "nginx:1.27", "Latest image must be nginx:1.27"
    assert history[0]["revision"] == 4, "Oldest retained revision must be 4"


def generate_expected_pod_and_pvc_names(manifest_dict: dict) -> List[str]:
    """Generate the expected ordinal pod names for this statefulset."""
    name = manifest_dict["metadata"]["name"]
    replicas = manifest_dict["spec"]["replicas"]
    return [f"{name}-{i}" for i in range(replicas)]


@register_validator("ctrl04")
def validate_ctrl04(manifest: Any, raw_yaml: str = "") -> None:
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(manifest, expected_kind="StatefulSet", expected_api_version="apps/v1")
    assert manifest["metadata"]["name"] == "redis-cluster"
    assert manifest["spec"]["serviceName"] == "redis-headless", (
        "serviceName must be 'redis-headless'"
    )
    assert manifest["spec"]["replicas"] == 3, "Replicas must equal 3"
    vct = manifest["spec"].get("volumeClaimTemplates", [])
    assert len(vct) == 1, "Must define exactly 1 volumeClaimTemplate"
    assert vct[0]["metadata"]["name"] == "data"
    assert vct[0]["spec"]["accessModes"] == ["ReadWriteOnce"]
    assert vct[0]["spec"]["resources"]["requests"]["storage"] == "1Gi"
    pod_names = generate_expected_pod_and_pvc_names(manifest)
    assert pod_names == ["redis-cluster-0", "redis-cluster-1", "redis-cluster-2"]


@register_validator("ctrl05")
def validate_ctrl05(manifest: Any, raw_yaml: str = "") -> None:
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(manifest, expected_kind="DaemonSet", expected_api_version="apps/v1")
    assert manifest["metadata"]["name"] == "fluentbit-daemon"
    assert "replicas" not in manifest["spec"], "DaemonSet spec must NOT contain 'replicas'"
    pod_spec = manifest["spec"]["template"]["spec"]
    assert pod_spec.get("nodeSelector") == {"logging": "enabled"}, (
        "nodeSelector must be {'logging': 'enabled'}"
    )
    tolerations = pod_spec.get("tolerations", [])
    assert len(tolerations) == 1, "Must define control-plane toleration"
    assert tolerations[0].get("key") == "node-role.kubernetes.io/control-plane"
    assert tolerations[0].get("operator") == "Exists"
    assert tolerations[0].get("effect") == "NoSchedule"


BATCH_MANIFESTS = '\napiVersion: batch/v1\nkind: Job\nmetadata:\n  name: data-migration-job\nspec:\n  completions: 5\n  parallelism: 2\n  backoffLimit: 3\n  template:\n    spec:\n      restartPolicy: OnFailure\n      containers:\n      - name: worker\n        image: busybox:1.36\n---\napiVersion: batch/v1\nkind: CronJob\nmetadata:\n  name: nightly-cleanup-cron\nspec:\n  schedule: "0 0 * * *"\n  successfulJobsHistoryLimit: 3\n  jobTemplate:\n    spec:\n      template:\n        spec:\n          restartPolicy: OnFailure\n          containers:\n          - name: cleanup\n            image: busybox:1.36\n'


@register_validator("ctrl06")
def validate_ctrl06(manifest: Any, raw_yaml: str = "") -> None:
    manifests = manifest if isinstance(manifest, list) else [manifest]
    assert len(manifests) == 2, "Must contain exactly 2 manifests (Job and CronJob)"
    validate_manifests(manifests, expected_kinds=["Job", "CronJob"])
    job, cronjob = (manifests[0], manifests[1])
    assert job["metadata"]["name"] == "data-migration-job"
    assert job["spec"]["completions"] == 5, "Job completions must be 5"
    assert job["spec"]["parallelism"] == 2, "Job parallelism must be 2"
    assert job["spec"]["backoffLimit"] == 3, "Job backoffLimit must be 3"
    assert job["spec"]["template"]["spec"]["restartPolicy"] in ("OnFailure", "Never"), (
        "Job restartPolicy must be OnFailure or Never"
    )
    assert cronjob["metadata"]["name"] == "nightly-cleanup-cron"
    assert cronjob["spec"]["schedule"] == "0 0 * * *", "CronJob schedule must be '0 0 * * *'"
    assert cronjob["spec"]["successfulJobsHistoryLimit"] == 3

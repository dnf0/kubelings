"""
Validators for Chapter 25: AI Batch Scheduling & Queuing with Kueue and Volcano
"""

from typing import Any

from kubelings.validator import validate_manifest_text
from kubelings.validators import register_validator


@register_validator("kueue01")
def validate_kueue01(manifest: Any, raw_yaml: str = "") -> None:
    passed, errors = validate_manifest_text(raw_yaml, "kueue01")
    assert passed, f"Kueue manifest validation failed: {errors}"
    docs = manifest if isinstance(manifest, list) else [manifest]
    assert len(docs) == 2, (
        "Manifest must define exactly 2 documents (ResourceFlavor and ClusterQueue)"
    )
    flavor_doc = next((d for d in docs if d.get("kind") == "ResourceFlavor"), None)
    assert flavor_doc is not None, "Missing ResourceFlavor document"
    assert flavor_doc["metadata"]["name"] == "default-flavor", (
        "ResourceFlavor name must be 'default-flavor'"
    )
    queue_doc = next((d for d in docs if d.get("kind") == "ClusterQueue"), None)
    assert queue_doc is not None, "Missing ClusterQueue document"
    assert queue_doc["metadata"]["name"] == "cluster-queue-ai", (
        "ClusterQueue name must be 'cluster-queue-ai'"
    )
    assert queue_doc["spec"]["cohort"] == "ai-research-cohort", (
        "Cohort must be 'ai-research-cohort'"
    )
    rg = queue_doc["spec"]["resourceGroups"][0]
    covered = set(rg["coveredResources"])
    assert "cpu" in covered, "coveredResources must include 'cpu'"
    assert "memory" in covered, "coveredResources must include 'memory'"
    assert "nvidia.com/gpu" in covered, "coveredResources must include 'nvidia.com/gpu'"
    flavor = rg["flavors"][0]
    assert flavor["name"] == "default-flavor", "Flavor name must be 'default-flavor'"
    res_map = {r["name"]: r for r in flavor["resources"]}
    assert str(res_map["cpu"]["nominalQuota"]) == "64", "cpu nominalQuota must be 64"
    assert str(res_map["cpu"].get("borrowingLimit")) == "32", "cpu borrowingLimit must be 32"
    assert str(res_map["memory"]["nominalQuota"]) == "256Gi", "memory nominalQuota must be 256Gi"
    assert str(res_map["nvidia.com/gpu"]["nominalQuota"]) == "8", (
        "nvidia.com/gpu nominalQuota must be 8"
    )
    assert str(res_map["nvidia.com/gpu"].get("borrowingLimit")) == "4", (
        "nvidia.com/gpu borrowingLimit must be 4"
    )


@register_validator("kueue02")
def validate_kueue02(manifest: Any, raw_yaml: str = "") -> None:
    passed, errors = validate_manifest_text(raw_yaml, "kueue02")
    assert passed, f"Kueue LocalQueue and Job manifest validation failed: {errors}"
    docs = manifest if isinstance(manifest, list) else [manifest]
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


@register_validator("volcano01")
def validate_volcano01(manifest: Any, raw_yaml: str = "") -> None:
    passed, errors = validate_manifest_text(raw_yaml, "volcano01")
    assert passed, f"Volcano Job manifest validation failed: {errors}"
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
    total_replicas = sum((t["replicas"] for t in tasks))
    assert total_replicas == 4, "Total task replicas must sum to 4"
    master_c = task_map["master"]["template"]["spec"]["containers"][0]
    assert master_c["name"] == "train-master", "Master container name must be 'train-master'"
    worker_c = task_map["worker"]["template"]["spec"]["containers"][0]
    assert worker_c["name"] == "train-worker", "Worker container name must be 'train-worker'"


@register_validator("volcano02")
def validate_volcano02(manifest: Any, raw_yaml: str = "") -> None:
    passed, errors = validate_manifest_text(raw_yaml, "volcano02")
    assert passed, f"Volcano Queue manifest validation failed: {errors}"
    assert manifest["metadata"]["name"] == "ai-research-queue", (
        "Queue name must be 'ai-research-queue'"
    )
    assert manifest["spec"]["weight"] == 1, "Queue weight must be 1"
    assert manifest["spec"]["reclaimable"] is True, "Queue reclaimable must be true"
    caps = manifest["spec"]["capability"]
    assert str(caps.get("cpu")) == "64", "cpu capability must be 64"
    assert str(caps.get("memory")) == "256Gi", "memory capability must be 256Gi"
    assert str(caps.get("nvidia.com/gpu")) == "8", "nvidia.com/gpu capability must be 8"

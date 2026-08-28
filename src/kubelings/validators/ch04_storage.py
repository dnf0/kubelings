"""
Validators for Chapter 04: Storage & Persistent Volumes
"""

from typing import Any, Dict

import yaml

from kubelings.validator import validate_manifest, validate_manifests
from kubelings.validators import register_validator


@register_validator("storage01")
def validate_storage01(manifest: Any, raw_yaml: str = "") -> None:
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(manifest, expected_kind="Pod", expected_api_version="v1")
    assert manifest["metadata"]["name"] == "log-collector-pod", (
        "Pod name must be 'log-collector-pod'"
    )
    container = manifest["spec"]["containers"][0]
    assert container["name"] == "collector"
    assert container["image"] == "busybox:1.36"
    mounts = {m["name"]: m for m in container.get("volumeMounts", [])}
    assert "scratch-volume" in mounts, "scratch-volume must be mounted"
    assert mounts["scratch-volume"]["mountPath"] == "/tmp/scratch"
    assert "host-log-volume" in mounts, "host-log-volume must be mounted"
    assert mounts["host-log-volume"]["mountPath"] == "/var/log/host-app"
    assert mounts["host-log-volume"].get("readOnly") is True
    volumes = {v["name"]: v for v in manifest["spec"].get("volumes", [])}
    assert "scratch-volume" in volumes, "Volume 'scratch-volume' missing in spec.volumes"
    assert isinstance(volumes["scratch-volume"].get("emptyDir"), dict)
    assert "host-log-volume" in volumes, "Volume 'host-log-volume' missing in spec.volumes"
    host_path = volumes["host-log-volume"].get("hostPath", {})
    assert host_path.get("path") == "/var/log/app"
    assert host_path.get("type") == "DirectoryOrCreate"


MANIFESTS = "\napiVersion: v1\nkind: PersistentVolume\nmetadata:\n  name: task-pv\nspec:\n  capacity:\n    storage: 10Gi\n  accessModes:\n    - ReadWriteOnce\n  storageClassName: manual\n  hostPath:\n    path: /mnt/data\n---\napiVersion: v1\nkind: PersistentVolumeClaim\nmetadata:\n  name: task-pvc\nspec:\n  accessModes:\n    - ReadWriteOnce\n  storageClassName: manual\n  resources:\n    requests:\n      storage: 5Gi\n"


def _parse_storage_str(val: str) -> int:
    """Parse storage string like '5Gi' or '10Mi' into bytes."""
    val = val.strip()
    if val.endswith("Gi"):
        return int(val[:-2]) * 1024 * 1024 * 1024
    if val.endswith("Mi"):
        return int(val[:-2]) * 1024 * 1024
    if val.endswith("Ki"):
        return int(val[:-2]) * 1024
    return int(val)


def check_pvc_matches_pv(pv: Dict[str, Any], pvc: Dict[str, Any]) -> bool:
    """Check whether a PersistentVolume satisfies a PersistentVolumeClaim request."""
    pv_spec = pv.get("spec", {})
    pvc_spec = pvc.get("spec", {})
    if pv_spec.get("storageClassName") != pvc_spec.get("storageClassName"):
        return False
    pv_capacity_str = pv_spec.get("capacity", {}).get("storage", "0")
    pvc_request_str = pvc_spec.get("resources", {}).get("requests", {}).get("storage", "0")
    if _parse_storage_str(pv_capacity_str) < _parse_storage_str(pvc_request_str):
        return False
    pv_modes = set(pv_spec.get("accessModes", []))
    pvc_modes = set(pvc_spec.get("accessModes", []))
    if not pvc_modes.issubset(pv_modes):
        return False
    return True


@register_validator("storage02")
def validate_storage02(manifest: Any, raw_yaml: str = "") -> None:
    manifests = manifest if isinstance(manifest, list) else [manifest]
    assert len(manifests) == 2, "Must contain exactly 2 manifests (PV and PVC)"
    validate_manifests(manifests, expected_kinds=["PersistentVolume", "PersistentVolumeClaim"])
    pv, pvc = (manifests[0], manifests[1])
    assert pv["metadata"]["name"] == "task-pv"
    assert pv["spec"]["capacity"]["storage"] == "10Gi"
    assert pv["spec"]["accessModes"] == ["ReadWriteOnce"]
    assert pv["spec"]["storageClassName"] == "manual"
    assert pv["spec"]["hostPath"]["path"] == "/mnt/data"
    assert pvc["metadata"]["name"] == "task-pvc"
    assert pvc["spec"]["accessModes"] == ["ReadWriteOnce"]
    assert pvc["spec"]["resources"]["requests"]["storage"] == "5Gi"
    assert pvc["spec"]["storageClassName"] == "manual"
    assert check_pvc_matches_pv(pv, pvc) is True, "PV should satisfy PVC requirements"
    incompatible_pvc = yaml.safe_load(yaml.dump(pvc))
    incompatible_pvc["spec"]["resources"]["requests"]["storage"] = "20Gi"
    assert check_pvc_matches_pv(pv, incompatible_pvc) is False, "PV should not satisfy 20Gi request"
    incompatible_sc = yaml.safe_load(yaml.dump(pvc))
    incompatible_sc["spec"]["storageClassName"] = "fast-ssd"
    assert check_pvc_matches_pv(pv, incompatible_sc) is False, (
        "PV should not satisfy mismatched storageClass"
    )


def evaluate_reclaim_lifecycle(reclaim_policy: str, pvc_deleted: bool) -> str:
    """Determine the PV status outcome when its bound PVC is deleted."""
    if not pvc_deleted:
        return "BOUND"
    if reclaim_policy == "Retain":
        return "RELEASED_RETAINED"
    elif reclaim_policy == "Delete":
        return "STORAGE_DELETED"
    elif reclaim_policy == "Recycle":
        return "SCRUBBED_AVAILABLE"
    else:
        raise ValueError(f"Unknown reclaim policy: {reclaim_policy}")


@register_validator("storage03")
def validate_storage03(manifest: Any, raw_yaml: str = "") -> None:
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(manifest, expected_kind="PersistentVolume", expected_api_version="v1")
    assert manifest["metadata"]["name"] == "shared-nfs-pv"
    assert manifest["spec"]["capacity"]["storage"] == "50Gi"
    modes = set(manifest["spec"]["accessModes"])
    assert modes == {"ReadWriteMany", "ReadOnlyMany"}, "Must support RWX and ROX access modes"
    assert manifest["spec"]["persistentVolumeReclaimPolicy"] == "Retain"
    assert manifest["spec"]["storageClassName"] == "nfs-storage"
    assert manifest["spec"]["nfs"]["server"] == "10.0.0.100"
    assert manifest["spec"]["nfs"]["path"] == "/exports/shared"
    assert evaluate_reclaim_lifecycle("Retain", pvc_deleted=False) == "BOUND"
    assert evaluate_reclaim_lifecycle("Retain", pvc_deleted=True) == "RELEASED_RETAINED"
    assert evaluate_reclaim_lifecycle("Delete", pvc_deleted=True) == "STORAGE_DELETED"
    assert evaluate_reclaim_lifecycle("Recycle", pvc_deleted=True) == "SCRUBBED_AVAILABLE"
    try:
        evaluate_reclaim_lifecycle("InvalidPolicy", pvc_deleted=True)
        raise AssertionError("Expected ValueError on invalid policy")
    except ValueError:
        pass


@register_validator("storage04")
def validate_storage04(manifest: Any, raw_yaml: str = "") -> None:
    manifests = manifest if isinstance(manifest, list) else [manifest]
    assert len(manifests) == 2, "Must define 2 manifests (StorageClass and PVC)"
    validate_manifests(manifests, expected_kinds=["StorageClass", "PersistentVolumeClaim"])
    sc, pvc = (manifests[0], manifests[1])
    assert sc["metadata"]["name"] == "fast-ebs"
    assert sc["provisioner"] == "ebs.csi.aws.com"
    assert sc["volumeBindingMode"] == "WaitForFirstConsumer"
    assert sc["reclaimPolicy"] == "Delete"
    assert sc.get("allowVolumeExpansion") is True
    assert sc["parameters"]["type"] == "gp3"
    assert sc["parameters"]["iops"] == "3000"
    assert sc["parameters"]["encrypted"] == "true"
    assert pvc["metadata"]["name"] == "dynamic-db-pvc"
    assert pvc["spec"]["storageClassName"] == "fast-ebs"
    assert pvc["spec"]["accessModes"] == ["ReadWriteOnce"]
    assert pvc["spec"]["resources"]["requests"]["storage"] == "20Gi"


def validate_expansion_request(
    initial_size_str: str, new_size_str: str, allow_expansion: bool
) -> bool:
    """Determine if a PVC resize request is permissible."""
    if not allow_expansion:
        return False
    initial_bytes = _parse_storage_str(initial_size_str)
    new_bytes = _parse_storage_str(new_size_str)
    return new_bytes > initial_bytes


@register_validator("storage05")
def validate_storage05(manifest: Any, raw_yaml: str = "") -> None:
    manifests = manifest if isinstance(manifest, list) else [manifest]
    assert len(manifests) == 3, "Must define 3 manifests (VolumeSnapshotClass, VolumeSnapshot, PVC)"
    validate_manifests(
        manifests, expected_kinds=["VolumeSnapshotClass", "VolumeSnapshot", "PersistentVolumeClaim"]
    )
    vsc, snap, pvc = (manifests[0], manifests[1], manifests[2])
    assert vsc["metadata"]["name"] == "csi-aws-vsc"
    assert vsc["driver"] == "ebs.csi.aws.com"
    assert vsc["deletionPolicy"] == "Delete"
    assert snap["metadata"]["name"] == "prod-db-snap-01"
    assert snap["spec"]["volumeSnapshotClassName"] == "csi-aws-vsc"
    assert snap["spec"]["source"]["persistentVolumeClaimName"] == "dynamic-db-pvc"
    assert pvc["metadata"]["name"] == "restored-db-pvc"
    assert pvc["spec"]["dataSource"]["name"] == "prod-db-snap-01"
    assert pvc["spec"]["dataSource"]["kind"] == "VolumeSnapshot"
    assert pvc["spec"]["dataSource"]["apiGroup"] == "snapshot.storage.k8s.io"
    assert validate_expansion_request("10Gi", "20Gi", allow_expansion=True) is True
    assert validate_expansion_request("10Gi", "10Gi", allow_expansion=True) is False
    assert validate_expansion_request("20Gi", "10Gi", allow_expansion=True) is False, (
        "Cannot shrink volumes"
    )
    assert validate_expansion_request("10Gi", "20Gi", allow_expansion=False) is False, (
        "Expansion disabled on StorageClass"
    )

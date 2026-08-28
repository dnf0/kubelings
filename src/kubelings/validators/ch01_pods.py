"""
Validators for Chapter 01: Kubernetes Core Workloads & Pods
"""

from typing import Any, Dict

from kubelings.validator import validate_manifest
from kubelings.validators import register_validator


@register_validator("pods01")
def validate_pods01(manifest: Any, raw_yaml: str = "") -> None:
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(manifest, expected_kind="Pod", expected_api_version="v1")
    assert manifest["metadata"]["name"] == "nginx-web", "Pod name must be 'nginx-web'"
    assert manifest["metadata"]["labels"]["app"] == "web", "Label 'app' must equal 'web'"
    container = manifest["spec"]["containers"][0]
    assert container["name"] == "nginx", "Container name must be 'nginx'"
    assert container["image"] == "nginx:alpine", "Container image must be 'nginx:alpine'"
    assert container["ports"][0]["containerPort"] == 80, "Container port must be 80"


@register_validator("pods02")
def validate_pods02(manifest: Any, raw_yaml: str = "") -> None:
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(manifest, expected_kind="Pod", expected_api_version="v1")
    assert manifest["metadata"]["name"] == "web-logger", "Pod name must be 'web-logger'"
    volumes = manifest["spec"].get("volumes", [])
    assert len(volumes) >= 1, "Must define at least one volume"
    assert volumes[0]["name"] == "shared-logs", "Volume name must be 'shared-logs'"
    assert "emptyDir" in volumes[0], "Volume must be of type emptyDir"
    containers = manifest["spec"]["containers"]
    assert len(containers) == 2, "Pod must contain exactly 2 containers (app and sidecar-logger)"
    c1 = containers[0]
    assert c1["name"] == "app"
    assert c1["image"] == "alpine:3.19"
    assert c1["volumeMounts"][0]["name"] == "shared-logs"
    assert c1["volumeMounts"][0]["mountPath"] == "/var/log/app"
    c2 = containers[1]
    assert c2["name"] == "sidecar-logger"
    assert c2["image"] == "busybox:1.36"
    assert c2["volumeMounts"][0]["name"] == "shared-logs"
    assert c2["volumeMounts"][0]["mountPath"] == "/var/log/shared"
    assert c2["volumeMounts"][0].get("readOnly") is True, (
        "Sidecar volumeMount must be readOnly: true"
    )


@register_validator("pods03")
def validate_pods03(manifest: Any, raw_yaml: str = "") -> None:
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(manifest, expected_kind="Pod", expected_api_version="v1")
    assert manifest["metadata"]["name"] == "init-service-demo"
    init_containers = manifest["spec"].get("initContainers", [])
    assert len(init_containers) == 1, "Must define exactly 1 initContainer"
    init_c = init_containers[0]
    assert init_c["name"] == "init-db-wait", "Init container name must be 'init-db-wait'"
    assert init_c["image"] == "busybox:1.36", "Init container image must be 'busybox:1.36'"
    assert "waiting for db" in str(init_c.get("command", "")), (
        "Init command must contain 'waiting for db'"
    )
    containers = manifest["spec"]["containers"]
    assert len(containers) == 1, "Must define exactly 1 main container"
    assert containers[0]["name"] == "main-app"
    assert containers[0]["image"] == "nginx:alpine"


def compute_qos_class(pod_dict: Dict[str, Any]) -> str:
    """Calculate the Kubernetes QoS class (Guaranteed, Burstable, BestEffort)."""
    containers = pod_dict.get("spec", {}).get("containers", [])
    if not containers:
        return "BestEffort"
    has_any_request_or_limit = False
    all_have_equal_limits_and_requests = True
    for c in containers:
        res = c.get("resources", {})
        requests = res.get("requests", {})
        limits = res.get("limits", {})
        req_cpu = requests.get("cpu")
        req_mem = requests.get("memory")
        lim_cpu = limits.get("cpu")
        lim_mem = limits.get("memory")
        if req_cpu or req_mem or lim_cpu or lim_mem:
            has_any_request_or_limit = True
        if not lim_cpu or not lim_mem:
            all_have_equal_limits_and_requests = False
        else:
            effective_req_cpu = req_cpu if req_cpu is not None else lim_cpu
            effective_req_mem = req_mem if req_mem is not None else lim_mem
            if effective_req_cpu != lim_cpu or effective_req_mem != lim_mem:
                all_have_equal_limits_and_requests = False
    if not has_any_request_or_limit:
        return "BestEffort"
    if all_have_equal_limits_and_requests:
        return "Guaranteed"
    return "Burstable"


@register_validator("pods04")
def validate_pods04(manifest: Any, raw_yaml: str = "") -> None:
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(manifest, expected_kind="Pod", expected_api_version="v1")
    res = manifest["spec"]["containers"][0]["resources"]
    assert res["requests"]["cpu"] == "500m"
    assert res["requests"]["memory"] == "256Mi"
    assert res["limits"]["cpu"] == "500m"
    assert res["limits"]["memory"] == "256Mi"
    assert compute_qos_class(manifest) == "Guaranteed"
    burstable_manifest = {
        "apiVersion": "v1",
        "kind": "Pod",
        "metadata": {"name": "burstable-pod"},
        "spec": {
            "containers": [
                {
                    "name": "worker",
                    "image": "busybox",
                    "resources": {
                        "requests": {"cpu": "100m", "memory": "128Mi"},
                        "limits": {"cpu": "200m", "memory": "256Mi"},
                    },
                }
            ]
        },
    }
    assert compute_qos_class(burstable_manifest) == "Burstable"
    best_effort_manifest = {
        "apiVersion": "v1",
        "kind": "Pod",
        "metadata": {"name": "best-effort-pod"},
        "spec": {"containers": [{"name": "worker", "image": "busybox"}]},
    }
    assert compute_qos_class(best_effort_manifest) == "BestEffort"


@register_validator("pods05")
def validate_pods05(manifest: Any, raw_yaml: str = "") -> None:
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(manifest, expected_kind="Pod", expected_api_version="v1")
    assert manifest["metadata"]["name"] == "downward-api-pod"
    env_vars = manifest["spec"]["containers"][0].get("env", [])
    assert len(env_vars) == 4, "Must define all 4 Downward API environment variables"
    env_map = {item["name"]: item["valueFrom"]["fieldRef"]["fieldPath"] for item in env_vars}
    assert env_map.get("MY_POD_NAME") == "metadata.name", "MY_POD_NAME must reference metadata.name"
    assert env_map.get("MY_POD_NAMESPACE") == "metadata.namespace", (
        "MY_POD_NAMESPACE must reference metadata.namespace"
    )
    assert env_map.get("MY_POD_IP") == "status.podIP", "MY_POD_IP must reference status.podIP"
    assert env_map.get("MY_NODE_NAME") == "spec.nodeName", (
        "MY_NODE_NAME must reference spec.nodeName"
    )


@register_validator("pods06")
def validate_pods06(manifest: Any, raw_yaml: str = "") -> None:
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(
        manifest, expected_kind="PodDisruptionBudget", expected_api_version="policy/v1"
    )
    assert manifest["metadata"]["name"] == "web-pdb", "PDB name must be 'web-pdb'"
    assert manifest["spec"].get("minAvailable") == 2, "spec.minAvailable must equal 2"
    selector = manifest["spec"].get("selector", {}).get("matchLabels", {})
    assert selector.get("app") == "web", "selector.matchLabels.app must equal 'web'"

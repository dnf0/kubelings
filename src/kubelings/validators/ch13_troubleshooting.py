"""
Validators for Chapter 13: Observability, Debugging & Production Troubleshooting
"""

from typing import Any, Dict, List

from kubelings.validator import validate_manifest, validate_manifests
from kubelings.validators import register_validator


def diagnose_exit_code(exit_code: int) -> Dict[str, Any]:
    if exit_code == 137:
        return {
            "reason": "OOMKilled",
            "cause": "Container exceeded memory limit and was killed by Linux kernel OOM killer",
        }
    elif exit_code == 143:
        return {"reason": "SIGTERM", "cause": "Graceful termination initiated by Kubernetes"}
    elif exit_code == 1:
        return {
            "reason": "ApplicationError",
            "cause": "Uncaught application exception or missing environment variables",
        }
    elif exit_code == 127:
        return {
            "reason": "CommandNotFound",
            "cause": "Container entrypoint binary or command not found in image PATH",
        }
    else:
        return {"reason": "Unknown", "cause": f"Unexpected exit code {exit_code}"}


@register_validator("troubleshoot01")
def validate_troubleshoot01(manifest: Any, raw_yaml: str = "") -> None:
    diag137 = diagnose_exit_code(137)
    assert diag137["reason"] == "OOMKilled"
    assert "memory" in diag137["cause"].lower()
    diag143 = diagnose_exit_code(143)
    assert diag143["reason"] == "SIGTERM"
    diag1 = diagnose_exit_code(1)
    assert diag1["reason"] == "ApplicationError"
    diag127 = diagnose_exit_code(127)
    assert diag127["reason"] == "CommandNotFound"
    diag_unknown = diagnose_exit_code(99)
    assert diag_unknown["reason"] == "Unknown"
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(manifest, expected_kind="Pod", expected_api_version="v1")
    metadata = manifest.get("metadata", {})
    assert metadata.get("name") == "crasher-pod-fixed"
    assert metadata.get("namespace") == "troubleshoot"
    container = manifest.get("spec", {}).get("containers", [])[0]
    assert container.get("name") == "api-server"
    res = container.get("resources", {})
    assert res.get("requests", {}).get("cpu") == "250m"
    assert res.get("requests", {}).get("memory") == "256Mi"
    assert res.get("limits", {}).get("cpu") == "500m"
    assert res.get("limits", {}).get("memory") == "512Mi"
    env_vars = container.get("env", [])
    db_env = next((e for e in env_vars if e.get("name") == "DATABASE_URL"), None)
    assert db_env is not None, "Must define DATABASE_URL environment variable"
    assert db_env.get("value") == "postgres://db.internal:5432/app"


MANIFESTS = '\napiVersion: v1\nkind: Secret\nmetadata:\n  name: regcred\n  namespace: finance\ntype: kubernetes.io/dockerconfigjson\nstringData:\n  .dockerconfigjson: \'{"auths":{"privateregistry.io":{"username":"finance-bot","password":"secrettoken"}}}\'\n---\napiVersion: v1\nkind: Pod\nmetadata:\n  name: payment-service\n  namespace: finance\nspec:\n  imagePullSecrets:\n  - name: regcred\n  containers:\n  - name: app\n    image: privateregistry.io/payment-app:v1.0.0\n'


@register_validator("troubleshoot02")
def validate_troubleshoot02(manifest: Any, raw_yaml: str = "") -> None:
    manifests = manifest if isinstance(manifest, list) else [manifest]
    assert len(manifests) == 2, "Must contain exactly 2 manifests (Secret and Pod)"
    validate_manifests(manifests, expected_kinds=["Secret", "Pod"])
    secret, pod = (manifests[0], manifests[1])
    assert secret["metadata"]["name"] == "regcred"
    assert secret["metadata"]["namespace"] == "finance"
    assert secret.get("type") == "kubernetes.io/dockerconfigjson"
    assert pod["metadata"]["name"] == "payment-service"
    assert pod["metadata"]["namespace"] == "finance"
    image_pull_secrets = pod["spec"].get("imagePullSecrets", [])
    assert len(image_pull_secrets) == 1
    assert image_pull_secrets[0].get("name") == "regcred"
    container = pod["spec"]["containers"][0]
    assert container["name"] == "app"
    assert container["image"] == "privateregistry.io/payment-app:v1.0.0"


@register_validator("troubleshoot03")
def validate_troubleshoot03(manifest: Any, raw_yaml: str = "") -> None:
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(manifest, expected_kind="Pod", expected_api_version="v1")
    metadata = manifest.get("metadata", {})
    assert metadata.get("name") == "gpu-worker"
    assert metadata.get("namespace") == "ml-workloads"
    spec = manifest.get("spec", {})
    node_sel = spec.get("nodeSelector", {})
    assert node_sel.get("node-type") == "gpu-compute-node", (
        "nodeSelector must target 'gpu-compute-node'"
    )
    tolerations = spec.get("tolerations", [])
    assert len(tolerations) >= 1, "Must define at least one toleration"
    tol = next((t for t in tolerations if t.get("key") == "sku"), None)
    assert tol is not None, "Must define toleration for key 'sku'"
    assert tol.get("operator") == "Equal"
    assert tol.get("value") == "gpu-worker"
    assert tol.get("effect") == "NoSchedule"
    container = spec.get("containers", [])[0]
    reqs = container.get("resources", {}).get("requests", {})
    assert reqs.get("cpu") == "1", "CPU request must be '1'"
    assert reqs.get("memory") == "2Gi", "Memory request must be '2Gi'"


@register_validator("troubleshoot04")
def validate_troubleshoot04(manifest: Any, raw_yaml: str = "") -> None:
    manifests = manifest if isinstance(manifest, list) else [manifest]
    assert len(manifests) == 2, "Must contain exactly 2 manifests (ResourceQuota and LimitRange)"
    validate_manifests(manifests, expected_kinds=["ResourceQuota", "LimitRange"])
    quota, limit_range = (manifests[0], manifests[1])
    assert quota["metadata"]["name"] == "compute-quota"
    assert quota["metadata"]["namespace"] == "team-billing"
    hard = quota.get("spec", {}).get("hard", {})
    assert hard.get("requests.cpu") == "4"
    assert hard.get("requests.memory") == "8Gi"
    assert hard.get("limits.cpu") == "8"
    assert hard.get("limits.memory") == "16Gi"
    assert hard.get("pods") == "10"
    assert limit_range["metadata"]["name"] == "container-limits"
    assert limit_range["metadata"]["namespace"] == "team-billing"
    limits = limit_range.get("spec", {}).get("limits", [])
    assert len(limits) == 1
    c_limit = limits[0]
    assert c_limit.get("type") == "Container"
    assert c_limit.get("default") == {"cpu": "500m", "memory": "512Mi"}
    assert c_limit.get("defaultRequest") == {"cpu": "200m", "memory": "256Mi"}
    assert c_limit.get("max") == {"cpu": "2", "memory": "2Gi"}
    assert c_limit.get("min") == {"cpu": "100m", "memory": "128Mi"}


DEBUG_EPHEMERAL_CONTAINER: Dict[str, Any] = {
    "name": "debugger",
    "image": "busybox:1.36",
    "command": ["sh"],
    "targetContainerName": "app",
    "stdin": True,
    "tty": True,
}


def triage_events(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    critical_reasons = {"OOMKilled", "FailedScheduling", "BackOff", "Unhealthy"}
    filtered = []
    for e in events:
        if e.get("type") == "Warning":
            count = e.get("count", 1)
            reason = e.get("reason", "")
            if count >= 3 or reason in critical_reasons:
                filtered.append({"reason": reason, "message": e.get("message", ""), "count": count})
    filtered.sort(key=lambda x: x["count"], reverse=True)
    return filtered


@register_validator("troubleshoot05")
def validate_troubleshoot05(manifest: Any, raw_yaml: str = "") -> None:
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(manifest, expected_kind="Pod", expected_api_version="v1")
    metadata = manifest.get("metadata", {})
    assert metadata.get("name") == "distroless-app"
    assert metadata.get("namespace") == "production"
    assert manifest.get("spec", {}).get("shareProcessNamespace") is True
    assert DEBUG_EPHEMERAL_CONTAINER.get("name") == "debugger"
    assert DEBUG_EPHEMERAL_CONTAINER.get("image") == "busybox:1.36"
    assert DEBUG_EPHEMERAL_CONTAINER.get("command") == ["sh"]
    assert DEBUG_EPHEMERAL_CONTAINER.get("targetContainerName") == "app"
    assert DEBUG_EPHEMERAL_CONTAINER.get("stdin") is True
    assert DEBUG_EPHEMERAL_CONTAINER.get("tty") is True
    sample_events = [
        {"type": "Normal", "reason": "Scheduled", "message": "Successfully assigned", "count": 1},
        {"type": "Warning", "reason": "Unhealthy", "message": "Liveness probe failed", "count": 2},
        {"type": "Warning", "reason": "FailedMount", "message": "Volume not ready", "count": 1},
        {
            "type": "Warning",
            "reason": "BackOff",
            "message": "Back-off restarting failed container",
            "count": 7,
        },
        {
            "type": "Warning",
            "reason": "FailedScheduling",
            "message": "0/3 nodes available",
            "count": 5,
        },
    ]
    triaged = triage_events(sample_events)
    assert len(triaged) == 3, f"Expected 3 triaged events, got {len(triaged)}"
    assert triaged[0]["reason"] == "BackOff" and triaged[0]["count"] == 7
    assert triaged[1]["reason"] == "FailedScheduling" and triaged[1]["count"] == 5
    assert triaged[2]["reason"] == "Unhealthy" and triaged[2]["count"] == 2

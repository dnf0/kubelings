"""
Validators for Chapter 10: Health Checking, Probes & Lifecycle
"""

from typing import Any, Dict, List

from kubelings.validator import validate_manifest
from kubelings.validators import register_validator


@register_validator("health01")
def validate_health01(manifest: Any, raw_yaml: str = "") -> None:
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(manifest, expected_kind="Pod", expected_api_version="v1")
    assert manifest["metadata"]["name"] == "web-liveness-pod"
    container = manifest["spec"]["containers"][0]
    assert container["name"] == "web"
    assert container["image"] == "nginx:1.25-alpine"
    probe = container.get("livenessProbe")
    assert isinstance(probe, dict), "livenessProbe must be defined"
    http_get = probe.get("httpGet")
    assert isinstance(http_get, dict), "livenessProbe.httpGet must be defined"
    assert http_get.get("path") == "/healthz", "httpGet path must be '/healthz'"
    assert http_get.get("port") == 8080, "httpGet port must be 8080"
    headers = http_get.get("httpHeaders", [])
    assert len(headers) == 1
    assert headers[0]["name"] == "X-Custom-Header"
    assert headers[0]["value"] == "Awesome"
    assert probe.get("initialDelaySeconds") == 15
    assert probe.get("periodSeconds") == 10
    assert probe.get("timeoutSeconds") == 2
    assert probe.get("failureThreshold") == 3


def simulate_service_endpoints(pods_state: List[Dict[str, Any]]) -> List[str]:
    """Filter the list of pod endpoints to only include IPs of pods with is_ready=True."""
    return [pod["ip"] for pod in pods_state if pod.get("is_ready") is True]


@register_validator("health02")
def validate_health02(manifest: Any, raw_yaml: str = "") -> None:
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(manifest, expected_kind="Pod", expected_api_version="v1")
    assert manifest["metadata"]["name"] == "db-service-pod"
    container = manifest["spec"]["containers"][0]
    assert container["name"] == "db-worker"
    assert container["image"] == "postgres:16-alpine"
    probe = container.get("readinessProbe")
    assert isinstance(probe, dict), "readinessProbe must be defined"
    exec_action = probe.get("exec")
    assert isinstance(exec_action, dict), "readinessProbe.exec must be defined"
    assert exec_action.get("command") == ["pg_isready", "-h", "127.0.0.1", "-p", "5432", "-q"]
    assert probe.get("initialDelaySeconds") == 5
    assert probe.get("periodSeconds") == 5
    assert probe.get("successThreshold") == 1
    assert probe.get("failureThreshold") == 2
    fleet = [
        {"ip": "10.244.1.10", "is_ready": True},
        {"ip": "10.244.1.11", "is_ready": False},
        {"ip": "10.244.2.15", "is_ready": True},
        {"ip": "10.244.3.20", "is_ready": False},
    ]
    active_endpoints = simulate_service_endpoints(fleet)
    assert active_endpoints == ["10.244.1.10", "10.244.2.15"], (
        f"Unexpected active endpoints: {active_endpoints}"
    )


def calculate_max_startup_budget(startup_probe: Dict[str, Any]) -> int:
    """Calculate the maximum startup budget duration in seconds before liveness checks kick in."""
    initial = startup_probe.get("initialDelaySeconds", 0)
    period = startup_probe.get("periodSeconds", 10)
    threshold = startup_probe.get("failureThreshold", 3)
    return initial + period * threshold


@register_validator("health03")
def validate_health03(manifest: Any, raw_yaml: str = "") -> None:
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(manifest, expected_kind="Pod", expected_api_version="v1")
    assert manifest["metadata"]["name"] == "legacy-app-pod"
    container = manifest["spec"]["containers"][0]
    assert container["name"] == "legacy-app"
    assert container["image"] == "openjdk:21-slim"
    startup = container.get("startupProbe")
    assert isinstance(startup, dict), "startupProbe must be defined"
    assert startup.get("tcpSocket", {}).get("port") == 8080
    assert startup.get("initialDelaySeconds") == 10
    assert startup.get("periodSeconds") == 10
    assert startup.get("failureThreshold") == 30
    liveness = container.get("livenessProbe")
    assert isinstance(liveness, dict), "livenessProbe must be defined"
    assert liveness.get("httpGet", {}).get("path") == "/alive"
    assert liveness.get("httpGet", {}).get("port") == 8080
    assert liveness.get("periodSeconds") == 10
    assert liveness.get("failureThreshold") == 3
    assert calculate_max_startup_budget(startup) == 310, (
        "Startup budget should be 10 + (10 * 30) = 310 seconds"
    )
    custom_probe = {"initialDelaySeconds": 5, "periodSeconds": 2, "failureThreshold": 10}
    assert calculate_max_startup_budget(custom_probe) == 25


@register_validator("health04")
def validate_health04(manifest: Any, raw_yaml: str = "") -> None:
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(manifest, expected_kind="Pod", expected_api_version="v1")
    assert manifest["metadata"]["name"] == "graceful-web-pod"
    assert manifest["spec"].get("terminationGracePeriodSeconds") == 60, (
        "terminationGracePeriodSeconds must be 60"
    )
    container = manifest["spec"]["containers"][0]
    assert container["name"] == "web-server"
    assert container["image"] == "nginx:alpine"
    lifecycle = container.get("lifecycle")
    assert isinstance(lifecycle, dict), "lifecycle must be defined"
    post_start = lifecycle.get("postStart", {})
    assert post_start.get("exec", {}).get("command") == [
        "/bin/sh",
        "-c",
        "echo Ready > /var/log/started.log",
    ]
    pre_stop = lifecycle.get("preStop", {})
    assert pre_stop.get("httpGet", {}).get("path") == "/prepare-shutdown"
    assert pre_stop.get("httpGet", {}).get("port") == 80

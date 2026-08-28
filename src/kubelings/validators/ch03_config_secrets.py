"""
Validators for Chapter 03: Configuration & Secret Management
"""

import base64
import copy
from typing import Any, Dict

from kubelings.validator import validate_manifest, validate_manifests
from kubelings.validators import register_validator

CONFIG_MANIFESTS = '\napiVersion: v1\nkind: ConfigMap\nmetadata:\n  name: app-config\ndata:\n  APP_ENV: production\n  DATABASE_HOST: postgres.internal\n  PORT: "8080"\n---\napiVersion: v1\nkind: Pod\nmetadata:\n  name: app-pod\nspec:\n  containers:\n  - name: backend\n    image: python:3.12-alpine\n    envFrom:\n    - configMapRef:\n        name: app-config\n    env:\n    - name: CUSTOM_PORT\n      valueFrom:\n        configMapKeyRef:\n          name: app-config\n          key: PORT\n'


@register_validator("config01")
def validate_config01(manifest: Any, raw_yaml: str = "") -> None:
    manifests = manifest if isinstance(manifest, list) else [manifest]
    assert len(manifests) == 2, "Must contain exactly 2 manifests (ConfigMap and Pod)"
    validate_manifests(manifests, expected_kinds=["ConfigMap", "Pod"])
    cm, pod = (manifests[0], manifests[1])
    assert cm["metadata"]["name"] == "app-config"
    assert cm["data"]["APP_ENV"] == "production"
    assert cm["data"]["DATABASE_HOST"] == "postgres.internal"
    assert cm["data"]["PORT"] == "8080"
    c = pod["spec"]["containers"][0]
    env_from = c.get("envFrom", [])
    assert len(env_from) >= 1, "Must define envFrom"
    assert env_from[0].get("configMapRef", {}).get("name") == "app-config", (
        "envFrom must reference app-config"
    )
    env_list = c.get("env", [])
    custom_port_entry = next((e for e in env_list if e.get("name") == "CUSTOM_PORT"), None)
    assert custom_port_entry is not None, "Must define CUSTOM_PORT in container env"
    cm_key_ref = custom_port_entry.get("valueFrom", {}).get("configMapKeyRef", {})
    assert cm_key_ref.get("name") == "app-config", "configMapKeyRef name must be 'app-config'"
    assert cm_key_ref.get("key") == "PORT", "configMapKeyRef key must be 'PORT'"


CONFIG_VOLUME_MANIFESTS = '\napiVersion: v1\nkind: ConfigMap\nmetadata:\n  name: nginx-config\ndata:\n  default.conf: "server { listen 80; server_name localhost; }"\n---\napiVersion: v1\nkind: Pod\nmetadata:\n  name: nginx-configured\nspec:\n  volumes:\n  - name: config-vol\n    configMap:\n      name: nginx-config\n  containers:\n  - name: nginx-server\n    image: nginx:alpine\n    volumeMounts:\n    - name: config-vol\n      mountPath: /etc/nginx/conf.d/default.conf\n      subPath: default.conf\n'


@register_validator("config02")
def validate_config02(manifest: Any, raw_yaml: str = "") -> None:
    manifests = manifest if isinstance(manifest, list) else [manifest]
    assert len(manifests) == 2, "Must contain exactly 2 manifests (ConfigMap and Pod)"
    validate_manifests(manifests, expected_kinds=["ConfigMap", "Pod"])
    cm, pod = (manifests[0], manifests[1])
    assert cm["metadata"]["name"] == "nginx-config"
    assert "listen 80" in cm["data"]["default.conf"]
    volumes = pod["spec"].get("volumes", [])
    assert len(volumes) >= 1, "Must define at least one volume in Pod spec"
    assert volumes[0]["name"] == "config-vol"
    assert volumes[0]["configMap"]["name"] == "nginx-config"
    c = pod["spec"]["containers"][0]
    mounts = c.get("volumeMounts", [])
    assert len(mounts) >= 1, "Must define volumeMounts in container"
    assert mounts[0]["name"] == "config-vol"
    assert mounts[0]["mountPath"] == "/etc/nginx/conf.d/default.conf"
    assert mounts[0].get("subPath") == "default.conf", (
        "volumeMount must specify subPath: 'default.conf'"
    )


def decode_secret_data(secret_dict: Dict[str, Any]) -> Dict[str, str]:
    """Decode base64 encoded strings in secret['data'] to utf-8 strings."""
    data = secret_dict.get("data", {})
    decoded: Dict[str, str] = {}
    for k, v in data.items():
        if isinstance(v, str):
            decoded[k] = base64.b64decode(v.encode("utf-8")).decode("utf-8")
    return decoded


@register_validator("config03")
def validate_config03(manifest: Any, raw_yaml: str = "") -> None:
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(manifest, expected_kind="Secret", expected_api_version="v1")
    assert manifest["metadata"]["name"] == "db-credentials"
    assert manifest.get("type") == "Opaque", "Secret type must be 'Opaque'"
    assert manifest.get("stringData", {}).get("api_key") == "prod-api-key-998877"
    decoded = decode_secret_data(manifest)
    assert decoded.get("username") == "admin", (
        f"Decoded username must be 'admin', got {decoded.get('username')}"
    )
    assert decoded.get("password") == "supersecret", (
        f"Decoded password must be 'supersecret', got {decoded.get('password')}"
    )


@register_validator("config04")
def validate_config04(manifest: Any, raw_yaml: str = "") -> None:
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(manifest, expected_kind="Pod", expected_api_version="v1")
    assert manifest["metadata"]["name"] == "secure-cert-pod"
    vol = manifest["spec"]["volumes"][0]
    assert vol["name"] == "tls-certs"
    assert vol["secret"]["secretName"] == "tls-secret"
    default_mode = vol["secret"].get("defaultMode")
    assert default_mode in (256, 256), f"defaultMode must be 256 (0400 octal), got {default_mode}"
    mount = manifest["spec"]["containers"][0]["volumeMounts"][0]
    assert mount["name"] == "tls-certs"
    assert mount["mountPath"] == "/etc/tls"
    assert mount.get("readOnly") is True, "VolumeMount must specify readOnly: true"


def check_immutability_guard(existing: Dict[str, Any], updated: Dict[str, Any]) -> bool:
    """Verify that updates to an immutable resource do not alter data contents."""
    if existing.get("immutable") is True:
        for field in ("data", "stringData", "binaryData"):
            if existing.get(field) != updated.get(field):
                raise ValueError(f"Cannot update {field} of an immutable resource")
    return True


@register_validator("config05")
def validate_config05(manifest: Any, raw_yaml: str = "") -> None:
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(manifest, expected_kind="ConfigMap", expected_api_version="v1")
    assert manifest["metadata"]["name"] == "app-feature-flags"
    assert manifest.get("immutable") is True, "ConfigMap must have 'immutable: true'"
    assert manifest["data"]["NEW_UI"] == "true"
    assert manifest["data"]["MAX_WORKERS"] == "8"
    assert check_immutability_guard(manifest, manifest) is True
    mutated = copy.deepcopy(manifest)
    mutated["data"]["MAX_WORKERS"] = "16"
    try:
        check_immutability_guard(manifest, mutated)
        raise AssertionError("Expected ValueError when mutating immutable ConfigMap data")
    except ValueError as e:
        assert "immutable" in str(e).lower()

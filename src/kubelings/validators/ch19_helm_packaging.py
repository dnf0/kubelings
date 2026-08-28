"""
Validators for Chapter 19: Package Management with Helm
"""

from typing import Any, Dict

import jsonschema
import yaml

from kubelings.validators import register_validator


def get_chart_metadata() -> Dict[str, Any]:
    manifest_yaml = "\napiVersion: v2\nname: webapp-chart\nversion: 1.2.0\nappVersion: 2.4.1\ndescription: A robust web application Helm chart with subchart dependencies\ndependencies:\n  - name: redis\n    version: 17.3.0\n    repository: https://charts.bitnami.com/bitnami\n    condition: redis.enabled\n"
    return yaml.safe_load(manifest_yaml)


@register_validator("helm01")
def validate_helm01(manifest: Any, raw_yaml: str = "") -> None:
    meta = manifest
    assert meta.get("apiVersion") == "v2", "apiVersion must be 'v2' for Helm 3"
    assert meta.get("name") == "webapp-chart"
    assert meta.get("version") == "1.2.0"
    assert meta.get("appVersion") == "2.4.1"
    deps = meta.get("dependencies", [])
    assert len(deps) == 1, "Must define 1 subchart dependency"
    assert deps[0].get("name") == "redis"
    assert deps[0].get("version") == "17.3.0"
    assert deps[0].get("condition") == "redis.enabled"


def chart_fullname(chart_name: str, release_name: str, fullname_override: str = "") -> str:
    if fullname_override:
        return fullname_override[:63].rstrip("-")
    if chart_name in release_name:
        return release_name[:63].rstrip("-")
    name = f"{release_name}-{chart_name}"
    return name[:63].rstrip("-")


def render_deployment(values: Dict[str, Any]) -> Dict[str, Any]:
    chart_name = values.get("Chart", {}).get("Name", "mychart")
    release_name = values.get("Release", {}).get("Name", "prod-release")
    name_override = values.get("fullnameOverride", "")
    full_name = chart_fullname(chart_name, release_name, name_override)
    replicas = values.get("replicaCount", 1)
    img_repo = values.get("image", {}).get("repository", "nginx")
    img_tag = values.get("image", {}).get("tag", "stable")
    return {
        "apiVersion": "apps/v1",
        "kind": "Deployment",
        "metadata": {
            "name": full_name,
            "labels": {
                "app.kubernetes.io/name": chart_name,
                "app.kubernetes.io/instance": release_name,
            },
        },
        "spec": {
            "replicas": replicas,
            "selector": {
                "matchLabels": {
                    "app.kubernetes.io/name": chart_name,
                    "app.kubernetes.io/instance": release_name,
                }
            },
            "template": {
                "metadata": {
                    "labels": {
                        "app.kubernetes.io/name": chart_name,
                        "app.kubernetes.io/instance": release_name,
                    }
                },
                "spec": {
                    "containers": [
                        {
                            "name": chart_name,
                            "image": f"{img_repo}:{img_tag}",
                            "ports": [{"containerPort": values.get("service", {}).get("port", 80)}],
                        }
                    ]
                },
            },
        },
    }


@register_validator("helm02")
def validate_helm02(manifest: Any, raw_yaml: str = "") -> None:
    assert chart_fullname("mychart", "prod-release") == "prod-release-mychart"
    assert chart_fullname("mychart", "prod-release", "custom-name") == "custom-name"
    assert chart_fullname("mychart", "mychart-prod") == "mychart-prod"
    dep = manifest
    assert dep.get("apiVersion") == "apps/v1"
    assert dep.get("kind") == "Deployment"
    assert dep.get("metadata", {}).get("name") == "prod-web"
    assert dep.get("spec", {}).get("replicas") == 3
    containers = dep.get("spec", {}).get("template", {}).get("spec", {}).get("containers", [])
    assert len(containers) == 1
    assert containers[0].get("image") == "nginx:1.25-alpine"
    assert containers[0].get("ports", [{}])[0].get("containerPort") == 8080


def get_values_schema() -> Dict[str, Any]:
    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "required": ["replicaCount", "image", "service"],
        "properties": {
            "replicaCount": {"type": "integer", "minimum": 1, "maximum": 100},
            "image": {
                "type": "object",
                "required": ["repository", "tag"],
                "properties": {"repository": {"type": "string"}, "tag": {"type": "string"}},
            },
            "service": {
                "type": "object",
                "required": ["type", "port"],
                "properties": {
                    "type": {"type": "string", "enum": ["ClusterIP", "NodePort", "LoadBalancer"]},
                    "port": {"type": "integer", "minimum": 1, "maximum": 65535},
                },
            },
        },
    }


@register_validator("helm03")
def validate_helm03(manifest: Any, raw_yaml: str = "") -> None:
    schema = manifest
    assert schema.get("$schema") == "http://json-schema.org/draft-07/schema#"
    assert set(schema.get("required", [])) == {"replicaCount", "image", "service"}
    valid_payload = {
        "replicaCount": 3,
        "image": {"repository": "nginx", "tag": "1.25"},
        "service": {"type": "ClusterIP", "port": 80},
    }
    jsonschema.validate(instance=valid_payload, schema=schema)
    invalid_payload = {
        "replicaCount": 0,
        "image": {"repository": "nginx", "tag": "1.25"},
        "service": {"type": "ClusterIP", "port": 80},
    }
    try:
        jsonschema.validate(instance=invalid_payload, schema=schema)
        raise AssertionError("Expected ValidationError on invalid replicaCount")
    except jsonschema.ValidationError:
        pass


def get_parent_values() -> Dict[str, Any]:
    manifest_yaml = "\nglobal:\n  environment: production\n  registry: registry.k8s.io\n\nredis:\n  architecture: replication\n  auth:\n    enabled: true\n    secretName: redis-credentials\n\npostgresql:\n  enabled: false\n  primary:\n    persistence:\n      size: 20Gi\n"
    return yaml.safe_load(manifest_yaml)


@register_validator("helm04")
def validate_helm04(manifest: Any, raw_yaml: str = "") -> None:
    values = manifest
    assert values.get("global", {}).get("environment") == "production"
    assert values.get("global", {}).get("registry") == "registry.k8s.io"
    assert values.get("redis", {}).get("architecture") == "replication"
    assert values.get("redis", {}).get("auth", {}).get("enabled") is True
    assert values.get("redis", {}).get("auth", {}).get("secretName") == "redis-credentials"
    assert values.get("postgresql", {}).get("enabled") is False
    assert (
        values.get("postgresql", {}).get("primary", {}).get("persistence", {}).get("size") == "20Gi"
    )

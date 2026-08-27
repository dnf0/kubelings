# I AM NOT DONE
"""
Chapter 19: Package Management with Helm
Exercise 19.2: Helm Go Templating & Named Helpers (_helpers.tpl)

Task: Implement the standard Helm fullname helper logic and render a Kubernetes Deployment.
Requirements:
- Function `chart_fullname(chart_name: str, release_name: str, fullname_override: str = "") -> str`:
    - If fullname_override is provided, return fullname_override truncated to 63 chars.
    - If release_name contains chart_name, return release_name truncated to 63 chars.
    - Otherwise return f"{release_name}-{chart_name}" truncated to 63 chars (trimmed of trailing hyphens).
- Function `render_deployment(values: dict) -> dict`:
    - Generates a Deployment manifest using chart_fullname as metadata.name and selector/template app labels.
    - apiVersion: 'apps/v1', kind: 'Deployment'
    - replicas: values.get('replicaCount', 1)
    - container image: f"{values['image']['repository']}:{values['image']['tag']}"
"""

from typing import Any, Dict


def chart_fullname(chart_name: str, release_name: str, fullname_override: str = "") -> str:
    return ""


def render_deployment(values: Dict[str, Any]) -> Dict[str, Any]:
    return {}


if __name__ == "__main__":
    assert chart_fullname("mychart", "prod-release") == "prod-release-mychart"
    assert chart_fullname("mychart", "prod-release", "custom-name") == "custom-name"
    assert chart_fullname("mychart", "mychart-prod") == "mychart-prod"

    values = {
        "Chart": {"Name": "web"},
        "Release": {"Name": "prod"},
        "replicaCount": 3,
        "image": {"repository": "nginx", "tag": "1.25-alpine"},
        "service": {"port": 8080},
    }
    dep = render_deployment(values)
    assert dep.get("apiVersion") == "apps/v1"
    assert dep.get("kind") == "Deployment"
    assert dep.get("metadata", {}).get("name") == "prod-web"
    assert dep.get("spec", {}).get("replicas") == 3
    containers = dep.get("spec", {}).get("template", {}).get("spec", {}).get("containers", [])
    assert len(containers) == 1
    assert containers[0].get("image") == "nginx:1.25-alpine"
    assert containers[0].get("ports", [{}])[0].get("containerPort") == 8080
    print("✓ Helm Go templating helper validation passed!")

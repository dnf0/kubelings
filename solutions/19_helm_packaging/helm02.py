"""
Chapter 19: Package Management with Helm
Exercise 19.2: Helm Go Templating & Named Helpers (_helpers.tpl) (Solution)
"""

from typing import Any, Dict


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

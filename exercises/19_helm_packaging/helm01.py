"""
Chapter 19: Package Management with Helm
Exercise 19.1: Helm Chart.yaml Metadata & Dependencies

Context & Why:
Helm is the de-facto package manager for Kubernetes, packaging collections of YAML templates
and configuration values into distributable, versioned charts. In Helm v3, the `Chart.yaml`
file uses `apiVersion: v2` to define chart metadata and dependency relationships.

A well-structured `Chart.yaml` strictly separates the packaging version (`version`, following
Semantic Versioning 2.0) from the deployed application workload version (`appVersion`).
Declaring dependencies (such as Redis from a public Helm repository) alongside conditional flags
(`condition: redis.enabled`) enables chart consumers to selectively enable or disable supporting
infrastructure subcharts directly through their values file.

Task: Construct a valid Helm v3 Chart.yaml metadata specification for 'webapp-chart'.
Requirements:
- apiVersion: 'v2' (Helm 3 standard)
- name: 'webapp-chart'
- version: '1.2.0' (SemVer 2.0.0 chart version)
- appVersion: '2.4.1' (Version of the underlying application)
- description: 'A robust web application Helm chart with subchart dependencies'
- dependencies: list containing a subchart dependency:
    - name: 'redis'
    - version: '17.3.0'
    - repository: 'https://charts.bitnami.com/bitnami'
    - condition: 'redis.enabled'
"""

from typing import Any, Dict

import yaml


def get_chart_metadata() -> Dict[str, Any]:
    manifest_yaml = """
apiVersion: v1
name: ""
version: ""
"""
    # TODO: Update manifest_yaml with the specified Chart.yaml metadata & dependencies and return the parsed dictionary (e.g., via yaml.safe_load).
    # WHY: Chart.yaml establishes the chart's SemVer package identity and dependency tree, allowing Helm to resolve
    #      and package subchart dependencies reliably.
    return {}


if __name__ == "__main__":
    meta = get_chart_metadata()
    assert meta.get("apiVersion") == "v2", "apiVersion must be 'v2' for Helm 3"
    assert meta.get("name") == "webapp-chart"
    assert meta.get("version") == "1.2.0"
    assert meta.get("appVersion") == "2.4.1"
    deps = meta.get("dependencies", [])
    assert len(deps) == 1, "Must define 1 subchart dependency"
    assert deps[0].get("name") == "redis"
    assert deps[0].get("version") == "17.3.0"
    assert deps[0].get("condition") == "redis.enabled"
    print("✓ Helm Chart.yaml metadata validation passed!")

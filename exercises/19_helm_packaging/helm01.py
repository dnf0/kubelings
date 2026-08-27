# I AM NOT DONE
"""
Chapter 19: Package Management with Helm
Exercise 19.1: Helm Chart.yaml Metadata & Dependencies

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

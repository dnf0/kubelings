"""
Chapter 19: Package Management with Helm
Exercise 19.4: Helm Subcharts & Global Values

Task: Construct a parent chart values.yaml structure configuring subchart overrides and global values.
Requirements:
- Structure must contain:
    - global: dictionary with keys:
        - environment: 'production'
        - registry: 'registry.k8s.io'
    - redis (subchart override): dictionary with keys:
        - architecture: 'replication'
        - auth: {'enabled': True, 'secretName': 'redis-credentials'}
    - postgresql (subchart override): dictionary with keys:
        - enabled: False
        - primary: {'persistence': {'size': '20Gi'}}
"""

from typing import Any, Dict

import yaml


def get_parent_values() -> Dict[str, Any]:
    manifest_yaml = """
global: {}
"""
    return {}


if __name__ == "__main__":
    values = get_parent_values()
    assert values.get("global", {}).get("environment") == "production"
    assert values.get("global", {}).get("registry") == "registry.k8s.io"
    assert values.get("redis", {}).get("architecture") == "replication"
    assert values.get("redis", {}).get("auth", {}).get("enabled") is True
    assert values.get("redis", {}).get("auth", {}).get("secretName") == "redis-credentials"
    assert values.get("postgresql", {}).get("enabled") is False
    assert (
        values.get("postgresql", {}).get("primary", {}).get("persistence", {}).get("size") == "20Gi"
    )
    print("✓ Helm subcharts and global values validation passed!")

"""
Chapter 19: Package Management with Helm
Exercise 19.4: Helm Subcharts & Global Values

Context & Why:
Large cloud-native platforms often build "umbrella charts" that orchestrate multiple
dependent microservices and datastores (e.g., Redis, PostgreSQL, ingress controllers)
under a unified deployment lifecycle. Managing configuration across nested subcharts
requires understanding Helm's hierarchical value resolution model.

In Helm, subchart values are namespaced under the subchart name (e.g. `redis.architecture`
overrides the default settings of the child Redis chart). Furthermore, values placed under
the special top-level `global` dictionary are automatically accessible by every template across
both the parent chart and all child subcharts. This eliminates repetitive parameter definitions
for shared cluster-wide settings like container registries, domain names, or target environments.

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
    # TODO: Update manifest_yaml with the global and subchart override configurations, returning the parsed dictionary (e.g., via yaml.safe_load).
    # WHY: Umbrella chart values.yaml files manage complex microservice stacks by overriding subchart parameters
    #      and broadcasting global settings (registry, environment) uniformly across all child charts.
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

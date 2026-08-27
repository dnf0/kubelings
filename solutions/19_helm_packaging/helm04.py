"""
Chapter 19: Package Management with Helm
Exercise 19.4: Helm Subcharts & Global Values (Solution)
"""

from typing import Any, Dict

import yaml


def get_parent_values() -> Dict[str, Any]:
    manifest_yaml = """
global:
  environment: production
  registry: registry.k8s.io

redis:
  architecture: replication
  auth:
    enabled: true
    secretName: redis-credentials

postgresql:
  enabled: false
  primary:
    persistence:
      size: 20Gi
"""
    return yaml.safe_load(manifest_yaml)


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

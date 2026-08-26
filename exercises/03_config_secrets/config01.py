"""
Exercise: exercises/03_config_secrets/config01.py
Topic: ConfigMaps as Environment Variables

Instructions:
ConfigMaps decouple configuration artifacts from container image content.
In the multi-document manifest below:
1. Complete the ConfigMap 'app-config' with data keys:
   APP_ENV: "production", DATABASE_HOST: "postgres.internal", PORT: "8080".
2. In the Pod 'app-pod':
   - Inject all ConfigMap keys using `envFrom` with `configMapRef: {name: "app-config"}`.
   - Inject the specific PORT key as CUSTOM_PORT using `valueFrom.configMapKeyRef`.
"""

# I AM NOT DONE

import yaml

from kubelings.validator import validate_manifests

CONFIG_MANIFESTS = """
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  APP_ENV: ???
  DATABASE_HOST: ???
  PORT: ???
---
apiVersion: v1
kind: Pod
metadata:
  name: app-pod
spec:
  containers:
  - name: backend
    image: python:3.12-alpine
    # TODO: add envFrom and env referencing app-config
"""


def verify():
    manifests = list(yaml.safe_load_all(CONFIG_MANIFESTS))
    assert len(manifests) == 2, "Must contain exactly 2 manifests (ConfigMap and Pod)"
    validate_manifests(manifests, expected_kinds=["ConfigMap", "Pod"])

    cm, pod = manifests[0], manifests[1]

    # ConfigMap validation
    assert cm["metadata"]["name"] == "app-config"
    assert cm["data"]["APP_ENV"] == "production"
    assert cm["data"]["DATABASE_HOST"] == "postgres.internal"
    assert cm["data"]["PORT"] == "8080"

    # Pod envFrom validation
    c = pod["spec"]["containers"][0]
    env_from = c.get("envFrom", [])
    assert len(env_from) >= 1, "Must define envFrom"
    assert env_from[0].get("configMapRef", {}).get("name") == "app-config", (
        "envFrom must reference app-config"
    )

    # Pod env valueFrom validation
    env_list = c.get("env", [])
    custom_port_entry = next((e for e in env_list if e.get("name") == "CUSTOM_PORT"), None)
    assert custom_port_entry is not None, "Must define CUSTOM_PORT in container env"
    cm_key_ref = custom_port_entry.get("valueFrom", {}).get("configMapKeyRef", {})
    assert cm_key_ref.get("name") == "app-config", "configMapKeyRef name must be 'app-config'"
    assert cm_key_ref.get("key") == "PORT", "configMapKeyRef key must be 'PORT'"

    print("✓ config01 passed!")


if __name__ == "__main__":
    verify()

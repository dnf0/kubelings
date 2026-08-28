"""
Exercise: exercises/03_config_secrets/config01.py
Topic: ConfigMaps as Environment Variables

Context & Why:
The Twelve-Factor App methodology advocates strict separation of configuration from code.
Kubernetes ConfigMaps store non-confidential key-value pairs that can be injected into Pods
at runtime. There are two primary injection patterns:
1. `envFrom`: Ingests all key-value pairs from a ConfigMap as individual container environment
   variables, matching the ConfigMap key names directly.
2. `env[].valueFrom.configMapKeyRef`: Selectively pulls a single key from a ConfigMap and binds
   it to a specific, custom-named environment variable inside the container.
Using ConfigMaps ensures application container images remain portable and identical across dev,
staging, and production environments.

Instructions:
ConfigMaps decouple configuration artifacts from container image content.
In the multi-document manifest below:
1. Complete the ConfigMap 'app-config' with data keys:
   APP_ENV: "production", DATABASE_HOST: "postgres.internal", PORT: "8080".
2. In the Pod 'app-pod':
   - Inject all ConfigMap keys using `envFrom` with `configMapRef: {name: "app-config"}`.
   - Inject the specific PORT key as CUSTOM_PORT using `valueFrom.configMapKeyRef`.
"""

import yaml

from kubelings.validator import validate_manifests

CONFIG_MANIFESTS = """
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  # TODO: Define keys APP_ENV: "production", DATABASE_HOST: "postgres.internal", and PORT: "8080"
  # WHY: Centralizes environment configuration parameters into a declarative, decoupled Kubernetes object.
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
    # TODO: Add envFrom referencing 'app-config' and env injecting 'PORT' as CUSTOM_PORT via valueFrom.configMapKeyRef
    # WHY: envFrom provides bulk injection of environment variables, while configMapKeyRef allows selective key mapping to custom variable names.
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

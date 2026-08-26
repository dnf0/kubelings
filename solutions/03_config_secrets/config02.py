"""
Exercise: solutions/03_config_secrets/config02.py
Topic: ConfigMaps Mounted as Volumes & subPath

Reference Solution
"""

import yaml
from kubelings.validator import validate_manifests

CONFIG_VOLUME_MANIFESTS = """
apiVersion: v1
kind: ConfigMap
metadata:
  name: nginx-config
data:
  default.conf: "server { listen 80; server_name localhost; }"
---
apiVersion: v1
kind: Pod
metadata:
  name: nginx-configured
spec:
  volumes:
  - name: config-vol
    configMap:
      name: nginx-config
  containers:
  - name: nginx-server
    image: nginx:alpine
    volumeMounts:
    - name: config-vol
      mountPath: /etc/nginx/conf.d/default.conf
      subPath: default.conf
"""


def verify():
    manifests = list(yaml.safe_load_all(CONFIG_VOLUME_MANIFESTS))
    assert len(manifests) == 2, "Must contain exactly 2 manifests (ConfigMap and Pod)"
    validate_manifests(manifests, expected_kinds=["ConfigMap", "Pod"])

    cm, pod = manifests[0], manifests[1]

    # Check ConfigMap
    assert cm["metadata"]["name"] == "nginx-config"
    assert "listen 80" in cm["data"]["default.conf"]

    # Check Pod volumes
    volumes = pod["spec"].get("volumes", [])
    assert len(volumes) >= 1, "Must define at least one volume in Pod spec"
    assert volumes[0]["name"] == "config-vol"
    assert volumes[0]["configMap"]["name"] == "nginx-config"

    # Check container volumeMounts
    c = pod["spec"]["containers"][0]
    mounts = c.get("volumeMounts", [])
    assert len(mounts) >= 1, "Must define volumeMounts in container"
    assert mounts[0]["name"] == "config-vol"
    assert mounts[0]["mountPath"] == "/etc/nginx/conf.d/default.conf"
    assert mounts[0].get("subPath") == "default.conf", (
        "volumeMount must specify subPath: 'default.conf'"
    )

    print("✓ config02 passed!")


if __name__ == "__main__":
    verify()

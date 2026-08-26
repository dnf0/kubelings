"""
Exercise: solutions/13_troubleshooting/troubleshoot02.py
Topic: Debugging ImagePullBackOff

Reference Solution
"""

import yaml

from kubelings.validator import validate_manifests

MANIFESTS = """
apiVersion: v1
kind: Secret
metadata:
  name: regcred
  namespace: finance
type: kubernetes.io/dockerconfigjson
stringData:
  .dockerconfigjson: '{"auths":{"privateregistry.io":{"username":"finance-bot","password":"secrettoken"}}}'
---
apiVersion: v1
kind: Pod
metadata:
  name: payment-service
  namespace: finance
spec:
  imagePullSecrets:
  - name: regcred
  containers:
  - name: app
    image: privateregistry.io/payment-app:v1.0.0
"""


def verify():
    manifests = list(yaml.safe_load_all(MANIFESTS))
    assert len(manifests) == 2, "Must contain exactly 2 manifests (Secret and Pod)"
    validate_manifests(manifests, expected_kinds=["Secret", "Pod"])

    secret, pod = manifests[0], manifests[1]

    # Verify Secret
    assert secret["metadata"]["name"] == "regcred"
    assert secret["metadata"]["namespace"] == "finance"
    assert secret.get("type") == "kubernetes.io/dockerconfigjson"

    # Verify Pod
    assert pod["metadata"]["name"] == "payment-service"
    assert pod["metadata"]["namespace"] == "finance"

    image_pull_secrets = pod["spec"].get("imagePullSecrets", [])
    assert len(image_pull_secrets) == 1
    assert image_pull_secrets[0].get("name") == "regcred"

    container = pod["spec"]["containers"][0]
    assert container["name"] == "app"
    assert container["image"] == "privateregistry.io/payment-app:v1.0.0"

    print("✓ troubleshoot02 passed!")


if __name__ == "__main__":
    verify()

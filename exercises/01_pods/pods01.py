"""
Exercise: exercises/01_pods/pods01.py
Topic: First Pod Manifest & Spec

Context & Why:
The Pod is the fundamental atomic unit of deployment in Kubernetes. It encapsulates
one or more containers that share an execution context: a single network namespace
(sharing an IP address and port space), shared IPC, and mounted storage volumes.
In production, bare Pods are rarely deployed on their own—higher-level controllers like
Deployments or StatefulSets manage their lifecycle. However, every workload controller
ultimately stamps out Pod specifications (`PodTemplateSpec`). Mastering the core Pod
schema—`apiVersion`, `kind`, `metadata` (names, labels), and `spec.containers`—is
essential for understanding all Kubernetes infrastructure.

Instructions:
Fix the YAML manifest below to define a valid Pod named 'nginx-web'
running nginx:alpine on container port 80 with label 'app: web'.
"""

import yaml

from kubelings.validator import validate_manifest

POD_MANIFEST = """
apiVersion: v1
kind: Pod
metadata:
  # TODO: Set the Pod name to 'nginx-web'
  # WHY: Pod names must be DNS-1123 compliant and uniquely identify the pod resource within its namespace.
  name: ???
  labels:
    # TODO: Add the label 'app: web'
    # WHY: Labels provide key-value indexing used by Services, Deployments, and NetworkPolicies to group and select Pods.
    app: ???
spec:
  containers:
  - name: nginx
    # TODO: Set the container image to 'nginx:alpine'
    # WHY: Alpine-based container images provide a minimal footprint, reducing image download latency and attack surface.
    image: ???
    ports:
    # TODO: Set containerPort to 80
    # WHY: Declaring containerPort documents the listening network port and aids tooling and service discovery.
    - containerPort: 0
"""


def verify():
    manifest = yaml.safe_load(POD_MANIFEST)
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(manifest, expected_kind="Pod", expected_api_version="v1")

    assert manifest["metadata"]["name"] == "nginx-web", "Pod name must be 'nginx-web'"
    assert manifest["metadata"]["labels"]["app"] == "web", "Label 'app' must equal 'web'"
    container = manifest["spec"]["containers"][0]
    assert container["name"] == "nginx", "Container name must be 'nginx'"
    assert container["image"] == "nginx:alpine", "Container image must be 'nginx:alpine'"
    assert container["ports"][0]["containerPort"] == 80, "Container port must be 80"
    print("✓ pods01 passed!")


if __name__ == "__main__":
    verify()

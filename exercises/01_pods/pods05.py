"""
Exercise: exercises/01_pods/pods05.py
Topic: Downward API & Environment Variables

Context & Why:
The Downward API allows containers to consume information about their own identity,
placement, and cluster environment without directly coupling to the Kubernetes client
libraries or requiring RBAC permissions to query the API server. By referencing
`fieldRef.fieldPath`, a container can dynamically receive its own Pod name, namespace,
assigned Pod IP, or the node name where it is currently executing. This is widely used
in production to parameterize logging frameworks, distributed tracing agents, service
mesh sidecars, and cluster-aware consensus applications.

Instructions:
The Kubernetes Downward API allows containers to consume information about themselves
or the cluster without coupling to the Kubernetes client or apiserver.

Complete the Pod manifest below to inject the following container environment variables:
1. MY_POD_NAME: from fieldPath 'metadata.name'
2. MY_POD_NAMESPACE: from fieldPath 'metadata.namespace'
3. MY_POD_IP: from fieldPath 'status.podIP'
4. MY_NODE_NAME: from fieldPath 'spec.nodeName'
"""

import yaml

from kubelings.validator import validate_manifest

POD_MANIFEST = """
apiVersion: v1
kind: Pod
metadata:
  name: downward-api-pod
spec:
  containers:
  - name: client-app
    image: alpine:3.19
    env:
    # TODO: Inject MY_POD_NAME referencing fieldPath 'metadata.name'
    # WHY: Allows the container process to self-identify its pod name for distributed tracing and structured logging.
    - name: MY_POD_NAME
      valueFrom:
        fieldRef:
          fieldPath: ???
    # TODO: Inject MY_POD_NAMESPACE referencing fieldPath 'metadata.namespace'
    # WHY: Enables multi-tenant workloads to know their deployment namespace boundary dynamically.
    - name: MY_POD_NAMESPACE
      valueFrom:
        fieldRef:
          fieldPath: ???
    # TODO: Inject MY_POD_IP referencing fieldPath 'status.podIP'
    # WHY: Exposes the dynamically assigned pod network IP address to application processes for peer discovery.
    - name: MY_POD_IP
      valueFrom:
        fieldRef:
          fieldPath: ???
    # TODO: Inject MY_NODE_NAME referencing fieldPath 'spec.nodeName'
    # WHY: Informs the application container of the physical/virtual host node executing the workload for node-affinity telemetry.
    - name: MY_NODE_NAME
      valueFrom:
        fieldRef:
          fieldPath: ???
"""


def verify():
    manifest = yaml.safe_load(POD_MANIFEST)
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(manifest, expected_kind="Pod", expected_api_version="v1")

    assert manifest["metadata"]["name"] == "downward-api-pod"
    env_vars = manifest["spec"]["containers"][0].get("env", [])
    assert len(env_vars) == 4, "Must define all 4 Downward API environment variables"

    env_map = {item["name"]: item["valueFrom"]["fieldRef"]["fieldPath"] for item in env_vars}
    assert env_map.get("MY_POD_NAME") == "metadata.name", "MY_POD_NAME must reference metadata.name"
    assert env_map.get("MY_POD_NAMESPACE") == "metadata.namespace", (
        "MY_POD_NAMESPACE must reference metadata.namespace"
    )
    assert env_map.get("MY_POD_IP") == "status.podIP", "MY_POD_IP must reference status.podIP"
    assert env_map.get("MY_NODE_NAME") == "spec.nodeName", (
        "MY_NODE_NAME must reference spec.nodeName"
    )

    print("✓ pods05 passed!")


if __name__ == "__main__":
    verify()

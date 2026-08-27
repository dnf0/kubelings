"""
Solution: solutions/24_kuberay_ml/ray01.py
Topic: RayCluster Core Architecture & Head Node
"""

import yaml

from kubelings.validator import validate_manifest_text

RAY_CLUSTER_MANIFEST = """
apiVersion: ray.io/v1
kind: RayCluster
metadata:
  name: ray-cluster-ml
spec:
  rayVersion: '2.35.0'
  headGroupSpec:
    rayStartParams:
      dashboard-host: '0.0.0.0'
      block: 'true'
    template:
      spec:
        containers:
          - name: ray-head
            image: rayproject/ray:2.35.0
            ports:
              - containerPort: 6379
                name: gcs
              - containerPort: 8265
                name: dashboard
  workerGroupSpecs:
    - groupName: worker-group
      replicas: 2
      minReplicas: 1
      maxReplicas: 5
      template:
        spec:
          containers:
            - name: ray-worker
              image: rayproject/ray:2.35.0
              resources:
                limits:
                  cpu: "2"
                  memory: 4Gi
"""


def verify():
    passed, errors = validate_manifest_text(RAY_CLUSTER_MANIFEST, "ray01")
    assert passed, f"RayCluster manifest validation failed: {errors}"

    manifest = yaml.safe_load(RAY_CLUSTER_MANIFEST)
    assert manifest["metadata"]["name"] == "ray-cluster-ml", "Cluster name must be 'ray-cluster-ml'"

    head_params = manifest["spec"]["headGroupSpec"]["rayStartParams"]
    assert head_params.get("dashboard-host") == "0.0.0.0", "dashboard-host must be '0.0.0.0'"
    assert head_params.get("block") == "true", "block must be 'true'"

    head_ports = manifest["spec"]["headGroupSpec"]["template"]["spec"]["containers"][0]["ports"]
    port_map = {p["name"]: p["containerPort"] for p in head_ports}
    assert port_map.get("gcs") == 6379, "GCS port must be 6379"
    assert port_map.get("dashboard") == 8265, "Dashboard port must be 8265"

    worker_spec = manifest["spec"]["workerGroupSpecs"][0]
    assert worker_spec["groupName"] == "worker-group", "Worker group name must be 'worker-group'"
    assert worker_spec["replicas"] == 2, "Worker replicas must be 2"
    assert worker_spec["minReplicas"] == 1, "minReplicas must be 1"
    assert worker_spec["maxReplicas"] == 5, "maxReplicas must be 5"

    worker_limits = worker_spec["template"]["spec"]["containers"][0]["resources"]["limits"]
    assert str(worker_limits.get("cpu")) == "2", "Worker CPU limit must be 2"
    assert str(worker_limits.get("memory")) == "4Gi", "Worker memory limit must be 4Gi"

    print("✓ ray01 passed!")


if __name__ == "__main__":
    verify()

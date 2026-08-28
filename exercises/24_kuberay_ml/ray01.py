"""
Exercise: exercises/24_kuberay_ml/ray01.py
Topic: RayCluster Core Architecture & Head Node

Context & Why:
KubeRay is the Kubernetes operator for Ray, the open-source unified compute framework used for
scaling AI, machine learning, and data processing workloads.

A Ray cluster follows a distributed architecture orchestrated by the `RayCluster` Custom Resource:
- Head Node: Runs the Global Control Store (GCS) metadata server on port 6379, the Ray Dashboard
  web UI on port 8265, the API server, and cluster scheduling coordinator. Configuring
  `rayStartParams` (`dashboard-host: '0.0.0.0'`, `block: 'true'`) ensures external accessibility
  and keeps the main head process running.
- Worker Nodes: Execute Ray tasks and actors. Organized into `workerGroupSpecs`, workers connect
  to the head node's GCS server and scale dynamically between `minReplicas` and `maxReplicas`.

Task:
Fix the RayCluster YAML manifest below to define a distributed Ray cluster:
1. Set 'apiVersion' to 'ray.io/v1' and 'kind' to 'RayCluster'.
2. Set 'metadata.name' to 'ray-cluster-ml'.
3. In 'spec.headGroupSpec.rayStartParams', set 'dashboard-host' to '0.0.0.0' and 'block' to 'true'.
4. In 'spec.headGroupSpec.template.spec.containers', define container 'ray-head' with image
   'rayproject/ray:2.35.0', and ports for GCS (containerPort: 6379, name: gcs) and
   Dashboard (containerPort: 8265, name: dashboard).
5. In 'spec.workerGroupSpecs', configure 'worker-group' with replicas: 2, minReplicas: 1, maxReplicas: 5,
   and container 'ray-worker' with image 'rayproject/ray:2.35.0' and limits of 2 CPUs and 4Gi memory.
"""

import yaml

from kubelings.validator import validate_manifest_text

# TODO: Fix the RayCluster YAML manifest by specifying the RayCluster kind, head group start parameters, GCS/dashboard ports, and worker resource limits.
# WHY: The RayCluster CRD automates the orchestration of Ray's distributed architecture on Kubernetes, coordinating the GCS metadata store and web dashboard on the head node while establishing a scalable worker group for parallel compute.
RAY_CLUSTER_MANIFEST = """
apiVersion: ???
kind: ???
metadata:
  name: ???
spec:
  rayVersion: '2.35.0'
  headGroupSpec:
    rayStartParams:
      dashboard-host: '127.0.0.1'
      block: 'false'
    template:
      spec:
        containers:
          - name: ???
            image: ???
            ports:
              - containerPort: 0
                name: gcs
              - containerPort: 0
                name: dashboard
  workerGroupSpecs:
    - groupName: ???
      replicas: 0
      minReplicas: 0
      maxReplicas: 0
      template:
        spec:
          containers:
            - name: ???
              image: ???
              resources:
                limits:
                  cpu: "0"
                  memory: 0Gi
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

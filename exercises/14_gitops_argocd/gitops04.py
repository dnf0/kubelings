"""
Exercise: Progressive Delivery with Argo Rollouts (gitops04)

Argo Rollouts replaces the standard Kubernetes Deployment controller to enable
advanced deployment strategies like Canary and Blue-Green with metric analysis.

Task:
Complete `get_rollout_manifest()` to define an Argo Rollout resource:
1. apiVersion: "argoproj.io/v1alpha1"
2. kind: "Rollout"
3. metadata:
   - name: "payment-service"
4. spec:
   - replicas: 5
   - strategy:
     - canary:
       - steps:
         - setWeight: 20
         - pause: {"duration": "10m"}
         - setWeight: 50
         - pause: {"duration": "30m"}
   - template:
     - metadata:
       - labels:
         - app: "payment"
     - spec:
       - containers:
         - name: "payment-api"
         - image: "payment:v2.0.0"
         - ports:
           - containerPort: 8080
"""

from typing import Any, Dict


def get_rollout_manifest() -> Dict[str, Any]:
    # TODO: Define and return the Argo Rollout manifest dictionary
    return {}


def verify() -> None:
    manifest = get_rollout_manifest()
    assert manifest, "Manifest cannot be empty"
    assert manifest.get("apiVersion") == "argoproj.io/v1alpha1"
    assert manifest.get("kind") == "Rollout"

    meta = manifest.get("metadata", {})
    assert meta.get("name") == "payment-service"

    spec = manifest.get("spec", {})
    assert spec.get("replicas") == 5

    strategy = spec.get("strategy", {})
    canary = strategy.get("canary", {})
    steps = canary.get("steps", [])
    assert len(steps) == 4
    assert steps[0].get("setWeight") == 20
    assert steps[1].get("pause", {}).get("duration") == "10m"
    assert steps[2].get("setWeight") == 50
    assert steps[3].get("pause", {}).get("duration") == "30m"

    containers = spec.get("template", {}).get("spec", {}).get("containers", [])
    assert len(containers) == 1
    assert containers[0].get("image") == "payment:v2.0.0"
    assert containers[0].get("ports", [{}])[0].get("containerPort") == 8080

    print("✓ Argo Rollout Canary validated successfully!")


if __name__ == "__main__":
    verify()

"""
Exercise: exercises/13_troubleshooting/troubleshoot05.py
Topic: Ephemeral Debug Containers & Event Triage

Instructions:
Production containers frequently use minimal or 'distroless' base images that
lack shells, curl, or debugging utilities. Kubernetes Ephemeral Containers
(`kubectl debug`) solve this by attaching diagnostic containers into a running
pod with process namespace sharing (`shareProcessNamespace: true`).

1. Define Pod 'distroless-app' in namespace 'production':
   - shareProcessNamespace: true
   - container 'app': image 'gcr.io/distroless/static:nonroot'
2. Define the ephemeral container specification dictionary `DEBUG_EPHEMERAL_CONTAINER`:
   - name: "debugger"
   - image: "busybox:1.36"
   - command: ["sh"]
   - targetContainerName: "app"
   - stdin: true, tty: true
3. Implement `triage_events(events: list) -> list`:
   - Keep only events where `type == "Warning"`.
   - Filter to keep events if `count >= 3` OR `reason in ("OOMKilled", "FailedScheduling", "BackOff", "Unhealthy")`.
   - Sort remaining events by `count` descending.
   - Return list of dicts with keys: `reason`, `message`, `count`.
"""

# I AM NOT DONE

from typing import Any, Dict, List

import yaml

from kubelings.validator import validate_manifest

POD_MANIFEST = """
apiVersion: v1
kind: Pod
metadata:
  name: distroless-app
  namespace: production
spec:
  shareProcessNamespace: ???
  containers:
  - name: app
    image: gcr.io/distroless/static:nonroot
"""

DEBUG_EPHEMERAL_CONTAINER: Dict[str, Any] = {
    "name": "debugger",
    "image": "busybox:1.36",
    # TODO: Complete ephemeral container spec
}


def triage_events(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    # TODO: Implement event triage filtering and sorting
    return []


def verify():
    manifest = yaml.safe_load(POD_MANIFEST)
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(manifest, expected_kind="Pod", expected_api_version="v1")

    metadata = manifest.get("metadata", {})
    assert metadata.get("name") == "distroless-app"
    assert metadata.get("namespace") == "production"
    assert manifest.get("spec", {}).get("shareProcessNamespace") is True

    # Check Ephemeral container spec
    assert DEBUG_EPHEMERAL_CONTAINER.get("name") == "debugger"
    assert DEBUG_EPHEMERAL_CONTAINER.get("image") == "busybox:1.36"
    assert DEBUG_EPHEMERAL_CONTAINER.get("command") == ["sh"]
    assert DEBUG_EPHEMERAL_CONTAINER.get("targetContainerName") == "app"
    assert DEBUG_EPHEMERAL_CONTAINER.get("stdin") is True
    assert DEBUG_EPHEMERAL_CONTAINER.get("tty") is True

    # Check Event Triage
    sample_events = [
        {"type": "Normal", "reason": "Scheduled", "message": "Successfully assigned", "count": 1},
        {"type": "Warning", "reason": "Unhealthy", "message": "Liveness probe failed", "count": 2},
        {"type": "Warning", "reason": "FailedMount", "message": "Volume not ready", "count": 1},
        {
            "type": "Warning",
            "reason": "BackOff",
            "message": "Back-off restarting failed container",
            "count": 7,
        },
        {
            "type": "Warning",
            "reason": "FailedScheduling",
            "message": "0/3 nodes available",
            "count": 5,
        },
    ]
    triaged = triage_events(sample_events)
    assert len(triaged) == 3, f"Expected 3 triaged events, got {len(triaged)}"

    # Order should be BackOff (7), FailedScheduling (5), Unhealthy (2)
    assert triaged[0]["reason"] == "BackOff" and triaged[0]["count"] == 7
    assert triaged[1]["reason"] == "FailedScheduling" and triaged[1]["count"] == 5
    assert triaged[2]["reason"] == "Unhealthy" and triaged[2]["count"] == 2

    print("✓ troubleshoot05 passed!")


if __name__ == "__main__":
    verify()

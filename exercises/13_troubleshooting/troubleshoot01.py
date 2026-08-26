"""
Exercise: exercises/13_troubleshooting/troubleshoot01.py
Topic: Debugging CrashLoopBackOff & Exit Codes

Instructions:
When a container in Kubernetes repeatedly terminates and restarts, its status
transitions to `CrashLoopBackOff`. The container exit code provides the primary
clue to the root cause:
- Exit code 137: Terminated by SIGKILL (often OOMKilled due to memory limits).
- Exit code 143: Terminated by SIGTERM (graceful termination).
- Exit code 1: Application-level exception / unhandled error / missing config.
- Exit code 127: Executable or command binary not found.

1. Implement `diagnose_exit_code(exit_code: int) -> dict`:
   - Return dictionary with keys "reason" and "cause" for codes 137, 143, 1, 127,
     or "Unknown" for other codes.
2. Fix Pod 'crasher-pod-fixed' in namespace 'troubleshoot':
   - Set container 'api-server' memory requests to "256Mi" and memory limits to "512Mi".
   - Set CPU requests to "250m" and CPU limits to "500m".
   - Supply the missing environment variable 'DATABASE_URL' = 'postgres://db.internal:5432/app'.
"""

# I AM NOT DONE

from typing import Any, Dict
import yaml
from kubelings.validator import validate_manifest

POD_MANIFEST = """
apiVersion: v1
kind: Pod
metadata:
  name: crasher-pod-fixed
  namespace: troubleshoot
spec:
  containers:
  - name: api-server
    image: nginx:alpine
    resources:
      requests:
        cpu: ???
        memory: ???
      limits:
        cpu: "500m"
        memory: ???
    env:
    - name: ???
      value: ???
"""


def diagnose_exit_code(exit_code: int) -> Dict[str, Any]:
    # TODO: Implement exit code diagnosis logic
    return {
        "reason": "TODO",
        "cause": "TODO",
    }


def verify():
    # 1. Test Diagnostic Function
    diag137 = diagnose_exit_code(137)
    assert diag137["reason"] == "OOMKilled"
    assert "memory" in diag137["cause"].lower()

    diag143 = diagnose_exit_code(143)
    assert diag143["reason"] == "SIGTERM"

    diag1 = diagnose_exit_code(1)
    assert diag1["reason"] == "ApplicationError"

    diag127 = diagnose_exit_code(127)
    assert diag127["reason"] == "CommandNotFound"

    diag_unknown = diagnose_exit_code(99)
    assert diag_unknown["reason"] == "Unknown"

    # 2. Test Fixed Pod Manifest
    manifest = yaml.safe_load(POD_MANIFEST)
    assert manifest is not None, "Manifest cannot be empty"
    validate_manifest(manifest, expected_kind="Pod", expected_api_version="v1")

    metadata = manifest.get("metadata", {})
    assert metadata.get("name") == "crasher-pod-fixed"
    assert metadata.get("namespace") == "troubleshoot"

    container = manifest.get("spec", {}).get("containers", [])[0]
    assert container.get("name") == "api-server"

    res = container.get("resources", {})
    assert res.get("requests", {}).get("cpu") == "250m"
    assert res.get("requests", {}).get("memory") == "256Mi"
    assert res.get("limits", {}).get("cpu") == "500m"
    assert res.get("limits", {}).get("memory") == "512Mi"

    env_vars = container.get("env", [])
    db_env = next((e for e in env_vars if e.get("name") == "DATABASE_URL"), None)
    assert db_env is not None, "Must define DATABASE_URL environment variable"
    assert db_env.get("value") == "postgres://db.internal:5432/app"

    print("✓ troubleshoot01 passed!")


if __name__ == "__main__":
    verify()

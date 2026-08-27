"""
Solution: solutions/24_kuberay_ml/ray04.py
Topic: RayService for Production LLM Serving
"""

import yaml

from kubelings.validator import validate_manifest_text

RAY_SERVICE_MANIFEST = """
apiVersion: ray.io/v1
kind: RayService
metadata:
  name: ray-llm-service
spec:
  serviceUnhealthyThreshold: 300
  rayClusterSpec:
    rayVersion: '2.35.0'
    headGroupSpec:
      rayStartParams:
        dashboard-host: '0.0.0.0'
      template:
        spec:
          containers:
            - name: ray-head
              image: rayproject/ray:2.35.0
  serveConfigV2: |
    applications:
      - name: llm_app
        route_prefix: /v1
        import_path: llm_serve:model
        runtime_env: {}
"""


def verify():
    passed, errors = validate_manifest_text(RAY_SERVICE_MANIFEST, "ray04")
    assert passed, f"RayService validation failed: {errors}"

    manifest = yaml.safe_load(RAY_SERVICE_MANIFEST)
    assert manifest["metadata"]["name"] == "ray-llm-service"
    assert manifest["spec"]["serviceUnhealthyThreshold"] == 300

    serve_cfg = yaml.safe_load(manifest["spec"]["serveConfigV2"])
    apps = serve_cfg.get("applications", [])
    assert len(apps) >= 1, "serveConfigV2 must contain at least 1 application"
    app = apps[0]
    assert app.get("name") == "llm_app", "Application name must be 'llm_app'"
    assert app.get("route_prefix") == "/v1", "Route prefix must be '/v1'"
    assert app.get("import_path") == "llm_serve:model", "Import path must be 'llm_serve:model'"

    print("✓ ray04 passed!")


if __name__ == "__main__":
    verify()

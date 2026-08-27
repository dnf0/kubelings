"""
Exercise: exercises/24_kuberay_ml/ray04.py
Topic: RayService for Production LLM Serving

Instructions:
Author a RayService manifest named 'ray-llm-service' for serving an LLM model:
1. Set 'apiVersion' to 'ray.io/v1' and 'kind' to 'RayService'.
2. Set 'spec.serviceUnhealthyThreshold' to 300.
3. In 'spec.rayClusterSpec', define 'rayVersion' as '2.35.0' and 'headGroupSpec' with container 'ray-head' running 'rayproject/ray:2.35.0'.
4. In 'spec.serveConfigV2', define an application named 'llm_app' with route prefix '/v1', import path 'llm_serve:model', and empty runtime_env.
"""

import yaml

from kubelings.validator import validate_manifest_text

RAY_SERVICE_MANIFEST = """
apiVersion: ray.io/v1
kind: RayService
metadata:
  name: ray-llm-service
spec:
  serviceUnhealthyThreshold: 0
  rayClusterSpec:
    rayVersion: '2.35.0'
    headGroupSpec:
      rayStartParams:
        dashboard-host: '0.0.0.0'
      template:
        spec:
          containers:
            - name: ???
              image: ???
  serveConfigV2: |
    applications: []
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

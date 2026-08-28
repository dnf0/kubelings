"""
Chapter 20: Declarative Customization with Kustomize
Exercise 20.4: Kustomize Multi-Environment Overlays & Image Transforms

Context & Why:
Managing distinct deployment environments (e.g. dev, staging, prod) often leads to
configuration drift and manifest duplication if each environment maintains standalone YAMLs.
Kustomize solves this with the Base and Overlay architecture.

An overlay references a common base (`resources: ['../../base']`) and layers on environment-specific
deltas. In production overlays, platform engineers adjust the `namespace` to `production`,
prefix all resource names with `prod-`, scale workloads to handle production traffic via `replicas: [{name: webapp, count: 10}]`,
and substitute development container image coordinates with pinned production registry tags
using `images: [{name: webapp, newName: quay.io/company/webapp, newTag: v3.1.0}]`.

Task: Construct a production environment overlay kustomization.yaml manifest.
Requirements:
- apiVersion: 'kustomize.config.k8s.io/v1beta1'
- kind: 'Kustomization'
- resources: ['../../base']
- namespace: 'production'
- namePrefix: 'prod-'
- images:
    - name: 'webapp'
      newName: 'quay.io/company/webapp'
      newTag: 'v3.1.0'
- replicas:
    - name: 'webapp'
      count: 10
"""

from typing import Any, Dict

import yaml


def get_prod_overlay() -> Dict[str, Any]:
    manifest_yaml = """
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
"""
    # TODO: Update manifest_yaml with the production overlay resources, namespace, prefix, image transforms, and replicas, returning the parsed dictionary (e.g., via yaml.safe_load).
    # WHY: Kustomize overlays compose base manifests with environment-specific overrides (replicas, image tags, namespaces),
    #      upholding DRY principles and preventing configuration drift between development and production.
    return {}


if __name__ == "__main__":
    overlay = get_prod_overlay()
    assert overlay.get("apiVersion") == "kustomize.config.k8s.io/v1beta1"
    assert "../../base" in overlay.get("resources", [])
    assert overlay.get("namespace") == "production"
    assert overlay.get("namePrefix") == "prod-"
    images = overlay.get("images", [])
    assert len(images) == 1
    assert images[0].get("name") == "webapp"
    assert images[0].get("newName") == "quay.io/company/webapp"
    assert images[0].get("newTag") == "v3.1.0"
    replicas = overlay.get("replicas", [])
    assert len(replicas) == 1
    assert replicas[0].get("name") == "webapp"
    assert replicas[0].get("count") == 10
    print("✓ Kustomize production overlay validation passed!")

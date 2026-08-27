# I AM NOT DONE
"""
Chapter 20: Declarative Customization with Kustomize
Exercise 20.4: Kustomize Multi-Environment Overlays & Image Transforms

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

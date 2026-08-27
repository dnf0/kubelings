"""
Chapter 20: Declarative Customization with Kustomize
Exercise 20.1: Kustomize Base Manifests & Metadata Transformations

Task: Construct a valid kustomization.yaml configuration dictionary for a base tier.
Requirements:
- apiVersion: 'kustomize.config.k8s.io/v1beta1'
- kind: 'Kustomization'
- resources: ['deployment.yaml', 'service.yaml']
- namespace: 'ecommerce-core'
- namePrefix: 'core-'
- commonLabels:
    app.kubernetes.io/managed-by: 'kustomize'
    tier: 'backend'
- commonAnnotations:
    team: 'platform'
"""

from typing import Any, Dict

import yaml


def get_kustomization_base() -> Dict[str, Any]:
    manifest_yaml = """
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
"""
    return {}


if __name__ == "__main__":
    base = get_kustomization_base()
    assert base.get("apiVersion") == "kustomize.config.k8s.io/v1beta1"
    assert base.get("kind") == "Kustomization"
    assert "deployment.yaml" in base.get("resources", [])
    assert "service.yaml" in base.get("resources", [])
    assert base.get("namespace") == "ecommerce-core"
    assert base.get("namePrefix") == "core-"
    assert base.get("commonLabels", {}).get("app.kubernetes.io/managed-by") == "kustomize"
    assert base.get("commonLabels", {}).get("tier") == "backend"
    assert base.get("commonAnnotations", {}).get("team") == "platform"
    print("✓ Kustomize base metadata validation passed!")

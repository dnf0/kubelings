"""
Chapter 20: Declarative Customization with Kustomize
Exercise 20.1: Kustomize Base Manifests & Metadata Transformations

Context & Why:
Kustomize is a declarative, template-free configuration management engine built directly
into `kubectl`. Unlike Helm, which relies on parameterized string templating, Kustomize works
with pure, valid Kubernetes manifests and applies structured transformations at build time.

A base `kustomization.yaml` declares a root set of resources and applies uniform transformations.
Setting `namespace`, `namePrefix: 'core-'`, `commonLabels`, and `commonAnnotations` at the base
level injects standard organizational metadata and scopes resource names without requiring
manual edits across individual workload, service, and ingress YAML files.

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
    # TODO: Update manifest_yaml with the base kustomization resources, namespace, prefix, labels, and annotations, returning the parsed dictionary (e.g., via yaml.safe_load).
    # WHY: Base kustomizations declare foundation resources and inject cross-cutting metadata (labels, annotations, prefixes)
    #      across all child resources without mutating raw source YAMLs.
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

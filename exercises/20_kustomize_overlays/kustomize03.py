# I AM NOT DONE
"""
Chapter 20: Declarative Customization with Kustomize
Exercise 20.3: Kustomize Strategic Merge & JSON6902 Target Patches

Task: Construct a kustomization.yaml applying targeted JSON 6902 patches to a base Deployment.
Requirements:
- apiVersion: 'kustomize.config.k8s.io/v1beta1'
- kind: 'Kustomization'
- resources: ['../../base']
- patches: list containing a patch targeting the 'webapp' Deployment:
    - target: {'group': 'apps', 'version': 'v1', 'kind': 'Deployment', 'name': 'webapp'}
    - patch:
        - op: 'replace', path: '/spec/replicas', value: 5
        - op: 'add', path: '/spec/template/spec/containers/0/resources/limits/cpu', value: '500m'
"""

from typing import Any, Dict

import yaml


def get_patch_kustomization() -> Dict[str, Any]:
    manifest_yaml = """
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
"""
    return {}


if __name__ == "__main__":
    kust = get_patch_kustomization()
    assert kust.get("apiVersion") == "kustomize.config.k8s.io/v1beta1"
    assert "../../base" in kust.get("resources", [])
    patches = kust.get("patches", [])
    assert len(patches) == 1
    target = patches[0].get("target", {})
    assert target.get("kind") == "Deployment"
    assert target.get("name") == "webapp"
    patch_content = patches[0].get("patch", "")
    assert "replace" in patch_content
    assert "/spec/replicas" in patch_content
    print("✓ Kustomize target patches validation passed!")

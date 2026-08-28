"""
Chapter 20: Declarative Customization with Kustomize
Exercise 20.3: Kustomize Strategic Merge & JSON6902 Target Patches

Context & Why:
When customizing shared or third-party base Kubernetes manifests, engineers often need
to override specific fields (such as scaling replicas or adjusting container CPU limits)
without creating and maintaining a complete copy of the source manifest.

Kustomize supports granular resource mutation using RFC 6902 JSON Patches. By combining
a `target` selector (`group`, `version`, `kind`, `name`) with RFC 6902 operations (`op: replace`,
`path: /spec/replicas`, `value: 5`), platform teams can make surgical, non-destructive alterations
to upstream resources. This keeps environmental overlay configurations minimal, transparent,
and resilient against upstream manifest structural shifts.

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
    # TODO: Update manifest_yaml with the target Deployment selector and RFC 6902 JSON patch operations, returning the parsed dictionary (e.g., via yaml.safe_load).
    # WHY: RFC 6902 JSON patches allow precise, surgical field modifications on base manifests without duplicating
    #      large resource definitions or maintaining unmaintainable forks.
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

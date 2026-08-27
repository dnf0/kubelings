"""
Exercise: ArgoCD ApplicationSet Matrix Generator (gitops02)

ArgoCD ApplicationSets allow templated multi-cluster and multi-environment
application generation using generators such as Git directories, List, or Matrix.

Task:
Complete `get_applicationset_manifest()` to define an ApplicationSet that uses
a `git` generator to discover all services under `apps/*` and deploys them to target clusters.

Specification:
1. apiVersion: "argoproj.io/v1alpha1"
2. kind: "ApplicationSet"
3. metadata:
   - name: "infra-apps"
   - namespace: "argocd"
4. spec:
   - generators:
     - git:
       - repoURL: "https://github.com/my-org/gitops-repo.git"
       - revision: "HEAD"
       - directories:
         - path: "apps/*"
   - template:
     - metadata:
       - name: "{{path.basename}}"
     - spec:
       - project: "default"
       - source:
         - repoURL: "https://github.com/my-org/gitops-repo.git"
         - targetRevision: "HEAD"
         - path: "{{path}}"
       - destination:
         - server: "https://kubernetes.default.svc"
         - namespace: "{{path.basename}}"
"""

from typing import Any, Dict

import yaml


def get_applicationset_manifest() -> Dict[str, Any]:
    # TODO: Define and return the ArgoCD ApplicationSet manifest dictionary
    return {}


def verify() -> None:
    manifest = get_applicationset_manifest()
    assert manifest, "Manifest cannot be empty"
    assert manifest.get("apiVersion") == "argoproj.io/v1alpha1"
    assert manifest.get("kind") == "ApplicationSet"

    meta = manifest.get("metadata", {})
    assert meta.get("name") == "infra-apps"
    assert meta.get("namespace") == "argocd"

    spec = manifest.get("spec", {})
    generators = spec.get("generators", [])
    assert len(generators) > 0, "Expected at least one generator"

    git_gen = generators[0].get("git", {})
    assert git_gen.get("repoURL") == "https://github.com/my-org/gitops-repo.git"
    assert git_gen.get("revision") == "HEAD"
    dirs = git_gen.get("directories", [])
    assert any(d.get("path") == "apps/*" for d in dirs)

    tmpl = spec.get("template", {})
    tmpl_meta = tmpl.get("metadata", {})
    assert tmpl_meta.get("name") == "{{path.basename}}"

    tmpl_spec = tmpl.get("spec", {})
    assert tmpl_spec.get("project") == "default"
    assert tmpl_spec.get("source", {}).get("path") == "{{path}}"
    assert tmpl_spec.get("destination", {}).get("namespace") == "{{path.basename}}"

    print("✓ ArgoCD ApplicationSet validated successfully!")


if __name__ == "__main__":
    verify()

"""
Solution: GitOps with ArgoCD Application CRD (gitops01)
"""

from typing import Any, Dict

import yaml


def get_argocd_application_manifest() -> Dict[str, Any]:
    return {
        "apiVersion": "argoproj.io/v1alpha1",
        "kind": "Application",
        "metadata": {
            "name": "guestbook-app",
            "namespace": "argocd",
        },
        "spec": {
            "project": "default",
            "source": {
                "repoURL": "https://github.com/argoproj/argocd-example-apps.git",
                "targetRevision": "HEAD",
                "path": "guestbook",
            },
            "destination": {
                "server": "https://kubernetes.default.svc",
                "namespace": "guestbook",
            },
            "syncPolicy": {
                "automated": {
                    "prune": True,
                    "selfHeal": True,
                }
            },
        },
    }


def verify() -> None:
    manifest = get_argocd_application_manifest()
    assert manifest, "Manifest cannot be empty"
    assert manifest.get("apiVersion") == "argoproj.io/v1alpha1", (
        "Expected apiVersion argoproj.io/v1alpha1"
    )
    assert manifest.get("kind") == "Application", "Expected kind Application"

    meta = manifest.get("metadata", {})
    assert meta.get("name") == "guestbook-app", "Expected metadata.name to be 'guestbook-app'"
    assert meta.get("namespace") == "argocd", "Expected metadata.namespace to be 'argocd'"

    spec = manifest.get("spec", {})
    assert spec.get("project") == "default", "Expected spec.project to be 'default'"

    source = spec.get("source", {})
    assert source.get("repoURL") == "https://github.com/argoproj/argocd-example-apps.git"
    assert source.get("targetRevision") == "HEAD"
    assert source.get("path") == "guestbook"

    dest = spec.get("destination", {})
    assert dest.get("server") == "https://kubernetes.default.svc"
    assert dest.get("namespace") == "guestbook"

    sync_policy = spec.get("syncPolicy", {})
    automated = sync_policy.get("automated", {})
    assert automated.get("prune") is True, "Expected syncPolicy.automated.prune to be True"
    assert automated.get("selfHeal") is True, "Expected syncPolicy.automated.selfHeal to be True"

    # Verify YAML serialization works
    dumped = yaml.safe_dump(manifest)
    assert "guestbook-app" in dumped
    print("✓ ArgoCD Application CRD validated successfully!")


if __name__ == "__main__":
    verify()

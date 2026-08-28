"""
Exercise: GitOps with ArgoCD Application CRD (gitops01)

Context & Why:
GitOps establishes Git repositories as the single source of truth for declared
system state in Kubernetes. ArgoCD implements this paradigm using an active
controller loop that continuously compares desired state (manifests in Git) with
the live cluster state.

When divergence occurs (e.g., direct manual edits or config drift), ArgoCD detects
the 'OutOfSync' condition. Enabling automated sync policies with `selfHeal: True`
instructs the controller to automatically revert unauthorized live changes back to
the Git baseline. Enabling `prune: True` ensures that when Kubernetes resources
are deleted from the Git repository, ArgoCD automatically cleans them up from the
cluster, preventing dangerous orphaned workloads and configuration clutter.

Task:
Complete `get_argocd_application_manifest()` to return a dictionary representing
a valid ArgoCD Application resource with:
1. apiVersion: "argoproj.io/v1alpha1"
2. kind: "Application"
3. metadata:
   - name: "guestbook-app"
   - namespace: "argocd"
4. spec:
   - project: "default"
   - source:
     - repoURL: "https://github.com/argoproj/argocd-example-apps.git"
     - targetRevision: "HEAD"
     - path: "guestbook"
   - destination:
     - server: "https://kubernetes.default.svc"
     - namespace: "guestbook"
   - syncPolicy:
     - automated:
       - prune: True
       - selfHeal: True
"""

from typing import Any, Dict

import yaml


def get_argocd_application_manifest() -> Dict[str, Any]:
    # TODO: Construct and return the dictionary representation of an ArgoCD Application CRD
    #       specifying source repo URL, revision, target cluster destination, and automated sync policies.
    # WHY: ArgoCD continuously reconciles the live state in the cluster against the desired state defined
    #      in Git, ensuring automated drift correction (selfHeal) and garbage-collecting orphaned resources (prune).
    return {}


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

"""
Validators for Chapter 14: GitOps Continuous Delivery with ArgoCD
"""

from typing import Any, Dict

import yaml

from kubelings.validators import register_validator


def get_argocd_application_manifest() -> Dict[str, Any]:
    return {
        "apiVersion": "argoproj.io/v1alpha1",
        "kind": "Application",
        "metadata": {"name": "guestbook-app", "namespace": "argocd"},
        "spec": {
            "project": "default",
            "source": {
                "repoURL": "https://github.com/argoproj/argocd-example-apps.git",
                "targetRevision": "HEAD",
                "path": "guestbook",
            },
            "destination": {"server": "https://kubernetes.default.svc", "namespace": "guestbook"},
            "syncPolicy": {"automated": {"prune": True, "selfHeal": True}},
        },
    }


@register_validator("gitops01")
def validate_gitops01(manifest: Any, raw_yaml: str = "") -> None:
    manifest = manifest
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
    dumped = yaml.safe_dump(manifest)
    assert "guestbook-app" in dumped


def get_applicationset_manifest() -> Dict[str, Any]:
    return {
        "apiVersion": "argoproj.io/v1alpha1",
        "kind": "ApplicationSet",
        "metadata": {"name": "infra-apps", "namespace": "argocd"},
        "spec": {
            "generators": [
                {
                    "git": {
                        "repoURL": "https://github.com/my-org/gitops-repo.git",
                        "revision": "HEAD",
                        "directories": [{"path": "apps/*"}],
                    }
                }
            ],
            "template": {
                "metadata": {"name": "{{path.basename}}"},
                "spec": {
                    "project": "default",
                    "source": {
                        "repoURL": "https://github.com/my-org/gitops-repo.git",
                        "targetRevision": "HEAD",
                        "path": "{{path}}",
                    },
                    "destination": {
                        "server": "https://kubernetes.default.svc",
                        "namespace": "{{path.basename}}",
                    },
                },
            },
        },
    }


@register_validator("gitops02")
def validate_gitops02(manifest: Any, raw_yaml: str = "") -> None:
    manifest = manifest
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
    assert any((d.get("path") == "apps/*" for d in dirs))
    tmpl = spec.get("template", {})
    tmpl_meta = tmpl.get("metadata", {})
    assert tmpl_meta.get("name") == "{{path.basename}}"
    tmpl_spec = tmpl.get("spec", {})
    assert tmpl_spec.get("project") == "default"
    assert tmpl_spec.get("source", {}).get("path") == "{{path}}"
    assert tmpl_spec.get("destination", {}).get("namespace") == "{{path.basename}}"


def get_sync_policy_manifest() -> Dict[str, Any]:
    return {
        "automated": {"prune": True, "selfHeal": True},
        "syncOptions": ["CreateNamespace=true", "ServerSideApply=true"],
        "retry": {"limit": 5, "backoff": {"duration": "5s", "factor": 2, "maxDuration": "3m"}},
    }


@register_validator("gitops03")
def validate_gitops03(manifest: Any, raw_yaml: str = "") -> None:
    policy = manifest
    assert policy, "Policy cannot be empty"
    sync_options = policy.get("syncOptions", [])
    assert "CreateNamespace=true" in sync_options
    assert "ServerSideApply=true" in sync_options
    retry = policy.get("retry", {})
    assert retry.get("limit") == 5
    backoff = retry.get("backoff", {})
    assert backoff.get("duration") == "5s"
    assert backoff.get("factor") == 2
    assert backoff.get("maxDuration") == "3m"
    automated = policy.get("automated", {})
    assert automated.get("prune") is True
    assert automated.get("selfHeal") is True


def get_rollout_manifest() -> Dict[str, Any]:
    return {
        "apiVersion": "argoproj.io/v1alpha1",
        "kind": "Rollout",
        "metadata": {"name": "payment-service"},
        "spec": {
            "replicas": 5,
            "strategy": {
                "canary": {
                    "steps": [
                        {"setWeight": 20},
                        {"pause": {"duration": "10m"}},
                        {"setWeight": 50},
                        {"pause": {"duration": "30m"}},
                    ]
                }
            },
            "template": {
                "metadata": {"labels": {"app": "payment"}},
                "spec": {
                    "containers": [
                        {
                            "name": "payment-api",
                            "image": "payment:v2.0.0",
                            "ports": [{"containerPort": 8080}],
                        }
                    ]
                },
            },
        },
    }


@register_validator("gitops04")
def validate_gitops04(manifest: Any, raw_yaml: str = "") -> None:
    manifest = manifest
    assert manifest, "Manifest cannot be empty"
    assert manifest.get("apiVersion") == "argoproj.io/v1alpha1"
    assert manifest.get("kind") == "Rollout"
    meta = manifest.get("metadata", {})
    assert meta.get("name") == "payment-service"
    spec = manifest.get("spec", {})
    assert spec.get("replicas") == 5
    strategy = spec.get("strategy", {})
    canary = strategy.get("canary", {})
    steps = canary.get("steps", [])
    assert len(steps) == 4
    assert steps[0].get("setWeight") == 20
    assert steps[1].get("pause", {}).get("duration") == "10m"
    assert steps[2].get("setWeight") == 50
    assert steps[3].get("pause", {}).get("duration") == "30m"
    containers = spec.get("template", {}).get("spec", {}).get("containers", [])
    assert len(containers) == 1
    assert containers[0].get("image") == "payment:v2.0.0"
    assert containers[0].get("ports", [{}])[0].get("containerPort") == 8080

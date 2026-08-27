# I AM NOT DONE
"""
Exercise: Sync Windows & Retry Strategies in ArgoCD (gitops03)

ArgoCD supports advanced sync policies including exponential retry backoff,
sync options (e.g. CreateNamespace, ServerSideApply), and sync windows for maintenance.

Task:
Complete `get_sync_policy_manifest()` returning an ArgoCD Application spec with:
1. syncPolicy.syncOptions:
   - "CreateNamespace=true"
   - "ServerSideApply=true"
2. syncPolicy.retry:
   - limit: 5
   - backoff:
     - duration: "5s"
     - factor: 2
     - maxDuration: "3m"
3. syncPolicy.automated:
   - prune: True
   - selfHeal: True
"""

from typing import Any, Dict


def get_sync_policy_manifest() -> Dict[str, Any]:
    # TODO: Define and return the ArgoCD sync policy dictionary
    return {}


def verify() -> None:
    policy = get_sync_policy_manifest()
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

    print("✓ ArgoCD Sync Policy & Retry strategy validated successfully!")


if __name__ == "__main__":
    verify()

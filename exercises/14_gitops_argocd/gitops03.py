"""
Exercise: Sync Windows & Retry Strategies in ArgoCD (gitops03)

Context & Why:
In production Kubernetes environments, continuous delivery pipelines must withstand
transient network glitches, webhook timeouts, and CRD registration race conditions.
ArgoCD provides granular `syncPolicy` configurations to make automated reconciliation
fault-tolerant.

Using `retry` with exponential backoff (`factor: 2`, `duration: '5s'`, `maxDuration: '3m'`)
prevents denial-of-service pressure on the Kubernetes API server while allowing temporary
failures (e.g., waiting for an admission webhook pod to become ready) to self-resolve.
Complementary `syncOptions` like `CreateNamespace=true` ensure prerequisites exist,
while `ServerSideApply=true` offloads field management and 3-way merging to the API
server for conflict-free resource updates.

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
    # TODO: Construct and return the dictionary representation of an ArgoCD syncPolicy specification
    #       configuring syncOptions (CreateNamespace, ServerSideApply), retry backoff, and automated sync.
    # WHY: Exponential retry backoff protects the API server during transient failures, while Server-Side Apply
    #      ensures reliable declarative field ownership and eliminates client-side merge conflicts.
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

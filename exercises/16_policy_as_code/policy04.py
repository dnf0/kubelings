"""
Chapter 16: Policy as Code with Kyverno & Gatekeeper
Exercise 16.4: OPA Gatekeeper ConstraintTemplate & Constraint

Context & Why:
Open Policy Agent (OPA) Gatekeeper is a widely adopted policy engine in Kubernetes that
uses the declarative query language Rego. To avoid writing monolithic, hardcoded policies,
Gatekeeper introduces a two-tier architecture: `ConstraintTemplate` and `Constraint`.

A `ConstraintTemplate` defines both the CRD schema (specifying parameters like allowed labels
via OpenAPI v3) and the underlying Rego evaluation logic (`package k8srequiredlabels`).
Platform administrators can then instantiate multiple lightweight `Constraint` CRDs that pass
different parameter configurations (e.g. requiring `owner` in development but requiring
`owner`, `cost-center`, and `env` in production) without changing the core Rego rule logic.

Task:
Fix the OPA Gatekeeper ConstraintTemplate manifest function to return the parsed manifest dictionary
containing the schema definition and Rego violation rules for required labels.
"""

from typing import Any, Dict

import yaml


def get_gatekeeper_template_manifest() -> Dict[str, Any]:
    manifest_yaml = """
apiVersion: templates.gatekeeper.sh/v1
kind: ConstraintTemplate
metadata:
  name: k8srequiredlabels
spec:
  crd:
    spec:
      names:
        kind: K8sRequiredLabels
      validation:
        openAPIV3Schema:
          type: object
          properties:
            labels:
              type: array
              items:
                type: string
  targets:
    - target: admission.k8s.gatekeeper.sh
      rego: |
        package k8srequiredlabels
        violation[{"msg": msg}] {
          provided := {label | input.review.object.metadata.labels[label]}
          required := {label | label := input.parameters.labels[_]}
          missing := required - provided
          count(missing) > 0
          msg := sprintf("You must provide labels: %v", [missing])
        }
"""
    # TODO: Parse and return the OPA Gatekeeper ConstraintTemplate manifest dictionary (e.g., using yaml.safe_load).
    # WHY: ConstraintTemplates decouple policy logic (written in Rego) from runtime configuration parameters,
    #      enabling flexible, reusable admission guardrails across heterogeneous cluster fleets.
    return {}


if __name__ == "__main__":
    tmpl = get_gatekeeper_template_manifest()
    assert tmpl.get("kind") == "ConstraintTemplate"
    assert tmpl.get("apiVersion") == "templates.gatekeeper.sh/v1"
    targets = tmpl.get("spec", {}).get("targets", [])
    assert len(targets) == 1
    assert "package k8srequiredlabels" in targets[0]["rego"]
    print("✓ OPA Gatekeeper template validation passed!")

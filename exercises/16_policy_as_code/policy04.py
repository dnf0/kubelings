# I AM NOT DONE
"""
Chapter 16: Policy as Code with Kyverno & Gatekeeper
Exercise 16.4: OPA Gatekeeper ConstraintTemplate & Constraint

Fix the OPA Gatekeeper ConstraintTemplate manifest defining the Rego
logic to verify mandatory labels and the associated constraint.
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
    # Fix the return dictionary
    return {}


if __name__ == "__main__":
    tmpl = get_gatekeeper_template_manifest()
    assert tmpl.get("kind") == "ConstraintTemplate"
    assert tmpl.get("apiVersion") == "templates.gatekeeper.sh/v1"
    targets = tmpl.get("spec", {}).get("targets", [])
    assert len(targets) == 1
    assert "package k8srequiredlabels" in targets[0]["rego"]
    print("✓ OPA Gatekeeper template validation passed!")

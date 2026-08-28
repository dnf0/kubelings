"""
Validators for Chapter 16: Policy as Code (Kyverno & Gatekeeper)
"""

from typing import Any, Dict

import yaml

from kubelings.validators import register_validator


def get_kyverno_policy_manifest() -> Dict[str, Any]:
    manifest_yaml = '\napiVersion: kyverno.io/v1\nkind: ClusterPolicy\nmetadata:\n  name: require-labels\nspec:\n  validationFailureAction: Enforce\n  background: true\n  rules:\n  - name: check-team-and-app-labels\n    match:\n      any:\n      - resources:\n          kinds:\n          - Pod\n    validate:\n      message: "Label \'app.kubernetes.io/name\' and \'team\' are required."\n      pattern:\n        metadata:\n          labels:\n            app.kubernetes.io/name: "?*"\n            team: "?*"\n'
    return yaml.safe_load(manifest_yaml)


@register_validator("policy01")
def validate_policy01(manifest: Any, raw_yaml: str = "") -> None:
    policy = manifest
    assert policy.get("kind") == "ClusterPolicy"
    assert policy.get("apiVersion") == "kyverno.io/v1"
    rules = policy.get("spec", {}).get("rules", [])
    assert len(rules) == 1
    assert "app.kubernetes.io/name" in rules[0]["validate"]["pattern"]["metadata"]["labels"]


def get_kyverno_mutation_manifest() -> Dict[str, Any]:
    manifest_yaml = "\napiVersion: kyverno.io/v1\nkind: ClusterPolicy\nmetadata:\n  name: mutate-pod-security\nspec:\n  rules:\n  - name: inject-run-as-non-root\n    match:\n      any:\n      - resources:\n          kinds:\n          - Pod\n    mutate:\n      patchStrategicMerge:\n        spec:\n          +(securityContext):\n            runAsNonRoot: true\n"
    return yaml.safe_load(manifest_yaml)


@register_validator("policy02")
def validate_policy02(manifest: Any, raw_yaml: str = "") -> None:
    policy = manifest
    assert policy.get("kind") == "ClusterPolicy"
    rules = policy.get("spec", {}).get("rules", [])
    assert len(rules) == 1
    mutate = rules[0].get("mutate", {})
    assert "patchStrategicMerge" in mutate


def get_kyverno_generate_manifest() -> Dict[str, Any]:
    manifest_yaml = '\napiVersion: kyverno.io/v1\nkind: ClusterPolicy\nmetadata:\n  name: generate-default-deny\nspec:\n  rules:\n  - name: generate-deny-all\n    match:\n      any:\n      - resources:\n          kinds:\n          - Namespace\n    generate:\n      apiVersion: networking.k8s.io/v1\n      kind: NetworkPolicy\n      name: default-deny-all\n      namespace: "{{request.object.metadata.name}}"\n      synchronize: true\n      data:\n        spec:\n          podSelector: {}\n          policyTypes:\n          - Ingress\n          - Egress\n'
    return yaml.safe_load(manifest_yaml)


@register_validator("policy03")
def validate_policy03(manifest: Any, raw_yaml: str = "") -> None:
    policy = manifest
    assert policy.get("kind") == "ClusterPolicy"
    rules = policy.get("spec", {}).get("rules", [])
    assert len(rules) == 1
    gen = rules[0].get("generate", {})
    assert gen.get("kind") == "NetworkPolicy"
    assert gen.get("synchronize") is True


def get_gatekeeper_template_manifest() -> Dict[str, Any]:
    manifest_yaml = '\napiVersion: templates.gatekeeper.sh/v1\nkind: ConstraintTemplate\nmetadata:\n  name: k8srequiredlabels\nspec:\n  crd:\n    spec:\n      names:\n        kind: K8sRequiredLabels\n      validation:\n        openAPIV3Schema:\n          type: object\n          properties:\n            labels:\n              type: array\n              items:\n                type: string\n  targets:\n    - target: admission.k8s.gatekeeper.sh\n      rego: |\n        package k8srequiredlabels\n        violation[{"msg": msg}] {\n          provided := {label | input.review.object.metadata.labels[label]}\n          required := {label | label := input.parameters.labels[_]}\n          missing := required - provided\n          count(missing) > 0\n          msg := sprintf("You must provide labels: %v", [missing])\n        }\n'
    return yaml.safe_load(manifest_yaml)


@register_validator("policy04")
def validate_policy04(manifest: Any, raw_yaml: str = "") -> None:
    tmpl = manifest
    assert tmpl.get("kind") == "ConstraintTemplate"
    assert tmpl.get("apiVersion") == "templates.gatekeeper.sh/v1"
    targets = tmpl.get("spec", {}).get("targets", [])
    assert len(targets) == 1
    assert "package k8srequiredlabels" in targets[0]["rego"]

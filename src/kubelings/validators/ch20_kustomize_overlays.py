"""
Validators for Chapter 20: Declarative Customization with Kustomize
"""

from typing import Any, Dict

import yaml

from kubelings.validators import register_validator


def get_kustomization_base() -> Dict[str, Any]:
    manifest_yaml = "\napiVersion: kustomize.config.k8s.io/v1beta1\nkind: Kustomization\nresources:\n  - deployment.yaml\n  - service.yaml\nnamespace: ecommerce-core\nnamePrefix: core-\ncommonLabels:\n  app.kubernetes.io/managed-by: kustomize\n  tier: backend\ncommonAnnotations:\n  team: platform\n"
    return yaml.safe_load(manifest_yaml)


@register_validator("kustomize01")
def validate_kustomize01(manifest: Any, raw_yaml: str = "") -> None:
    base = manifest
    assert base.get("apiVersion") == "kustomize.config.k8s.io/v1beta1"
    assert base.get("kind") == "Kustomization"
    assert "deployment.yaml" in base.get("resources", [])
    assert "service.yaml" in base.get("resources", [])
    assert base.get("namespace") == "ecommerce-core"
    assert base.get("namePrefix") == "core-"
    assert base.get("commonLabels", {}).get("app.kubernetes.io/managed-by") == "kustomize"
    assert base.get("commonLabels", {}).get("tier") == "backend"
    assert base.get("commonAnnotations", {}).get("team") == "platform"


def get_generator_kustomization() -> Dict[str, Any]:
    manifest_yaml = "\napiVersion: kustomize.config.k8s.io/v1beta1\nkind: Kustomization\nconfigMapGenerator:\n  - name: app-config\n    literals:\n      - LOG_LEVEL=info\n      - FEATURE_FLAGS=beta\nsecretGenerator:\n  - name: api-secret\n    literals:\n      - API_KEY=supersecretkey123\n    type: Opaque\ngeneratorOptions:\n  disableNameSuffixHash: false\n  labels:\n    generated-by: kustomize\n"
    return yaml.safe_load(manifest_yaml)


@register_validator("kustomize02")
def validate_kustomize02(manifest: Any, raw_yaml: str = "") -> None:
    kust = manifest
    assert kust.get("apiVersion") == "kustomize.config.k8s.io/v1beta1"
    assert kust.get("kind") == "Kustomization"
    cm_gens = kust.get("configMapGenerator", [])
    assert len(cm_gens) == 1
    assert cm_gens[0].get("name") == "app-config"
    assert "LOG_LEVEL=info" in cm_gens[0].get("literals", [])
    sec_gens = kust.get("secretGenerator", [])
    assert len(sec_gens) == 1
    assert sec_gens[0].get("name") == "api-secret"
    assert "API_KEY=supersecretkey123" in sec_gens[0].get("literals", [])
    assert sec_gens[0].get("type") == "Opaque"
    gen_opts = kust.get("generatorOptions", {})
    assert gen_opts.get("disableNameSuffixHash") is False
    assert gen_opts.get("labels", {}).get("generated-by") == "kustomize"


def get_patch_kustomization() -> Dict[str, Any]:
    manifest_yaml = "\napiVersion: kustomize.config.k8s.io/v1beta1\nkind: Kustomization\nresources:\n  - ../../base\npatches:\n  - target:\n      group: apps\n      version: v1\n      kind: Deployment\n      name: webapp\n    patch: |-\n      - op: replace\n        path: /spec/replicas\n        value: 5\n      - op: add\n        path: /spec/template/spec/containers/0/resources/limits/cpu\n        value: 500m\n"
    return yaml.safe_load(manifest_yaml)


@register_validator("kustomize03")
def validate_kustomize03(manifest: Any, raw_yaml: str = "") -> None:
    kust = manifest
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


def get_prod_overlay() -> Dict[str, Any]:
    manifest_yaml = "\napiVersion: kustomize.config.k8s.io/v1beta1\nkind: Kustomization\nresources:\n  - ../../base\nnamespace: production\nnamePrefix: prod-\nimages:\n  - name: webapp\n    newName: quay.io/company/webapp\n    newTag: v3.1.0\nreplicas:\n  - name: webapp\n    count: 10\n"
    return yaml.safe_load(manifest_yaml)


@register_validator("kustomize04")
def validate_kustomize04(manifest: Any, raw_yaml: str = "") -> None:
    overlay = manifest
    assert overlay.get("apiVersion") == "kustomize.config.k8s.io/v1beta1"
    assert "../../base" in overlay.get("resources", [])
    assert overlay.get("namespace") == "production"
    assert overlay.get("namePrefix") == "prod-"
    images = overlay.get("images", [])
    assert len(images) == 1
    assert images[0].get("name") == "webapp"
    assert images[0].get("newName") == "quay.io/company/webapp"
    assert images[0].get("newTag") == "v3.1.0"
    replicas = overlay.get("replicas", [])
    assert len(replicas) == 1
    assert replicas[0].get("name") == "webapp"
    assert replicas[0].get("count") == 10

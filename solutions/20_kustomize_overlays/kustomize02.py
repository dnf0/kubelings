"""
Chapter 20: Declarative Customization with Kustomize
Exercise 20.2: Kustomize ConfigMap & Secret Generators (Solution)
"""

from typing import Any, Dict

import yaml


def get_generator_kustomization() -> Dict[str, Any]:
    manifest_yaml = """
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
configMapGenerator:
  - name: app-config
    literals:
      - LOG_LEVEL=info
      - FEATURE_FLAGS=beta
secretGenerator:
  - name: api-secret
    literals:
      - API_KEY=supersecretkey123
    type: Opaque
generatorOptions:
  disableNameSuffixHash: false
  labels:
    generated-by: kustomize
"""
    return yaml.safe_load(manifest_yaml)


if __name__ == "__main__":
    kust = get_generator_kustomization()
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
    print("✓ Kustomize generators validation passed!")

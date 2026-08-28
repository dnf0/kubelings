"""
Chapter 20: Declarative Customization with Kustomize
Exercise 20.2: Kustomize ConfigMap & Secret Generators

Context & Why:
In vanilla Kubernetes, modifying a ConfigMap or Secret in-place does not trigger a rollout
of referencing Deployments or DaemonSets. As a result, running Pods retain stale in-memory
configurations, leading to confusing bugs and configuration drift across replicas.

Kustomize solves this using `configMapGenerator` and `secretGenerator`. By default, Kustomize
computes a cryptographic hash of the generated configuration contents and appends it as a suffix
to the resource name (e.g. `app-config-g8h6m5f778`). It also updates all Deployment environment
and volume references to point to the new suffixed name. When configuration changes, the name
changes, guaranteeing an automatic rolling restart of dependent workloads. Ensuring
`generatorOptions.disableNameSuffixHash: False` preserves this immutable release pattern.

Task: Construct a kustomization.yaml manifest utilizing configMapGenerator and secretGenerator.
Requirements:
- apiVersion: 'kustomize.config.k8s.io/v1beta1'
- kind: 'Kustomization'
- configMapGenerator:
    - name: 'app-config'
    - literals: ['LOG_LEVEL=info', 'FEATURE_FLAGS=beta']
- secretGenerator:
    - name: 'api-secret'
    - literals: ['API_KEY=supersecretkey123']
    - type: 'Opaque'
- generatorOptions:
    disableNameSuffixHash: False
    labels:
        generated-by: 'kustomize'
"""

from typing import Any, Dict

import yaml


def get_generator_kustomization() -> Dict[str, Any]:
    manifest_yaml = """
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
"""
    # TODO: Update manifest_yaml with the configMapGenerator, secretGenerator, and generatorOptions, returning the parsed dictionary (e.g., via yaml.safe_load).
    # WHY: Kustomize generators compute cryptographic content hash suffixes that force rolling restarts of referencing
    #      workloads whenever configuration changes, eliminating silent configuration drift.
    return {}


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

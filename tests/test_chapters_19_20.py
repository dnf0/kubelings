"""Tests for Chapter 19 (Helm Packaging) & Chapter 20 (Kustomize Overlays)."""

from pathlib import Path

import jsonschema
import yaml

from kubelings.manifest import get_exercise_by_name, get_manifest


def test_manifest_20_chapters_and_90_exercises():
    manifest = get_manifest()
    assert len(manifest.chapters) >= 20
    assert len(manifest.all_exercises) >= 90


def test_chapter_19_manifest_structure():
    manifest = get_manifest()
    ch19 = next((c for c in manifest.chapters if c.number == 19), None)
    assert ch19 is not None
    assert ch19.name == "19_helm_packaging"
    assert len(ch19.exercises) == 4
    for ex_name in ["helm01", "helm02", "helm03", "helm04"]:
        ex = get_exercise_by_name(ex_name)
        assert ex is not None
        assert ex.chapter_name == "19_helm_packaging"


def test_chapter_20_manifest_structure():
    manifest = get_manifest()
    ch20 = next((c for c in manifest.chapters if c.number == 20), None)
    assert ch20 is not None
    assert ch20.name == "20_kustomize_overlays"
    assert len(ch20.exercises) == 4
    for ex_name in ["kustomize01", "kustomize02", "kustomize03", "kustomize04"]:
        ex = get_exercise_by_name(ex_name)
        assert ex is not None
        assert ex.chapter_name == "20_kustomize_overlays"


def test_helm01_chart_metadata():
    meta = yaml.safe_load(
        Path("solutions/19_helm_packaging/helm01.yaml").read_text(encoding="utf-8")
    )
    assert meta["apiVersion"] == "v2"
    assert meta["name"] == "webapp-chart"
    assert meta["version"] == "1.2.0"
    assert meta["appVersion"] == "2.4.1"
    assert len(meta["dependencies"]) == 1
    dep = meta["dependencies"][0]
    assert dep["name"] == "redis"
    assert dep["version"] == "17.3.0"
    assert dep["condition"] == "redis.enabled"


def test_helm02_named_templates():
    dep = yaml.safe_load(
        Path("solutions/19_helm_packaging/helm02.yaml").read_text(encoding="utf-8")
    )
    assert dep["apiVersion"] == "apps/v1"
    assert dep["kind"] == "Deployment"
    assert dep["metadata"]["name"] == "prod-web"
    assert dep["spec"]["replicas"] == 3
    assert dep["spec"]["template"]["spec"]["containers"][0]["image"] == "nginx:1.25-alpine"
    assert dep["spec"]["template"]["spec"]["containers"][0]["ports"][0]["containerPort"] == 8080


def test_helm03_values_schema():
    schema = yaml.safe_load(
        Path("solutions/19_helm_packaging/helm03.yaml").read_text(encoding="utf-8")
    )
    assert schema["$schema"] == "http://json-schema.org/draft-07/schema#"
    assert "replicaCount" in schema["required"]
    assert "image" in schema["required"]
    assert "service" in schema["required"]

    valid_values = {
        "replicaCount": 2,
        "image": {"repository": "myrepo/app", "tag": "v1.0"},
        "service": {"type": "ClusterIP", "port": 80},
    }
    jsonschema.validate(instance=valid_values, schema=schema)


def test_helm04_subcharts_and_globals():
    values = yaml.safe_load(
        Path("solutions/19_helm_packaging/helm04.yaml").read_text(encoding="utf-8")
    )
    assert values["global"]["environment"] == "production"
    assert values["global"]["registry"] == "registry.k8s.io"
    assert values["redis"]["architecture"] == "replication"
    assert values["redis"]["auth"]["enabled"] is True
    assert values["postgresql"]["enabled"] is False


def test_kustomize01_base():
    base = yaml.safe_load(
        Path("solutions/20_kustomize_overlays/kustomize01.yaml").read_text(encoding="utf-8")
    )
    assert base["apiVersion"] == "kustomize.config.k8s.io/v1beta1"
    assert base["kind"] == "Kustomization"
    assert "deployment.yaml" in base["resources"]
    assert base["namespace"] == "ecommerce-core"
    assert base["namePrefix"] == "core-"
    assert base["commonLabels"]["app.kubernetes.io/managed-by"] == "kustomize"


def test_kustomize02_generators():
    kust = yaml.safe_load(
        Path("solutions/20_kustomize_overlays/kustomize02.yaml").read_text(encoding="utf-8")
    )
    assert kust["apiVersion"] == "kustomize.config.k8s.io/v1beta1"
    assert kust["kind"] == "Kustomization"
    assert len(kust["configMapGenerator"]) == 1
    assert kust["configMapGenerator"][0]["name"] == "app-config"
    assert len(kust["secretGenerator"]) == 1
    assert kust["secretGenerator"][0]["name"] == "api-secret"
    assert kust["generatorOptions"]["disableNameSuffixHash"] is False


def test_kustomize03_patches():
    kust = yaml.safe_load(
        Path("solutions/20_kustomize_overlays/kustomize03.yaml").read_text(encoding="utf-8")
    )
    assert kust["apiVersion"] == "kustomize.config.k8s.io/v1beta1"
    assert "../../base" in kust["resources"]
    assert len(kust["patches"]) == 1
    target = kust["patches"][0]["target"]
    assert target["kind"] == "Deployment"
    assert target["name"] == "webapp"


def test_kustomize04_prod_overlay():
    overlay = yaml.safe_load(
        Path("solutions/20_kustomize_overlays/kustomize04.yaml").read_text(encoding="utf-8")
    )
    assert overlay["apiVersion"] == "kustomize.config.k8s.io/v1beta1"
    assert "../../base" in overlay["resources"]
    assert overlay["namespace"] == "production"
    assert overlay["namePrefix"] == "prod-"
    assert overlay["images"][0]["name"] == "webapp"
    assert overlay["images"][0]["newTag"] == "v3.1.0"
    assert overlay["replicas"][0]["count"] == 10

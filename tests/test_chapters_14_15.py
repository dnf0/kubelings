import pytest
from kubelings.manifest import get_manifest, get_exercise_by_name


def test_expanded_chapters_count():
    manifest = get_manifest()
    assert len(manifest.chapters) == 15
    assert len(manifest.all_exercises) == 70


def test_chapter_14_gitops_structure():
    manifest = get_manifest()
    ch14 = next((c for c in manifest.chapters if c.number == 14), None)
    assert ch14 is not None
    assert ch14.name == "14_gitops_argocd"
    assert len(ch14.exercises) == 4
    for ex_name in ["gitops01", "gitops02", "gitops03", "gitops04"]:
        ex = get_exercise_by_name(ex_name)
        assert ex is not None
        assert ex.chapter_name == "14_gitops_argocd"


def test_chapter_15_service_mesh_structure():
    manifest = get_manifest()
    ch15 = next((c for c in manifest.chapters if c.number == 15), None)
    assert ch15 is not None
    assert ch15.name == "15_service_mesh_cilium"
    assert len(ch15.exercises) == 4
    for ex_name in ["mesh01", "mesh02", "mesh03", "mesh04"]:
        ex = get_exercise_by_name(ex_name)
        assert ex is not None
        assert ex.chapter_name == "15_service_mesh_cilium"

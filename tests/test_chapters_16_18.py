"""Tests for Curriculum Chapters 16, 17, and 18."""

from kubelings.manifest import get_exercise_by_name, get_manifest


def test_manifest_chapters_16_18_count():
    manifest = get_manifest()
    assert len(manifest.chapters) == 18
    assert len(manifest.all_exercises) == 82


def test_chapter_16_policy_as_code():
    manifest = get_manifest()
    ch16 = next(c for c in manifest.chapters if c.number == 16)
    assert ch16.name == "16_policy_as_code"
    assert len(ch16.exercises) == 4
    ex_names = [e.name for e in ch16.exercises]
    assert ex_names == ["policy01", "policy02", "policy03", "policy04"]


def test_chapter_17_multitenancy():
    manifest = get_manifest()
    ch17 = next(c for c in manifest.chapters if c.number == 17)
    assert ch17.name == "17_multitenancy_vcluster"
    assert len(ch17.exercises) == 4
    ex_names = [e.name for e in ch17.exercises]
    assert ex_names == ["tenant01", "tenant02", "tenant03", "tenant04"]


def test_chapter_18_admission_webhooks():
    manifest = get_manifest()
    ch18 = next(c for c in manifest.chapters if c.number == 18)
    assert ch18.name == "18_admission_webhooks"
    assert len(ch18.exercises) == 4
    ex_names = [e.name for e in ch18.exercises]
    assert ex_names == ["webhook01", "webhook02", "webhook03", "webhook04"]


def test_exercise_lookup_chapters_16_18():
    assert get_exercise_by_name("policy01") is not None
    assert get_exercise_by_name("tenant02") is not None
    assert get_exercise_by_name("webhook04") is not None

from pathlib import Path

from kubelings.manifest import get_exercise_by_name, get_manifest, get_next_exercise
from kubelings.models import Exercise, ExerciseStatus


def test_exercise_status_enum():
    assert ExerciseStatus.NOT_STARTED == "not_started"
    assert ExerciseStatus.IN_PROGRESS == "in_progress"
    assert ExerciseStatus.COMPLETED == "completed"
    assert ExerciseStatus.FAILED == "failed"


def test_exercise_dataclass_properties():
    ex = Exercise(
        name="pods01",
        title="First Pod Manifest & Spec",
        path="exercises/01_pods/pods01.yaml",
        chapter_name="01_pods",
        hints=["Hint 1", "Hint 2"],
        requires_cluster=False,
    )
    assert ex.file_path == Path("exercises/01_pods/pods01.yaml")
    assert ex.solution_path == Path("solutions/01_pods/pods01.yaml")
    assert ex.requires_cluster is False


def test_manifest_loads_all_chapters():
    manifest = get_manifest()
    assert len(manifest.chapters) == 26
    assert len(manifest.all_exercises) == 114

    first = manifest.all_exercises[0]
    assert first.name == "pods01"
    assert first.chapter_name == "01_pods"
    assert first.path == "exercises/01_pods/pods01.yaml"

    last = manifest.all_exercises[-1]
    assert last.name == "accel04"
    assert last.chapter_name == "26_hardware_acceleration_dra"


def test_all_26_chapters_structure():
    manifest = get_manifest()
    expected_chapters = [
        (1, "01_pods", 6),
        (2, "02_controllers", 6),
        (3, "03_config_secrets", 5),
        (4, "04_storage", 5),
        (5, "05_services_networking", 5),
        (6, "06_ingress_gateway", 4),
        (7, "07_scheduling", 5),
        (8, "08_security_rbac", 5),
        (9, "09_network_policies", 4),
        (10, "10_lifecycle_probes", 4),
        (11, "11_autoscaling", 4),
        (12, "12_crds_and_operators", 4),
        (13, "13_troubleshooting", 5),
        (14, "14_gitops_argocd", 4),
        (15, "15_service_mesh_cilium", 4),
        (16, "16_policy_as_code", 4),
        (17, "17_multitenancy_vcluster", 4),
        (18, "18_admission_webhooks", 4),
        (19, "19_helm_packaging", 4),
        (20, "20_kustomize_overlays", 4),
        (21, "21_gateway_api", 4),
        (22, "22_crossplane_iac", 4),
        (23, "23_ebpf_tetragon", 4),
        (24, "24_kuberay_ml", 4),
        (25, "25_batch_kueue_volcano", 4),
        (26, "26_hardware_acceleration_dra", 4),
    ]

    for number, name, count in expected_chapters:
        ch = manifest.chapters[number - 1]
        assert ch.number == number
        assert ch.name == name
        assert bool(ch.title)
        assert bool(ch.description)
        assert len(ch.exercises) == count
        for ex in ch.exercises:
            assert ex.chapter_name == name
            assert ex.name.isalnum()
            assert ex.path.startswith(f"exercises/{name}/")
            assert ex.path.endswith(".yaml")
            assert len(ex.hints) >= 2, f"Exercise {ex.name} should have at least 2 hints"
            assert all(isinstance(h, str) and len(h) > 0 for h in ex.hints)


def test_get_exercise_by_name():
    ex = get_exercise_by_name("pods01")
    assert ex is not None
    assert ex.name == "pods01"
    assert ex.path == "exercises/01_pods/pods01.yaml"

    # Test by relative path
    ex_by_path = get_exercise_by_name("exercises/01_pods/pods01.yaml")
    assert ex_by_path is not None
    assert ex_by_path.name == "pods01"

    # Test by filename
    ex_by_file = get_exercise_by_name("pods01.yaml")
    assert ex_by_file is not None
    assert ex_by_file.name == "pods01"

    # Test not found
    assert get_exercise_by_name("nonexistent") is None


def test_get_next_exercise():
    next_ex = get_next_exercise("pods01")
    assert next_ex is not None
    assert next_ex.name == "pods02"

    # Test next exercise across chapter boundary
    # pods06 -> ctrl01
    next_across = get_next_exercise("pods06")
    assert next_across is not None
    assert next_across.name == "ctrl01"

    # Test next exercise across chapters
    next_across_v2 = get_next_exercise("webhook04")
    assert next_across_v2 is not None
    assert next_across_v2.name == "helm01"

    next_across_v3 = get_next_exercise("kustomize04")
    assert next_across_v3 is not None
    assert next_across_v3.name == "gateway01"

    next_across_v4 = get_next_exercise("tetragon04")
    assert next_across_v4 is not None
    assert next_across_v4.name == "ray01"

    next_across_v5 = get_next_exercise("ray04")
    assert next_across_v5 is not None
    assert next_across_v5.name == "kueue01"

    next_across_v6 = get_next_exercise("volcano02")
    assert next_across_v6 is not None
    assert next_across_v6.name == "accel01"

    # Test last exercise returns None
    assert get_next_exercise("accel04") is None

    # Test nonexistent exercise returns None
    assert get_next_exercise("nonexistent") is None


def test_manifest_singleton():
    m1 = get_manifest()
    m2 = get_manifest()
    assert m1 is m2

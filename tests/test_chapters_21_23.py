"""Tests for Chapter 21 (Gateway API), Chapter 22 (Crossplane IaC), and Chapter 23 (eBPF Tetragon)."""

from pathlib import Path

import pytest

from kubelings.manifest import get_exercise_by_name, get_manifest
from kubelings.models import Exercise
from kubelings.runner import ExerciseRunner
from kubelings.validators import load_all_validators

load_all_validators()


def test_manifest_23_chapters_and_102_exercises():
    manifest = get_manifest()
    assert len(manifest.chapters) >= 23
    assert len(manifest.all_exercises) >= 102


def test_chapter_21_manifest_structure():
    manifest = get_manifest()
    ch21 = next((c for c in manifest.chapters if c.number == 21), None)
    assert ch21 is not None
    assert ch21.name == "21_gateway_api"
    assert len(ch21.exercises) == 4
    for ex_name in ["gateway01", "gateway02", "gateway03", "gateway04"]:
        ex = get_exercise_by_name(ex_name)
        assert ex is not None
        assert ex.chapter_name == "21_gateway_api"


def test_chapter_22_manifest_structure():
    manifest = get_manifest()
    ch22 = next((c for c in manifest.chapters if c.number == 22), None)
    assert ch22 is not None
    assert ch22.name == "22_crossplane_iac"
    assert len(ch22.exercises) == 4
    for ex_name in ["crossplane01", "crossplane02", "crossplane03", "crossplane04"]:
        ex = get_exercise_by_name(ex_name)
        assert ex is not None
        assert ex.chapter_name == "22_crossplane_iac"


def test_chapter_23_manifest_structure():
    manifest = get_manifest()
    ch23 = next((c for c in manifest.chapters if c.number == 23), None)
    assert ch23 is not None
    assert ch23.name == "23_ebpf_tetragon"
    assert len(ch23.exercises) == 4
    for ex_name in ["tetragon01", "tetragon02", "tetragon03", "tetragon04"]:
        ex = get_exercise_by_name(ex_name)
        assert ex is not None
        assert ex.chapter_name == "23_ebpf_tetragon"


@pytest.mark.parametrize("ex_name", ["gateway01", "gateway02", "gateway03", "gateway04"])
def test_gateway_solutions(ex_name: str):
    sol_path = Path(f"solutions/21_gateway_api/{ex_name}.yaml")
    assert sol_path.exists(), f"Solution missing: {sol_path}"
    ex = Exercise(name=ex_name, title=ex_name, path=str(sol_path), chapter_name="21_gateway_api")
    runner = ExerciseRunner()
    result = runner.run_exercise(ex)
    assert result.passed, f"Solution {sol_path} failed: {result.error}"


@pytest.mark.parametrize(
    "ex_name", ["crossplane01", "crossplane02", "crossplane03", "crossplane04"]
)
def test_crossplane_solutions(ex_name: str):
    sol_path = Path(f"solutions/22_crossplane_iac/{ex_name}.yaml")
    assert sol_path.exists(), f"Solution missing: {sol_path}"
    ex = Exercise(name=ex_name, title=ex_name, path=str(sol_path), chapter_name="22_crossplane_iac")
    runner = ExerciseRunner()
    result = runner.run_exercise(ex)
    assert result.passed, f"Solution {sol_path} failed: {result.error}"


@pytest.mark.parametrize("ex_name", ["tetragon01", "tetragon02", "tetragon03", "tetragon04"])
def test_tetragon_solutions(ex_name: str):
    sol_path = Path(f"solutions/23_ebpf_tetragon/{ex_name}.yaml")
    assert sol_path.exists(), f"Solution missing: {sol_path}"
    ex = Exercise(name=ex_name, title=ex_name, path=str(sol_path), chapter_name="23_ebpf_tetragon")
    runner = ExerciseRunner()
    result = runner.run_exercise(ex)
    assert result.passed, f"Solution {sol_path} failed: {result.error}"

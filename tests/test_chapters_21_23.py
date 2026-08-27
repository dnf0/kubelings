"""Tests for Chapter 21 (Gateway API), Chapter 22 (Crossplane IaC), and Chapter 23 (eBPF Tetragon)."""

import importlib.util
from pathlib import Path
from typing import Any

from kubelings.manifest import get_exercise_by_name, get_manifest


def _load_module_from_path(file_path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(file_path.stem, file_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_manifest_23_chapters_and_102_exercises():
    manifest = get_manifest()
    assert len(manifest.chapters) == 23
    assert len(manifest.all_exercises) == 102


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


def test_gateway01_solution():
    mod = _load_module_from_path(Path("solutions/21_gateway_api/gateway01.py"))
    mod.verify()


def test_gateway02_solution():
    mod = _load_module_from_path(Path("solutions/21_gateway_api/gateway02.py"))
    mod.verify()


def test_gateway03_solution():
    mod = _load_module_from_path(Path("solutions/21_gateway_api/gateway03.py"))
    mod.verify()


def test_gateway04_solution():
    mod = _load_module_from_path(Path("solutions/21_gateway_api/gateway04.py"))
    mod.verify()


def test_crossplane01_solution():
    mod = _load_module_from_path(Path("solutions/22_crossplane_iac/crossplane01.py"))
    mod.verify()


def test_crossplane02_solution():
    mod = _load_module_from_path(Path("solutions/22_crossplane_iac/crossplane02.py"))
    mod.verify()


def test_crossplane03_solution():
    mod = _load_module_from_path(Path("solutions/22_crossplane_iac/crossplane03.py"))
    mod.verify()


def test_crossplane04_solution():
    mod = _load_module_from_path(Path("solutions/22_crossplane_iac/crossplane04.py"))
    mod.verify()


def test_tetragon01_solution():
    mod = _load_module_from_path(Path("solutions/23_ebpf_tetragon/tetragon01.py"))
    mod.verify()


def test_tetragon02_solution():
    mod = _load_module_from_path(Path("solutions/23_ebpf_tetragon/tetragon02.py"))
    mod.verify()


def test_tetragon03_solution():
    mod = _load_module_from_path(Path("solutions/23_ebpf_tetragon/tetragon03.py"))
    mod.verify()


def test_tetragon04_solution():
    mod = _load_module_from_path(Path("solutions/23_ebpf_tetragon/tetragon04.py"))
    mod.verify()

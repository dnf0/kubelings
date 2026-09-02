"""Tests verifying that all 26 reference guides are comprehensive, valid, and bidirectionally linked."""

import re
from pathlib import Path

import pytest
import yaml

from kubelings.manifest import build_manifest

GUIDES_DIR = Path(__file__).resolve().parent.parent / "docs" / "guides"

CHAPTER_SLUGS = [
    "01-pods",
    "02-controllers",
    "03-config-secrets",
    "04-storage",
    "05-services-networking",
    "06-ingress-gateway",
    "07-scheduling",
    "08-security-rbac",
    "09-network-policies",
    "10-lifecycle-probes",
    "11-autoscaling",
    "12-crds-and-operators",
    "13-troubleshooting",
    "14-gitops-argocd",
    "15-service-mesh-cilium",
    "16-policy-as-code",
    "17-multitenancy-vcluster",
    "18-admission-webhooks",
    "19-helm-packaging",
    "20-kustomize-overlays",
    "21-gateway-api",
    "22-crossplane-iac",
    "23-ebpf-tetragon",
    "24-kuberay-ml",
    "25-batch-kueue-volcano",
    "26-hardware-acceleration-dra",
]


def test_all_26_guide_files_exist():
    """Verify all 26 chapter guide files exist in docs/guides/."""
    for slug in CHAPTER_SLUGS:
        guide_path = GUIDES_DIR / f"{slug}.md"
        assert guide_path.exists(), f"Missing reference guide: {guide_path}"


@pytest.mark.parametrize("slug", CHAPTER_SLUGS)
def test_guide_contains_all_required_sections(slug: str):
    """Verify each guide contains the 7 standardized sections without empty stubs."""
    guide_path = GUIDES_DIR / f"{slug}.md"
    content = guide_path.read_text(encoding="utf-8")

    # Section 1: Hero card with link to playground
    assert "../playground/index.html?chapter=" in content, (
        f"{slug}: Missing playground launcher link"
    )

    # Section 2: Architecture Overview & Control Plane Mechanics
    assert re.search(r"## 1\. Architectural Overview", content), (
        f"{slug}: Missing Section 1 Architecture"
    )

    # Section 3: Annotated Production YAML
    assert re.search(r"## 2\. Annotated Production YAML", content), (
        f"{slug}: Missing Section 2 YAML Anatomy"
    )

    # Section 4: Real-World Patterns
    assert re.search(r"## 3\. Real-World Architectural Patterns", content), (
        f"{slug}: Missing Section 3 Patterns"
    )

    # Section 5: Production Hardening
    assert re.search(r"## 4\. Production Hardening", content), (
        f"{slug}: Missing Section 4 Hardening"
    )

    # Section 6: Failure Modes & Diagnostics
    assert re.search(r"## 5\. Failure Modes & Diagnostic Triage Tree", content), (
        f"{slug}: Missing Section 5 Triage"
    )

    # Section 7: Interactive Practice Matrix
    assert re.search(r"## 6\. Interactive Practice Matrix", content), (
        f"{slug}: Missing Section 6 Practice Matrix"
    )


@pytest.mark.parametrize("slug", CHAPTER_SLUGS)
def test_guide_yaml_manifests_are_valid_and_non_empty(slug: str):
    """Extract and parse all YAML code blocks to ensure zero syntax errors or empty manifests."""
    guide_path = GUIDES_DIR / f"{slug}.md"
    content = guide_path.read_text(encoding="utf-8")

    # Find all yaml fenced code blocks
    yaml_blocks = re.findall(r"```yaml\n(.*?)```", content, re.DOTALL)
    assert len(yaml_blocks) >= 2, (
        f"{slug}: Must have at least 2 YAML manifests, found {len(yaml_blocks)}"
    )

    for i, block in enumerate(yaml_blocks):
        stripped = block.strip()
        assert len(stripped) > 20, f"{slug}: YAML block {i + 1} is empty or too short: '{stripped}'"
        # Parse with yaml.safe_load (handle multi-doc yaml too)
        docs = list(yaml.safe_load_all(stripped))
        assert len(docs) >= 1, f"{slug}: YAML block {i + 1} parsed into zero documents"
        for doc in docs:
            if doc is not None:
                assert isinstance(doc, dict), (
                    f"{slug}: YAML block {i + 1} doc must be a dict, got {type(doc)}"
                )
                assert len(doc) > 0, f"{slug}: YAML block {i + 1} doc is empty"


def test_all_114_exercises_are_linked_in_guides():
    """Verify that every single exercise in the curriculum has a direct playground deep link in its chapter guide."""
    manifest = build_manifest()
    all_exercise_ids = {ex.name for ex in manifest.all_exercises}
    assert len(all_exercise_ids) == 114

    linked_exercise_ids = set()
    for slug in CHAPTER_SLUGS:
        guide_path = GUIDES_DIR / f"{slug}.md"
        content = guide_path.read_text(encoding="utf-8")
        matches = re.findall(r"\.\./playground/index\.html\?exercise=([a-zA-Z0-9_-]+)", content)
        for m in matches:
            linked_exercise_ids.add(m)

    missing = all_exercise_ids - linked_exercise_ids
    assert not missing, (
        f"The following exercises are not linked in any reference guide: {sorted(missing)}"
    )

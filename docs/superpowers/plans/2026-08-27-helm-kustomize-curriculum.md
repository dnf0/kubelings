# Helm & Kustomize Curriculum Track (Chapters 19 & 20) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add Chapter 19 (Helm Packaging) and Chapter 20 (Kustomize Overlays) with 8 new exercises, expanding Kubelings to 20 chapters and 90 total exercises.

**Architecture:** Implement offline exercise evaluators in Python using YAML parsing and JSON Schema validation for Helm chart manifests, Go template helpers, values validation schemas, and Kustomize overlays. Register chapters in curriculum manifest and update tests and documentation.

**Tech Stack:** Python 3.10+, PyYAML, jsonschema, pytest, rich, typer, mkdocs-material.

---

### Task 1: Chapter 19 (Helm Packaging) Exercises & Solutions
**Files:**
- Create: `exercises/19_helm_packaging/helm01.py` ... `helm04.py`
- Create: `solutions/19_helm_packaging/helm01.py` ... `helm04.py`

- [ ] **Step 1: Create starter exercises and reference solutions for helm01 to helm04**
- [ ] **Step 2: Commit Chapter 19 exercises and solutions**

---

### Task 2: Chapter 20 (Kustomize Overlays) Exercises & Solutions
**Files:**
- Create: `exercises/20_kustomize_overlays/kustomize01.py` ... `kustomize04.py`
- Create: `solutions/20_kustomize_overlays/kustomize01.py` ... `kustomize04.py`

- [ ] **Step 1: Create starter exercises and reference solutions for kustomize01 to kustomize04**
- [ ] **Step 2: Commit Chapter 20 exercises and solutions**

---

### Task 3: Update Manifest & Curriculum Engine
**Files:**
- Modify: `src/kubelings/manifest.py`

- [ ] **Step 1: Add Chapters 19 and 20 with exercise definitions and hints in manifest.py**
- [ ] **Step 2: Commit manifest updates**

---

### Task 4: Unit & Solution Testing for 90 Exercises
**Files:**
- Create: `tests/test_chapters_19_20.py`
- Modify: `tests/test_manifest.py`
- Modify: `tests/test_solutions_and_exercises.py`

- [ ] **Step 1: Write test_chapters_19_20.py and update assertions to 20 chapters / 90 exercises**
- [ ] **Step 2: Run pytest and verify 90/90 pass**
- [ ] **Step 3: Commit test suite updates**

---

### Task 5: Documentation & Syllabus Updates
**Files:**
- Modify: `README.md`
- Modify: `docs/syllabus.md`
- Modify: `docs/index.md`

- [ ] **Step 1: Update README and documentation pages with 20 chapters and 90 exercises**
- [ ] **Step 2: Rebuild demo SVG and test MkDocs build**
- [ ] **Step 3: Commit documentation updates**

---

### Task 6: Final Verification, Knowledge Graph Rebuild & Release
- [ ] **Step 1: Run ruff check, ruff format, pyright, pytest, and kubelings test**
- [ ] **Step 2: Run graphify update . to rebuild knowledge graph**
- [ ] **Step 3: Push to remote main and monitor CI/CD release**

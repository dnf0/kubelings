# Design Specification: Helm & Kustomize Curriculum Track (Chapters 19 & 20)

## 1. Overview & Objectives

Kubelings currently features 18 chapters and 82 exercises. This track expands the curriculum with **8 new exercises** covering production-grade declarative packaging, templating, and configuration management:
- **Chapter 19: Package Management with Helm** (`19_helm_packaging` / `helm01` - `helm04`)
- **Chapter 20: Declarative Customization with Kustomize** (`20_kustomize_overlays` / `kustomize01` - `kustomize04`)

Total curriculum expands to **20 Chapters** and **90 Exercises**.

---

## 2. Curriculum Breakdown

### Chapter 19: Package Management with Helm (`19_helm_packaging`)
1. `helm01`: **`Chart.yaml` Metadata & Dependencies**
   - Goal: Build valid Helm v3 chart metadata specifications (`apiVersion: v2`, semver `version`, `appVersion`, `description`, `dependencies` with condition toggles).
2. `helm02`: **Go Templating & `_helpers.tpl` Named Templates**
   - Goal: Construct standardized Helm helper templates (`define "mychart.fullname"`, `include`, `quote`, `toYaml`, `nindent 4`) and render deployment templates with dynamic release names and labels.
3. `helm03`: **`values.schema.json` Validation Schema**
   - Goal: Author a strict JSONSchema Draft-7 definition validating `values.yaml` inputs (e.g., `replicaCount` bounds, required `image.repository`, port constraints).
4. `helm04`: **Subcharts, Global Values & Library Templates**
   - Goal: Configure parent chart with child subcharts, passing global variables (`global.environment`, `global.imageRegistry`) and applying subchart value overrides.

---

### Chapter 20: Declarative Customization with Kustomize (`20_kustomize_overlays`)
1. `kustomize01`: **`kustomization.yaml` Base Manifests & Metadata Transformations**
   - Goal: Author standard `kustomization.yaml` bases applying `resources`, `namespace`, `namePrefix`, `commonLabels`, and `commonAnnotations`.
2. `kustomize02`: **ConfigMap & Secret Generators**
   - Goal: Use `configMapGenerator` and `secretGenerator` with `literals`, `files`, and `options.disableNameSuffixHash` to enforce immutable deployment rollouts.
3. `kustomize03`: **Strategic Merge Patches & JSON6902 Target Patches**
   - Goal: Apply granular patches to base resources using both inline strategic merge diffs and RFC 6902 JSON patch operations (`op: replace`, `op: add`).
4. `kustomize04`: **Multi-Environment Overlays (`dev` / `staging` / `prod`)**
   - Goal: Structure multi-environment overlays referencing shared bases with customized replica counts, resource limit adjustments, and image tag overrides.

---

## 3. Evaluation & Validation Architecture

- **In-Memory Offline Engine**:
  - Exercises construct valid dictionary representations or template strings that are verified for structural correctness, schema conformance, and rendering logic.
  - Zero external CLI requirements: works 100% offline in sub-millisecond execution loops.
- **Manifest Integration**:
  - Registered in `src/kubelings/manifest.py`.
  - Full suite testing via `tests/test_chapters_19_20.py`, `tests/test_manifest.py`, and `tests/test_solutions_and_exercises.py`.

---

## 4. Verification & Release Gate
1. `pytest` unit & integration tests covering all 90 exercises.
2. `kubelings test` confirming `90/90` solutions pass.
3. `ruff` & `pyright` passing with zero warnings.
4. `graphify update .` knowledge graph rebuild.
5. Push to GitHub, triggering CI, MkDocs doc build, and Semantic Release (`v0.4.0`).

# Kubelings Onboarding Experience & Guided Tour Specification

**Date:** 2026-08-27  
**Status:** Approved  
**Author:** Antigravity Pairing Assistant & Daniel Fisher  

---

## 1. Executive Summary

Kubelings teaches Kubernetes from the ground up through test-driven micro-exercises. To help new learners get started quickly without friction, this specification defines a **Unified Onboarding Suite**:
1. **Interactive CLI Tour (`kubelings tour`)**: A rich 5-step terminal walkthrough with live environment checks, workflow explanation, and an interactive first exercise resolution.
2. **VS Code & Cursor Walkthrough**: A declarative in-editor walkthrough (`contributes.walkthroughs`) guiding users through curriculum browsing, cluster checks, and on-save diagnostics.
3. **Comprehensive Documentation Guide (`docs/onboarding-guide.md`)**: A polished, visual onboarding guide and tutorial integrated into the documentation suite.

---

## 2. Architecture & Components

```
+-------------------------------------------------------------------------+
|                        Unified Onboarding Suite                         |
+------------------------------------+------------------------------------+
                                     |
         +---------------------------+---------------------------+
         |                                                       |
         v                                                       v
+-----------------------------+                         +-----------------------------+
|    CLI Tour (`tour.py`)     |                         |  VS Code Editor Walkthrough |
|  - 5 Interactive Steps      |                         |  - `contributes.walkthrough`|
|  - Rich Panels & Syntax     |                         |  - Action Buttons & Links   |
|  - Cluster Live Check       |                         |  - In-Editor Diagnostics    |
|  - Live pods01 Evaluation   |                         |  - Quick Fix Demonstrations |
+--------------+--------------+                         +--------------+--------------+
               |                                                       |
               +---------------------------+---------------------------+
                                           |
                                           v
                        +-------------------------------------+
                        |     Docs & Educational Guides       |
                        |   - `docs/onboarding-guide.md`      |
                        |   - `README.md` & CLI Reference     |
                        +-------------------------------------+
```

---

## 3. CLI Guided Tour (`kubelings tour`)

### 3.1 CLI Interface & Options
```bash
kubelings tour [OPTIONS]
```

**Options:**
- `--step`, `-s` `INTEGER`: Jump directly to a specific step (1 to 5).
- `--non-interactive`: Run through all steps sequentially without waiting for keypresses (useful for automated testing and CI demos).
- `--json`: Output step descriptions and status in structured JSON.

### 3.2 The 5 Tour Steps

#### Step 1: Welcome & Pedagogical Philosophy
- Displays ASCII Kubelings logo.
- Explains the core philosophy:
  - Active debugging: Every exercise starts in an intentionally incomplete/broken state.
  - Sub-30ms instant feedback: Schema and spec validation happens locally in memory.
  - Test-driven mastery: Code passes only when all Kubernetes assertions succeed.

#### Step 2: Environment & Cluster Verification
- Performs live verification:
  - Python version & virtual environment health.
  - Local exercises workspace integrity (`exercises/` directory with 23 chapters).
  - Kubernetes cluster detection via `ClusterDetector`:
    - If local/remote cluster found: displays active context name and nodes.
    - If no cluster found: confirms offline validation mode is 100% active and ready.

#### Step 3: The Kubelings Workflow & Hotkeys
- Explains the continuous iteration loop:
  - 1. Open exercise file in your editor (e.g. `exercises/01_pods/pods01.py`).
  - 2. Read `# TODO:` instructions and schema requirements.
  - 3. Edit and save the file.
  - 4. Automated file watcher tests your code in `< 30ms`.
- Explains interactive terminal hotkeys:
  - `[n]` / `[Enter]`: Next exercise.
  - `[p]`: Previous exercise.
  - `[h]`: Reveal progressive hint tier.
  - `[r]`: Rerun evaluation.
  - `[l]`: Show syllabus overview.
  - `[q]`: Quit watch loop.

#### Step 4: Guided First Exercise (`pods01`) Walkthrough
- Previews the first exercise `exercises/01_pods/pods01.py`.
- Evaluates `pods01` live using `ExerciseRunner` and shows the real error message.
- Explains what's missing: adding `labels: {app: web}` and `ports: [{containerPort: 80}]` to the Pod specification.
- Displays the solution diff comparing starter code to reference solution.
- Confirms the student is ready to edit the file.

#### Step 5: IDE Tooling & Next Steps
- Recommends the VS Code extension for inline error squiggles and quick fixes.
- Presents final action prompt:
  - Press `[Enter]` to immediately launch `kubelings watch`.
  - Press `[q]` to return to shell.

---

## 4. VS Code & Cursor Extension Walkthrough

### 4.1 Walkthrough Registration (`package.json`)
Register `contributes.walkthroughs` in `extensions/vscode/package.json`:
- **ID**: `kubelings.walkthrough`
- **Title**: *Get Started with Kubelings ☸️*
- **Description**: *Master Kubernetes through hands-on, test-driven micro-exercises.*
- **Steps**:
  1. `welcome`: Overview & Curriculum structure -> Action: `[View Curriculum Syllabus]`.
  2. `cluster`: Cluster & Environment Check -> Action: `[Check Cluster Connectivity]`.
  3. `watch`: Terminal Watch Mode -> Action: `[Start Kubelings Watch]`.
  4. `first-exercise`: Solve First Exercise -> Action: `[Open pods01.py]`.
  5. `quickfixes`: Diagnostics & Quick Fixes -> Action: `[Run pods01 Verification]`.

### 4.2 Supporting Markdown & Assets
- Create markdown step definitions in `extensions/vscode/walkthrough/*.md`.
- Register `kubelings.openWalkthrough` command in `src/commands.ts`.
- Expose `cliBridge.tour()` in `src/cliBridge.ts`.

---

## 5. Documentation Suite Updates

### 5.1 New Document: `docs/onboarding-guide.md`
- Comprehensive illustrated walkthrough covering:
  - Installation and zero-install execution (`uvx kubelings tour`).
  - Terminal interactive tour experience.
  - VS Code extension walkthrough.
  - Solving the first Pod exercise step-by-step.
  - Learning roadmap from Pods to Controllers, Storage, RBAC, Operators, and Incident Troubleshooting.

### 5.2 Updated Existing Documents
- `README.md`: Highlight `kubelings tour` under Quickstart.
- `docs/index.md` & `docs/getting-started.md`: Add tour command and link to onboarding guide.
- `docs/cli-reference.md`: Add full reference for `kubelings tour`.

---

## 6. Verification & Quality Gates

### 6.1 Test Coverage Requirements
1. `tests/test_tour.py`:
   - Non-interactive execution runs through all 5 steps with exit code 0.
   - Specific step jumping (`kubelings tour --step 4`) works.
   - JSON output (`kubelings tour --json`) contains structured step metadata and verification status.
2. `extensions/vscode/test/walkthrough.test.ts`:
   - Command `kubelings.openWalkthrough` is registered and executable.
   - `cliBridge.tour()` method successfully retrieves tour metadata.
3. Full regression testing:
   - 489+ Python tests passing (`uv run pytest`).
   - 40+ TypeScript tests passing (`make vscode-test`).
   - Ruff linting and formatting clean (`uv run ruff check . && uv run ruff format --check .`).
   - Type check clean (`uv run pyright`).
   - VSIX extension package built (`make vscode-package`).

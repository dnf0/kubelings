# Kubelings WebAssembly (Pyodide) Browser Playground Design Specification

- **Date:** 2026-08-27
- **Status:** Approved
- **Target Release:** `v0.7.0`
- **Branch:** `feat/webassembly-playground`

---

## 1. Objective & Motivation

**Kubelings** currently provides terminal-based learning loops via `uvx kubelings tour` and `kubelings watch`, as well as a native VS Code / Cursor IDE extension.

To enable **zero-install, zero-friction discovery**, we are building the **Kubelings WebAssembly Browser Playground** embedded directly into the documentation site (`https://dnf0.github.io/kubelings/playground/`).

### Key Goals:
1. **Instant Client-Side Python & Kubernetes Validation**: Run Python 3.12 and the in-memory Kubelings schema validator in the browser via **Pyodide WebAssembly** in under 15ms per evaluation.
2. **VS Code-Grade Browser Editor**: Embed **Monaco Editor** with Python syntax highlighting, keyboard shortcuts (`Ctrl+Enter`), code folding, and automatic dark/light theme synchronization with MkDocs Material.
3. **Curated Flagship Exercise Showcase**: Provide an interactive dropdown to test 11 representative exercises spanning all 6 curriculum tiers (Pods, Controllers, Storage, Scheduling, Network Policies, Autoscaling, GitOps, Gateway API, KubeRay, and Apple Silicon GPU acceleration).
4. **Interactive Action Controls**:
   - **`▶ Run Solution`**: Evaluates active editor code in a background Web Worker and outputs colorized ANSI diagnostics.
   - **`↺ Reset Code`**: Restores the starter exercise code.
   - **`💡 Reveal Hint`**: Progressively reveals Hint Tiers (1 ➔ 2 ➔ 3).
   - **`🔍 Compare Solution`**: Opens a side-by-side Monaco Diff Editor comparing user code with the reference solution.
5. **Zero Maintenance & 100% Deterministic Parity**: Auto-generate the browser bundle JSON directly from repository sources (`src/kubelings/validator.py`, `exercises/`, `solutions/`, `manifest.py`) via a build script with pytest verification.

---

## 2. System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│ Browser Window / MkDocs Page (/playground/)                                             │
│                                                                                         │
│  ┌───────────────────────────────────────────────────────────────────────────────────┐  │
│  │ Navigation & Exercise Selector Header                                             │  │
│  │   [ Tier / Chapter Dropdown ]   [ Exercise Dropdown ]   [ 💡 Progressive Hint Bar ]│  │
│  └───────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                         │
│  ┌───────────────────────────────────────────────┬───────────────────────────────────┐  │
│  │ Monaco Editor Container                       │ Terminal / Diagnostic Output Pane │  │
│  │  • Python syntax highlighting                 │  • Colorized test pass/fail       │  │
│  │  • Keyboard shortcut: Ctrl+Enter / Cmd+Enter  │  • ANSI error rendering           │  │
│  │  • Action Bar: [▶ Run] [↺ Reset] [🔍 Diff]    │  • Execution timing (<15ms)       │  │
│  └───────────────────────┬───────────────────────┴─────────────────▲─────────────────┘  │
│                          │                                         │                    │
│                          │ postMessage({ type: 'RUN', code, id })  │ postMessage(result)│
│                          ▼                                         │                    │
│  ┌─────────────────────────────────────────────────────────────────┴─────────────────┐  │
│  │ Web Worker (playground-worker.js)                                                 │  │
│  │  • Pyodide v0.26+ WebAssembly Runtime (Python 3.12 in Wasm)                       │  │
│  │  • PyYAML pure-Python wheel loaded in Pyodide                                     │  │
│  │  • Virtual Memory FS: /lib/kubelings/ (validator.py, bundle definitions)          │  │
│  │  • Execution Sandbox: runs AST validation and schema tests locally                │  │
│  └───────────────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Curated Flagship Exercises (Showcase Matrix)

The playground includes 11 flagship exercises spanning all 6 curriculum tiers:

| Tier | Chapter | Exercise ID | Exercise Name | Topic Tested |
| :--- | :--- | :--- | :--- | :--- |
| **Tier 1** | `01_pods` | `pods01` | First Pod Manifest & Spec | Container port 80 & label selector |
| **Tier 1** | `02_controllers` | `ctrl01` | ReplicaSet & MatchLabels | `matchLabels` selector synchronization |
| **Tier 1** | `03_config_secrets` | `config01` | ConfigMap Key Injection | `configMapKeyRef` environment injection |
| **Tier 1** | `04_storage` | `storage01` | PVC Volume Mounting | PersistentVolumeClaim volume mount |
| **Tier 2** | `07_scheduling` | `sched01` | Node Affinity & Tolerations | `nodeSelector` and node placement |
| **Tier 2** | `09_netpol` | `netpol01` | Default-Deny Network Policies | Pod isolation and ingress filtering |
| **Tier 3** | `11_autoscaling` | `autoscale01`| Horizontal Pod Autoscaler | HPA v2 CPU utilization metric target |
| **Tier 4** | `14_gitops` | `gitops01` | ArgoCD Application CRD | `argoproj.io/v1alpha1` Application spec |
| **Tier 5** | `21_gateway_api` | `gateway01` | Gateway API HTTPRoute | `gateway.networking.k8s.io/v1` HTTPRoute |
| **Tier 6** | `24_kuberay` | `ray01` | KubeRay RayCluster Basics | `ray.io/v1` RayCluster head/worker specs |
| **Tier 6** | `26_hardware` | `accel02` | Apple Silicon GPU Acceleration | `apple.com/gpu: 1` & `DEVICE: mps` |

---

## 4. Web Worker Communication Protocol

The Web Worker communicates with the main UI thread via structured JSON messages:

### Request Messages (Main Thread ➔ Worker):
1. **`INIT`**:
   ```json
   {
     "type": "INIT",
     "bundle": { ...playgroundBundleData... }
   }
   ```
2. **`RUN_EXERCISE`**:
   ```json
   {
     "type": "RUN_EXERCISE",
     "exerciseId": "pods01",
     "code": "import yaml\n..."
   }
   ```

### Response Messages (Worker ➔ Main Thread):
1. **`STATUS`**:
   ```json
   {
     "type": "STATUS",
     "stage": "loading_pyodide" | "installing_packages" | "mounting_bundle" | "ready",
     "message": "⚡ Pyodide WebAssembly loaded."
   }
   ```
2. **`RUN_RESULT`**:
   ```json
   {
     "type": "RUN_RESULT",
     "exerciseId": "pods01",
     "passed": true,
     "error": null,
     "output": "✓ Exercise pods01 passed all schema and manifest validations!",
     "durationMs": 11.4
   }
   ```

---

## 5. File Structure & Assets

```
docs/
├── playground.md                     # Dedicated MkDocs page embedding the Playground container
└── assets/
    └── playground/
        ├── playground.css            # Responsive flexbox split-pane layout & styling
        ├── playground.js             # UI Controller, Monaco Editor lifecycle & theme sync
        ├── playground-worker.js      # Background Pyodide Web Worker
        └── playground-bundle.json    # Auto-generated JSON bundle (validator + showcase exercises)

scripts/
└── build_playground_bundle.py        # Build script compiling validator + exercises into JSON

tests/
└── test_playground_bundle.py         # Pytest verifying bundle generation, parity & execution
```

---

## 6. Build & Verification Strategy

1. **`scripts/build_playground_bundle.py`**:
   - Reads `src/kubelings/validator.py`, `src/kubelings/models.py`, and `manifest.py`.
   - Extracts starters, solutions, and hints for the 11 flagship exercises.
   - Serializes into `docs/assets/playground/playground-bundle.json`.
2. **Automated Pytest (`tests/test_playground_bundle.py`)**:
   - Asserts `playground-bundle.json` exists and contains all 11 flagship exercises.
   - Asserts all starter exercises in the bundle fail validation initially.
   - Asserts all reference solutions in the bundle pass validation.
3. **MkDocs Build Verification**:
   - `uv run mkdocs build --strict` verifies no broken links or navigation errors.

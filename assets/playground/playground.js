/**
 * Kubelings WebAssembly Playground UI Controller
 *
 * Manages Monaco Editor lifecycle, Web Worker Pyodide execution,
 * exercise navigation, progressive hints, diff inspection, and
 * MkDocs Material dark/light theme synchronization.
 */

(function () {
  "use strict";

  // Tier classification for showcase exercises
  const TIER_MAPPINGS = {
    pods01: { tier: "Tier 1: Core Workloads", badge: "01_pods" },
    ctrl01: { tier: "Tier 1: Core Workloads", badge: "02_controllers" },
    config01: { tier: "Tier 1: Core Workloads", badge: "03_config_secrets" },
    storage01: { tier: "Tier 1: Core Workloads", badge: "04_storage" },
    sched01: { tier: "Tier 2: Scheduling & NetPol", badge: "07_scheduling" },
    netpol01: { tier: "Tier 2: Scheduling & NetPol", badge: "09_netpol" },
    autoscale01: { tier: "Tier 3: Operations & Scale", badge: "11_autoscaling" },
    gitops01: { tier: "Tier 4: GitOps & CRDs", badge: "14_gitops" },
    gateway01: { tier: "Tier 5: Cloud Native Ingress", badge: "21_gateway_api" },
    ray01: { tier: "Tier 6: AI & GPU Acceleration", badge: "24_kuberay" },
    accel02: { tier: "Tier 6: AI & GPU Acceleration", badge: "26_hardware" },
  };

  // State
  const state = {
    bundle: null,
    worker: null,
    workerReady: false,
    monacoLoaded: false,
    editor: null,
    diffEditor: null,
    originalModel: null,
    modifiedModel: null,
    currentExerciseId: "pods01",
    revealedHints: 0,
    isDiffMode: false,
    isRunning: false,
    container: null,
    elements: {},
  };

  /**
   * Resolve an asset URL relative to playground.js or known locations.
   * @param {string} filename
   * @returns {string}
   */
  function resolveAssetUrl(filename) {
    if (document.currentScript && document.currentScript.src) {
      return new URL(filename, document.currentScript.src).href;
    }
    const scripts = document.querySelectorAll('script[src*="playground.js"]');
    if (scripts.length > 0) {
      const src = scripts[scripts.length - 1].src;
      return new URL(filename, src).href;
    }
    // Fallback relative to site root / current path
    return "assets/playground/" + filename;
  }

  /**
   * Escape HTML special characters for safe output.
   * @param {string} str
   * @returns {string}
   */
  function escapeHtml(str) {
    if (!str) return "";
    return str
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  /**
   * Convert ANSI escape sequences to styled HTML spans.
   * @param {string} text
   * @returns {string}
   */
  function ansiToHtml(text) {
    if (!text) return "";
    let escaped = escapeHtml(text);

    // Color codes
    escaped = escaped
      .replace(/\x1b\[32m/g, '<span class="term-pass">')
      .replace(/\x1b\[31m/g, '<span class="term-fail">')
      .replace(/\x1b\[33m/g, '<span class="term-warn">')
      .replace(/\x1b\[34m/g, '<span class="term-info">')
      .replace(/\x1b\[36m/g, '<span class="term-info">')
      .replace(/\x1b\[1m/g, '<span class="term-bold">')
      .replace(/\x1b\[2m/g, '<span class="term-dim">')
      .replace(/\x1b\[0m/g, "</span>")
      .replace(/\x1b\[\d+m/g, ""); // strip unknown codes

    return escaped;
  }

  /**
   * Get current Monaco theme based on MkDocs Material palette or system dark mode.
   * @returns {string} 'vs-dark' or 'vs'
   */
  function getMonacoTheme() {
    const scheme = document.body.getAttribute("data-md-color-scheme");
    if (scheme === "slate") {
      return "vs-dark";
    }
    if (scheme === "default") {
      return "vs";
    }
    if (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches) {
      return "vs-dark";
    }
    return "vs";
  }

  /**
   * Render the playground DOM structure if the container is empty.
   * @param {HTMLElement} container
   */
  function renderPlaygroundSkeleton(container) {
    if (container.querySelector(".playground-workspace")) {
      return; // Already has markup
    }

    container.innerHTML = `
      <div class="playground-header">
        <div class="playground-header-left">
          <div class="playground-select-wrapper">
            <select id="playground-exercise-select" class="playground-exercise-select" aria-label="Select Kubelings Exercise">
              <option value="loading">Loading exercises...</option>
            </select>
            <span class="playground-select-arrow">▼</span>
          </div>
          <span id="playground-topic" class="playground-topic-badge">Initializing...</span>
        </div>
        <div class="playground-header-right">
          <div id="playground-status" class="playground-status-pill status-loading" title="WebAssembly Engine Status">
            <span class="status-dot"></span>
            <span class="status-text">⚡ Starting Python Wasm...</span>
          </div>
        </div>
      </div>

      <div class="playground-toolbar">
        <button id="playground-run-btn" class="playground-btn playground-btn-primary" title="Execute validation (Ctrl+Enter)">
          <span class="btn-icon">▶</span>
          <span>Run Solution</span>
          <span class="playground-btn-kbd">Ctrl+Enter</span>
        </button>
        <button id="playground-reset-btn" class="playground-btn" title="Reset editor to starter code">
          <span class="btn-icon">↺</span>
          <span>Reset Code</span>
        </button>
        <button id="playground-hint-btn" class="playground-btn" title="Reveal hints step-by-step">
          <span class="btn-icon">💡</span>
          <span class="hint-label">Reveal Hint</span>
        </button>
        <button id="playground-diff-btn" class="playground-btn" title="Compare code side-by-side with reference solution">
          <span class="btn-icon">🔍</span>
          <span class="diff-label">Compare Solution</span>
        </button>
      </div>

      <div id="playground-hints" class="playground-hints-card" aria-live="polite"></div>

      <div class="playground-workspace">
        <div class="playground-editor-pane">
          <div id="playground-editor"></div>
          <div id="playground-diff-editor"></div>
        </div>
        <div class="playground-output-pane">
          <div class="playground-output-header">
            <div class="playground-output-title">
              <span class="playground-output-title-dot"></span>
              <span>Diagnostic Output</span>
            </div>
            <div id="playground-output-meta" class="playground-output-meta">Pyodide Wasm Engine</div>
          </div>
          <pre id="playground-output">⚡ Initializing Python 3.12 WebAssembly Runtime and Monaco Editor...</pre>
        </div>
      </div>
    `;
  }

  /**
   * Cache references to key DOM elements.
   * @param {HTMLElement} container
   */
  function bindElements(container) {
    state.elements = {
      select: container.querySelector("#playground-exercise-select"),
      topic: container.querySelector("#playground-topic"),
      status: container.querySelector("#playground-status"),
      statusText: container.querySelector("#playground-status .status-text"),
      runBtn: container.querySelector("#playground-run-btn"),
      resetBtn: container.querySelector("#playground-reset-btn"),
      hintBtn: container.querySelector("#playground-hint-btn"),
      hintLabel: container.querySelector("#playground-hint-btn .hint-label") || container.querySelector("#playground-hint-btn"),
      diffBtn: container.querySelector("#playground-diff-btn"),
      diffLabel: container.querySelector("#playground-diff-btn .diff-label") || container.querySelector("#playground-diff-btn"),
      hintsCard: container.querySelector("#playground-hints"),
      workspace: container.querySelector(".playground-workspace"),
      editorContainer: container.querySelector("#playground-editor"),
      diffContainer: container.querySelector("#playground-diff-editor"),
      output: container.querySelector("#playground-output"),
      outputMeta: container.querySelector("#playground-output-meta"),
    };
  }

  /**
   * Update status pill UI.
   * @param {string} stage - 'loading', 'ready', 'running', 'error'
   * @param {string} message
   */
  function updateStatus(stage, message) {
    const el = state.elements.status;
    const txt = state.elements.statusText;
    if (!el || !txt) return;

    el.className = "playground-status-pill";
    if (stage === "ready") {
      el.classList.add("status-ready");
      state.workerReady = true;
    } else if (stage === "running") {
      el.classList.add("status-running");
    } else if (stage === "error") {
      el.classList.add("status-error");
    } else {
      el.classList.add("status-loading");
    }
    txt.textContent = message;
  }

  /**
   * Populate exercise dropdown grouped by Tier.
   */
  function populateExercises() {
    const select = state.elements.select;
    if (!select || !state.bundle || !state.bundle.exercises) return;

    select.innerHTML = "";
    const exercises = state.bundle.exercises;
    const tierGroups = {};

    // Group exercises by tier
    for (const [id, ex] of Object.entries(exercises)) {
      const tierInfo = TIER_MAPPINGS[id] || {
        tier: "Other Exercises",
        badge: ex.chapter || "general",
      };
      if (!tierGroups[tierInfo.tier]) {
        tierGroups[tierInfo.tier] = [];
      }
      tierGroups[tierInfo.tier].push({ id, ...ex });
    }

    for (const [tierName, exList] of Object.entries(tierGroups)) {
      const optgroup = document.createElement("optgroup");
      optgroup.label = tierName;

      for (const ex of exList) {
        const option = document.createElement("option");
        option.value = ex.id;
        option.textContent = `${ex.id}: ${ex.title}`;
        optgroup.appendChild(option);
      }
      select.appendChild(optgroup);
    }

    select.value = state.currentExerciseId;
    select.addEventListener("change", (e) => {
      selectExercise(e.target.value);
    });
  }

  /**
   * Switch the active exercise and update editor & hints.
   * @param {string} exerciseId
   */
  function selectExercise(exerciseId) {
    if (!state.bundle || !state.bundle.exercises[exerciseId]) return;

    state.currentExerciseId = exerciseId;
    const ex = state.bundle.exercises[exerciseId];

    // Update topic badge
    if (state.elements.topic) {
      const tierInfo = TIER_MAPPINGS[exerciseId];
      state.elements.topic.textContent = tierInfo
        ? `${tierInfo.badge} • ${ex.title}`
        : `${ex.chapter || "exercise"} • ${ex.title}`;
    }

    // Reset hints
    state.revealedHints = 0;
    renderHints();

    // Update Monaco editor code
    if (state.editor) {
      state.editor.setValue(ex.starter_code || "");
    }

    // If diff editor is active, update diff models
    if (state.isDiffMode && state.diffEditor && window.monaco) {
      updateDiffModels();
    }

    // Output welcoming line
    if (state.elements.output) {
      state.elements.output.innerHTML = `
<span class="term-banner-info">📚 Loaded exercise: <strong>${escapeHtml(ex.id)}</strong> — ${escapeHtml(ex.title)}</span>
<span class="term-dim">Fix the manifest issues in the Python code on the left, then click </span><span class="term-pass">▶ Run Solution</span><span class="term-dim"> (or press Ctrl+Enter).</span>
`;
    }
  }

  /**
   * Render hint cards up to the currently revealed hint index.
   */
  function renderHints() {
    const card = state.elements.hintsCard;
    const label = state.elements.hintLabel;
    if (!card) return;

    const ex = state.bundle && state.bundle.exercises[state.currentExerciseId];
    const hints = (ex && ex.hints) || [];

    if (state.revealedHints <= 0 || hints.length === 0) {
      card.className = "playground-hints-card";
      card.innerHTML = "";
      if (label) label.textContent = "Reveal Hint";
      return;
    }

    card.className = "playground-hints-card hints-visible";
    let html = "";
    for (let i = 0; i < state.revealedHints && i < hints.length; i++) {
      html += `
        <div class="playground-hint-item">
          <span class="playground-hint-badge">Hint ${i + 1}/${hints.length}</span>
          <span class="playground-hint-text">${escapeHtml(hints[i])}</span>
        </div>
      `;
    }
    card.innerHTML = html;

    if (label) {
      if (state.revealedHints >= hints.length) {
        label.textContent = `Hide Hints (${hints.length}/${hints.length})`;
      } else {
        label.textContent = `Next Hint (${state.revealedHints}/${hints.length})`;
      }
    }
  }

  /**
   * Toggle progressive hints.
   */
  function toggleHint() {
    const ex = state.bundle && state.bundle.exercises[state.currentExerciseId];
    const hints = (ex && ex.hints) || [];
    if (hints.length === 0) return;

    if (state.revealedHints >= hints.length) {
      state.revealedHints = 0;
    } else {
      state.revealedHints++;
    }
    renderHints();
  }

  /**
   * Update diff editor original and modified models.
   */
  function updateDiffModels() {
    if (!window.monaco || !state.diffEditor) return;

    const ex = state.bundle && state.bundle.exercises[state.currentExerciseId];
    if (!ex) return;

    const userCode = state.editor ? state.editor.getValue() : ex.starter_code;
    const solutionCode = ex.solution_code || "";

    if (state.originalModel) state.originalModel.dispose();
    if (state.modifiedModel) state.modifiedModel.dispose();

    state.originalModel = window.monaco.editor.createModel(userCode, "python");
    state.modifiedModel = window.monaco.editor.createModel(solutionCode, "python");

    state.diffEditor.setModel({
      original: state.originalModel,
      modified: state.modifiedModel,
    });
  }

  /**
   * Toggle side-by-side solution diff comparison.
   */
  function toggleDiffView() {
    if (!state.diffEditor || !state.editor) return;

    state.isDiffMode = !state.isDiffMode;
    const workspace = state.elements.workspace;
    const label = state.elements.diffLabel;
    const diffBtn = state.elements.diffBtn;

    if (state.isDiffMode) {
      updateDiffModels();
      if (workspace) workspace.classList.add("diff-active");
      if (diffBtn) diffBtn.classList.add("btn-active");
      if (label) label.textContent = "Close Diff";
      setTimeout(() => state.diffEditor.layout(), 20);
    } else {
      if (workspace) workspace.classList.remove("diff-active");
      if (diffBtn) diffBtn.classList.remove("btn-active");
      if (label) label.textContent = "Compare Solution";
      setTimeout(() => state.editor.layout(), 20);
    }
  }

  /**
   * Reset editor code to current exercise's starter code.
   */
  function resetEditorCode() {
    const ex = state.bundle && state.bundle.exercises[state.currentExerciseId];
    if (!ex || !state.editor) return;

    state.editor.setValue(ex.starter_code || "");
    if (state.isDiffMode) {
      updateDiffModels();
    }

    if (state.elements.output) {
      state.elements.output.innerHTML = `
<span class="term-banner-info">↺ Reset editor code to the original starter template for '${escapeHtml(ex.id)}'.</span>
<span class="term-dim">Press </span><span class="term-pass">▶ Run Solution</span><span class="term-dim"> (Ctrl+Enter) to evaluate.</span>
`;
    }
  }

  /**
   * Execute the active exercise code in Pyodide Web Worker.
   */
  function runCurrentExercise() {
    if (state.isRunning) return;

    const ex = state.bundle && state.bundle.exercises[state.currentExerciseId];
    if (!ex) return;

    if (!state.workerReady || !state.worker) {
      if (state.elements.output) {
        state.elements.output.innerHTML = `<span class="term-banner-fail">⏳ Python WebAssembly engine is still initializing. Please wait a moment...</span>`;
      }
      return;
    }

    const code = state.editor ? state.editor.getValue() : ex.starter_code;
    state.isRunning = true;

    // UI running feedback
    updateStatus("running", "⚡ Running validation in WebAssembly...");
    if (state.elements.runBtn) {
      state.elements.runBtn.disabled = true;
      state.elements.runBtn.querySelector(".btn-icon").textContent = "⏳";
    }
    if (state.elements.outputMeta) {
      state.elements.outputMeta.textContent = "Executing in Wasm sandbox...";
    }

    state.worker.postMessage({
      type: "RUN_EXERCISE",
      exerciseId: state.currentExerciseId,
      code: code,
      filename: ex.filename || "exercise.py",
    });
  }

  /**
   * Handle result from Pyodide Web Worker.
   * @param {Object} result
   */
  function handleRunResult(result) {
    state.isRunning = false;

    // Restore run button
    if (state.elements.runBtn) {
      state.elements.runBtn.disabled = false;
      state.elements.runBtn.querySelector(".btn-icon").textContent = "▶";
    }

    updateStatus("ready", "✅ Ready (Python 3.12 Wasm)");

    const duration = typeof result.durationMs === "number" ? result.durationMs : 0;
    if (state.elements.outputMeta) {
      state.elements.outputMeta.textContent = `⏱ Execution Time: ${duration} ms`;
    }

    const outEl = state.elements.output;
    if (!outEl) return;

    if (result.passed) {
      let outputHtml = `
<span class="term-banner-pass">✓ PASSED (${duration} ms) — Exercise '${escapeHtml(result.exerciseId)}' validated successfully!</span>
`;
      if (result.output) {
        outputHtml += `<span class="term-pass">${ansiToHtml(result.output)}</span>\n`;
      }
      outputHtml += `<span class="term-dim">✨ All schema constraints and assertions passed in client-side WebAssembly!</span>`;
      outEl.innerHTML = outputHtml;
    } else {
      let outputHtml = `
<span class="term-banner-fail">✗ VALIDATION FAILED (${duration} ms) — Exercise '${escapeHtml(result.exerciseId)}'</span>
`;
      if (result.error) {
        outputHtml += `<span class="term-fail term-bold">${escapeHtml(result.error)}</span>\n\n`;
      }
      if (result.traceback) {
        outputHtml += `<span class="term-dim">${escapeHtml(result.traceback)}</span>\n`;
      } else if (result.output) {
        outputHtml += `<span class="term-dim">${escapeHtml(result.output)}</span>\n`;
      }
      outputHtml += `<span class="term-dim">Tip: Check hints with 💡 Reveal Hint or compare against the reference solution with 🔍 Compare Solution.</span>`;
      outEl.innerHTML = outputHtml;
    }

    outEl.scrollTop = 0;
  }

  /**
   * Setup Web Worker with Pyodide and mount bundle.
   */
  async function initWorker() {
    const workerUrl = resolveAssetUrl("playground-worker.js");
    let worker;

    try {
      worker = new Worker(workerUrl);
    } catch (e) {
      // Cross-origin fallback via fetch + Blob
      try {
        const resp = await fetch(workerUrl);
        const code = await resp.text();
        const blob = new Blob([code], { type: "application/javascript" });
        worker = new Worker(URL.createObjectURL(blob));
      } catch (err) {
        updateStatus("error", "Failed to spawn Web Worker: " + err.message);
        return;
      }
    }

    state.worker = worker;

    worker.onmessage = function (e) {
      const msg = e.data;
      if (!msg) return;

      if (msg.type === "STATUS") {
        updateStatus(msg.stage, msg.message);
        if (msg.stage === "ready") {
          const ex = state.bundle && state.bundle.exercises[state.currentExerciseId];
          if (state.elements.output && ex) {
            state.elements.output.innerHTML = `
<span class="term-banner-info">🚀 Kubelings WebAssembly Playground Ready (Python 3.12 + PyYAML)</span>
<span class="term-dim">Active Exercise: </span><span class="term-bold">${escapeHtml(ex.id)}</span> — ${escapeHtml(ex.title)}
<span class="term-dim">Click </span><span class="term-pass">▶ Run Solution</span><span class="term-dim"> (Ctrl+Enter) to validate your manifest.</span>
`;
          }
        }
      } else if (msg.type === "RUN_RESULT") {
        handleRunResult(msg);
      }
    };

    worker.onerror = function (err) {
      updateStatus("error", "Worker error: " + (err.message || "Unknown error"));
    };

    // Send bundle to worker for initialization
    worker.postMessage({
      type: "INIT",
      bundle: state.bundle,
    });
  }

  /**
   * Load Playground Bundle JSON.
   */
  async function loadBundle() {
    const candidateUrls = [
      resolveAssetUrl("playground-bundle.json"),
      "assets/playground/playground-bundle.json",
      "/assets/playground/playground-bundle.json",
      "../assets/playground/playground-bundle.json",
      "docs/assets/playground/playground-bundle.json",
    ];

    let bundleData = null;
    for (const url of candidateUrls) {
      try {
        const res = await fetch(url);
        if (res.ok) {
          bundleData = await res.json();
          break;
        }
      } catch (_) {
        // Try next candidate
      }
    }

    if (!bundleData) {
      throw new Error("Unable to load playground-bundle.json from candidate paths.");
    }

    state.bundle = bundleData;
  }

  /**
   * Load Monaco Editor AMD loader from CDN and initialize editor instances.
   */
  function loadMonacoEditor(onLoaded) {
    if (window.monaco) {
      onLoaded();
      return;
    }

    if (window.require && window.require.config) {
      window.require.config({
        paths: { vs: "https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.45.0/min/vs" },
      });
      window.require(["vs/editor/editor.main"], onLoaded);
      return;
    }

    const loaderScript = document.createElement("script");
    loaderScript.src = "https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.45.0/min/vs/loader.min.js";
    loaderScript.onload = function () {
      window.require.config({
        paths: { vs: "https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.45.0/min/vs" },
      });
      window.require(["vs/editor/editor.main"], onLoaded);
    };
    loaderScript.onerror = function () {
      updateStatus("error", "Failed to load Monaco Editor from CDN.");
    };
    document.head.appendChild(loaderScript);
  }

  /**
   * Initialize Monaco Editor and Monaco Diff Editor.
   */
  function setupMonaco() {
    const editorEl = state.elements.editorContainer;
    const diffEl = state.elements.diffContainer;
    if (!editorEl || !window.monaco) return;

    const currentTheme = getMonacoTheme();
    const ex = state.bundle && state.bundle.exercises[state.currentExerciseId];
    const initialCode = (ex && ex.starter_code) || "";

    // Main Code Editor
    state.editor = window.monaco.editor.create(editorEl, {
      value: initialCode,
      language: "python",
      theme: currentTheme,
      automaticLayout: true,
      fontSize: 13.5,
      lineHeight: 20,
      tabSize: 4,
      insertSpaces: true,
      minimap: { enabled: false },
      scrollBeyondLastLine: false,
      roundedSelection: true,
      renderLineHighlight: "all",
      padding: { top: 12, bottom: 12 },
    });

    // Keyboard shortcut: Ctrl+Enter or Cmd+Enter to run
    state.editor.addCommand(
      window.monaco.KeyMod.CtrlCmd | window.monaco.KeyCode.Enter,
      runCurrentExercise
    );

    // Diff Editor (Side-by-Side)
    if (diffEl) {
      state.diffEditor = window.monaco.editor.createDiffEditor(diffEl, {
        automaticLayout: true,
        readOnly: true,
        renderSideBySide: true,
        theme: currentTheme,
        minimap: { enabled: false },
        fontSize: 13,
        lineHeight: 19,
        scrollBeyondLastLine: false,
        padding: { top: 12, bottom: 12 },
      });
    }

    // Set up theme synchronization observer
    setupThemeObserver();
  }

  let activeThemeObserver = null;

  /**
   * Observe MkDocs Material theme changes to dynamically sync Monaco editor theme.
   */
  function setupThemeObserver() {
    if (activeThemeObserver) {
      activeThemeObserver.disconnect();
      activeThemeObserver = null;
    }

    activeThemeObserver = new MutationObserver((mutations) => {
      for (const m of mutations) {
        if (m.type === "attributes" && m.attributeName === "data-md-color-scheme") {
          const theme = getMonacoTheme();
          if (window.monaco) {
            window.monaco.editor.setTheme(theme);
          }
        }
      }
    });

    activeThemeObserver.observe(document.body, {
      attributes: true,
      attributeFilter: ["data-md-color-scheme"],
    });

    // Also listen to system dark mode preference change
    if (window.matchMedia) {
      window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => {
        if (window.monaco) {
          window.monaco.editor.setTheme(getMonacoTheme());
        }
      });
    }
  }

  /**
   * Bind event listeners for UI buttons.
   */
  function bindActionButtons() {
    if (state.elements.runBtn) {
      state.elements.runBtn.addEventListener("click", runCurrentExercise);
    }
    if (state.elements.resetBtn) {
      state.elements.resetBtn.addEventListener("click", resetEditorCode);
    }
    if (state.elements.hintBtn) {
      state.elements.hintBtn.addEventListener("click", toggleHint);
    }
    if (state.elements.diffBtn) {
      state.elements.diffBtn.addEventListener("click", toggleDiffView);
    }
  }

  /**
   * Main Initialization Entry Point.
   */
  async function initKubelingsPlayground() {
    const container = document.querySelector("#kubelings-playground, .kubelings-playground");
    if (!container) return;

    if (container.dataset.playgroundInitialized === "true") {
      return; // Prevent duplicate initialization
    }

    // Clean up any stale instances before re-initializing
    if (state.editor) {
      try {
        state.editor.dispose();
      } catch (_) {}
      state.editor = null;
    }
    if (state.diffEditor) {
      try {
        state.diffEditor.dispose();
      } catch (_) {}
      state.diffEditor = null;
    }
    if (state.worker) {
      try {
        state.worker.terminate();
      } catch (_) {}
      state.worker = null;
    }

    container.dataset.playgroundInitialized = "true";
    state.container = container;

    // Render skeleton if container is empty
    renderPlaygroundSkeleton(container);
    bindElements(container);
    bindActionButtons();

    try {
      updateStatus("loading", "⚡ Loading showcase bundle...");
      await loadBundle();

      populateExercises();
      selectExercise(state.currentExerciseId);

      updateStatus("loading", "⚡ Loading Monaco Editor & Web Worker...");
      loadMonacoEditor(() => {
        state.monacoLoaded = true;
        setupMonaco();
      });

      await initWorker();
    } catch (err) {
      updateStatus("error", "Error: " + err.message);
      if (state.elements.output) {
        state.elements.output.innerHTML = `<span class="term-banner-fail">Initialization Error: ${escapeHtml(err.message)}</span>`;
      }
    }
  }

  // Expose globally
  window.initKubelingsPlayground = initKubelingsPlayground;

  // Auto-mount when DOM is ready
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initKubelingsPlayground);
  } else {
    initKubelingsPlayground();
  }

  // MkDocs Material navigation.instant support
  if (typeof window.document$ !== "undefined") {
    window.document$.subscribe(initKubelingsPlayground);
  }
})();

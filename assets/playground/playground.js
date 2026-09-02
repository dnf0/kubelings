/**
 * Kubelings WebAssembly Playground UI Controller & State Engine
 *
 * Full 114-exercise browser learning environment powered by Pyodide WebAssembly.
 * Features client-side localStorage persistence, interactive split-pane syllabus sidebar,
 * real-time search & filters, progressive hints, side-by-side solution diffs, and progress backup.
 */

(function () {
  "use strict";

  const STORAGE_KEY = "kubelings_learning_state_v1";

  /**
   * ==========================================================================
   * KubelingsStorage: Client-Side Progress & Working Code Persistence
   * ==========================================================================
   */
  const KubelingsStorage = {
    state: null,
    saveTimeout: null,

    init(bundle) {
      let saved = null;
      try {
        const raw = localStorage.getItem(STORAGE_KEY);
        if (raw) {
          saved = JSON.parse(raw);
        }
      } catch (e) {
        console.warn("Failed to read Kubelings state from localStorage:", e);
      }

      const totalExercises = bundle && bundle.exercises ? Object.keys(bundle.exercises).length : 114;

      if (!saved || saved.version !== 1 || !saved.exercises) {
        saved = {
          version: 1,
          lastActiveExerciseId: "pods01",
          exercises: {},
          stats: {
            completedCount: 0,
            totalCount: totalExercises,
            completionPercentage: 0,
          },
        };
      }

      // Ensure all bundle exercises are represented in storage
      if (bundle && bundle.exercises) {
        for (const [id, ex] of Object.entries(bundle.exercises)) {
          if (!saved.exercises[id]) {
            saved.exercises[id] = {
              status: "not_started",
              userCode: ex.starter_code || "",
              hintsRevealed: 0,
            };
          }
        }
      }

      this.state = saved;
      this.recalculateStats(bundle);
      this.persist();
      return this.state;
    },

    recalculateStats(bundle) {
      if (!this.state || !this.state.exercises) return;
      let completed = 0;
      const total = bundle && bundle.exercises ? Object.keys(bundle.exercises).length : Object.keys(this.state.exercises).length;

      for (const exState of Object.values(this.state.exercises)) {
        if (exState.status === "completed") {
          completed++;
        }
      }

      this.state.stats = {
        completedCount: completed,
        totalCount: total || 1,
        completionPercentage: total > 0 ? Math.round((completed / total) * 100) : 0,
      };
    },

    persist() {
      if (!this.state) return;
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(this.state));
      } catch (e) {
        console.warn("Failed to write Kubelings state to localStorage:", e);
      }
    },

    getExerciseState(exerciseId, defaultStarterCode = "") {
      if (!this.state) return { status: "not_started", userCode: defaultStarterCode, hintsRevealed: 0 };
      if (!this.state.exercises[exerciseId]) {
        this.state.exercises[exerciseId] = {
          status: "not_started",
          userCode: defaultStarterCode,
          hintsRevealed: 0,
        };
        this.persist();
      }
      return this.state.exercises[exerciseId];
    },

    saveExerciseCode(exerciseId, code) {
      if (!this.state) return;
      const exState = this.getExerciseState(exerciseId, code);
      exState.userCode = code;
      if (exState.status === "not_started") {
        exState.status = "in_progress";
      }
      exState.lastEvaluatedAt = new Date().toISOString();

      clearTimeout(this.saveTimeout);
      this.saveTimeout = setTimeout(() => {
        this.persist();
      }, 300);
    },

    markCompleted(exerciseId, bundle) {
      if (!this.state) return;
      const exState = this.getExerciseState(exerciseId);
      exState.status = "completed";
      exState.passedAt = new Date().toISOString();
      this.recalculateStats(bundle);
      this.persist();
    },

    setHintsRevealed(exerciseId, count) {
      if (!this.state) return;
      const exState = this.getExerciseState(exerciseId);
      exState.hintsRevealed = count;
      this.persist();
    },

    resetExercise(exerciseId, starterCode) {
      if (!this.state) return;
      this.state.exercises[exerciseId] = {
        status: "not_started",
        userCode: starterCode || "",
        hintsRevealed: 0,
      };
      this.persist();
    },

    resetAll(bundle) {
      this.state = {
        version: 1,
        lastActiveExerciseId: "pods01",
        exercises: {},
        stats: {
          completedCount: 0,
          totalCount: bundle && bundle.exercises ? Object.keys(bundle.exercises).length : 114,
          completionPercentage: 0,
        },
      };
      if (bundle && bundle.exercises) {
        for (const [id, ex] of Object.entries(bundle.exercises)) {
          this.state.exercises[id] = {
            status: "not_started",
            userCode: ex.starter_code || "",
            hintsRevealed: 0,
          };
        }
      }
      this.persist();
    },

    exportJSON() {
      return JSON.stringify(this.state, null, 2);
    },

    importJSON(jsonString, bundle) {
      try {
        const parsed = JSON.parse(jsonString);
        if (!parsed || parsed.version !== 1 || !parsed.exercises) {
          throw new Error("Invalid Kubelings progress backup format.");
        }
        this.state = parsed;
        this.recalculateStats(bundle);
        this.persist();
        return true;
      } catch (err) {
        console.error("Import failed:", err);
        return false;
      }
    },
  };

  /**
   * ==========================================================================
   * Application State & UI Controller
   * ==========================================================================
   */
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
    sidebarFilter: "all", // 'all', 'incomplete', 'completed'
    searchQuery: "",
    expandedChapters: new Set(),
    container: null,
    elements: {},
  };

  /**
   * Resolve an asset URL relative to playground.js or known locations.
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
    return "assets/playground/" + filename;
  }

  function escapeHtml(str) {
    if (!str) return "";
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function ansiToHtml(text) {
    if (!text) return "";
    let escaped = escapeHtml(text);
    escaped = escaped
      .replace(/\x1b\[32m/g, '<span class="term-pass">')
      .replace(/\x1b\[31m/g, '<span class="term-fail">')
      .replace(/\x1b\[33m/g, '<span class="term-warn">')
      .replace(/\x1b\[34m/g, '<span class="term-info">')
      .replace(/\x1b\[36m/g, '<span class="term-info">')
      .replace(/\x1b\[1m/g, '<span class="term-bold">')
      .replace(/\x1b\[2m/g, '<span class="term-dim">')
      .replace(/\x1b\[0m/g, "</span>")
      .replace(/\x1b\[\d+m/g, "");
    return escaped;
  }

  function getMonacoTheme() {
    const scheme = document.body.getAttribute("data-md-color-scheme");
    if (scheme === "slate") return "vs-dark";
    if (scheme === "default") return "vs";
    if (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches) {
      return "vs-dark";
    }
    return "vs";
  }

  /**
   * Render the complete split-pane layout skeleton.
   */
  function renderPlaygroundSkeleton(container) {
    if (container.querySelector(".playground-split-layout")) {
      return;
    }

    container.innerHTML = `
      <div class="playground-split-layout">
        <!-- Sidebar: Curriculum & Progress Explorer -->
        <aside class="playground-sidebar" aria-label="Kubelings Curriculum Sidebar">
          <div class="sidebar-header">
            <div class="sidebar-title-row">
              <span class="sidebar-title">☸ Curriculum</span>
              <div class="sidebar-actions">
                <button id="pg-btn-export" class="sidebar-icon-btn" title="Export Progress (JSON)">📥</button>
                <button id="pg-btn-import" class="sidebar-icon-btn" title="Import Progress (JSON)">📤</button>
                <button id="pg-btn-reset-all" class="sidebar-icon-btn sidebar-icon-danger" title="Reset All Progress">🗑️</button>
                <input type="file" id="pg-file-import" accept=".json" style="display:none;" />
              </div>
            </div>

            <!-- Global Progress Bar -->
            <div class="sidebar-progress-container">
              <div class="sidebar-progress-labels">
                <span id="pg-progress-text" class="sidebar-progress-text">0 / 114 Completed</span>
                <span id="pg-progress-pct" class="sidebar-progress-pct">0%</span>
              </div>
              <div class="sidebar-progress-track">
                <div id="pg-progress-fill" class="sidebar-progress-fill" style="width: 0%;"></div>
              </div>
            </div>

            <!-- Search & Filters -->
            <div class="sidebar-search-row">
              <input type="text" id="pg-search-input" class="sidebar-search-input" placeholder="Search exercises, concepts..." />
            </div>
            <div class="sidebar-filter-tabs">
              <button class="filter-tab active" data-filter="all">All</button>
              <button class="filter-tab" data-filter="incomplete">To Do</button>
              <button class="filter-tab" data-filter="completed">Done</button>
            </div>
          </div>

          <!-- Syllabus Chapters Tree -->
          <div id="pg-syllabus-tree" class="sidebar-syllabus-tree">
            <div class="sidebar-loading-placeholder">⚡ Loading curriculum syllabus...</div>
          </div>
        </aside>

        <!-- Main Workspace: Editor, Controls & Diagnostics -->
        <main class="playground-main-workspace">
          <!-- Exercise Breadcrumb & Top Bar -->
          <div class="workspace-top-bar">
            <div class="workspace-meta-left">
              <span id="pg-chapter-badge" class="chapter-badge">Chapter 01</span>
              <h2 id="pg-exercise-title" class="exercise-title">Loading exercise...</h2>
              <span id="pg-cluster-tag" class="cluster-tag" style="display:none;">Live Cluster</span>
            </div>
            <div class="workspace-meta-right">
              <div class="nav-stepper">
                <button id="pg-prev-btn" class="nav-btn" title="Previous Exercise (Alt+Left)">← Prev</button>
                <button id="pg-next-btn" class="nav-btn" title="Next Exercise (Alt+Right)">Next →</button>
              </div>
              <button id="pg-fullscreen-btn" class="nav-btn" title="Toggle Fullscreen (F11)">⛶ Fullscreen</button>
              <div id="playground-status" class="playground-status-pill status-loading" title="WebAssembly Engine Status">
                <span class="status-dot"></span>
                <span class="status-text">⚡ Starting Python Wasm...</span>
              </div>
            </div>
          </div>

          <!-- Action Toolbar -->
          <div class="playground-toolbar">
            <button id="playground-run-btn" class="playground-btn playground-btn-primary" title="Execute validation in Pyodide Wasm (Ctrl+Enter)">
              <span class="btn-icon">▶</span>
              <span>Run Solution</span>
              <span class="playground-btn-kbd">Ctrl+Enter</span>
            </button>
            <button id="playground-hint-btn" class="playground-btn" title="Reveal hints step-by-step (H)">
              <span class="btn-icon">💡</span>
              <span class="hint-label">Reveal Hint</span>
            </button>
            <button id="playground-reset-btn" class="playground-btn" title="Reset current file to starter template">
              <span class="btn-icon">↺</span>
              <span>Reset Code</span>
            </button>
            <button id="playground-diff-btn" class="playground-btn" title="Compare side-by-side with reference solution">
              <span class="btn-icon">🔍</span>
              <span class="diff-label">Compare Solution</span>
            </button>
          </div>

          <!-- Live Cluster Notification Banner -->
          <div id="pg-cluster-banner" class="playground-cluster-banner" style="display:none;">
            <span class="banner-icon">ℹ️</span>
            <div class="banner-content">
              <strong>Offline AST & Schema Validation:</strong> This exercise spec is evaluated in-browser. To test live cluster reconciliation against <code>kind</code> or <code>minikube</code>, run <code>kubelings run <span id="pg-cluster-banner-ex"></span></code> in your CLI.
            </div>
          </div>

          <!-- Progressive Hints Card -->
          <div id="playground-hints" class="playground-hints-card" aria-live="polite"></div>

          <!-- Editor & Terminal Panes -->
          <div class="playground-workspace">
            <div class="playground-editor-pane">
              <div id="playground-editor"></div>
              <div id="playground-diff-editor"></div>
            </div>
            <div class="playground-output-pane">
              <div class="playground-output-header">
                <div class="playground-output-title">
                  <span class="playground-output-title-dot"></span>
                  <span>Terminal Diagnostics</span>
                </div>
                <div id="playground-output-meta" class="playground-output-meta">Pyodide Wasm Sandbox</div>
              </div>
              <pre id="playground-output">⚡ Initializing Python 3.12 WebAssembly Runtime and Monaco Editor...</pre>
            </div>
          </div>
        </main>
      </div>
    `;
  }

  /**
   * Bind cached DOM references.
   */
  function bindElements(container) {
    state.elements = {
      sidebarTree: container.querySelector("#pg-syllabus-tree"),
      progressText: container.querySelector("#pg-progress-text"),
      progressPct: container.querySelector("#pg-progress-pct"),
      progressFill: container.querySelector("#pg-progress-fill"),
      searchInput: container.querySelector("#pg-search-input"),
      filterTabs: container.querySelectorAll(".filter-tab"),
      exportBtn: container.querySelector("#pg-btn-export"),
      importBtn: container.querySelector("#pg-btn-import"),
      importFile: container.querySelector("#pg-file-import"),
      resetAllBtn: container.querySelector("#pg-btn-reset-all"),
      chapterBadge: container.querySelector("#pg-chapter-badge"),
      exerciseTitle: container.querySelector("#pg-exercise-title"),
      clusterTag: container.querySelector("#pg-cluster-tag"),
      clusterBanner: container.querySelector("#pg-cluster-banner"),
      clusterBannerEx: container.querySelector("#pg-cluster-banner-ex"),
      prevBtn: container.querySelector("#pg-prev-btn"),
      nextBtn: container.querySelector("#pg-next-btn"),
      fullscreenBtn: container.querySelector("#pg-fullscreen-btn"),
      status: container.querySelector("#playground-status"),
      statusText: container.querySelector("#playground-status .status-text"),
      runBtn: container.querySelector("#playground-run-btn"),
      resetBtn: container.querySelector("#playground-reset-btn"),
      hintBtn: container.querySelector("#playground-hint-btn"),
      hintLabel: container.querySelector("#playground-hint-btn .hint-label"),
      diffBtn: container.querySelector("#playground-diff-btn"),
      diffLabel: container.querySelector("#playground-diff-btn .diff-label"),
      hintsCard: container.querySelector("#playground-hints"),
      workspace: container.querySelector(".playground-workspace"),
      editorContainer: container.querySelector("#playground-editor"),
      diffContainer: container.querySelector("#playground-diff-editor"),
      output: container.querySelector("#playground-output"),
      outputMeta: container.querySelector("#playground-output-meta"),
    };
  }

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
   * Update the global progress bar and counter.
   */
  function updateProgressUI() {
    if (!state.bundle || !KubelingsStorage.state) return;
    const stats = KubelingsStorage.state.stats;
    const completed = stats.completedCount;
    const total = stats.totalCount || Object.keys(state.bundle.exercises).length || 114;
    const pct = stats.completionPercentage;

    if (state.elements.progressText) {
      state.elements.progressText.textContent = `${completed} / ${total} Completed`;
    }
    if (state.elements.progressPct) {
      state.elements.progressPct.textContent = `${pct}%`;
    }
    if (state.elements.progressFill) {
      state.elements.progressFill.style.width = `${pct}%`;
    }
  }

  /**
   * Render the 26-chapter collapsible accordion tree in the sidebar.
   */
  function renderSyllabusTree() {
    const treeEl = state.elements.sidebarTree;
    if (!treeEl || !state.bundle || !state.bundle.chapters) return;

    const query = state.searchQuery.toLowerCase().trim();
    const filter = state.sidebarFilter;
    let html = "";

    const activeExercise = state.bundle.exercises[state.currentExerciseId];
    const activeChapterNumber = activeExercise ? activeExercise.chapter_number : 1;

    // Ensure the active chapter is expanded by default
    if (state.expandedChapters.size === 0) {
      state.expandedChapters.add(activeChapterNumber);
    }

    let matchingExerciseCount = 0;

    for (const chapter of state.bundle.chapters) {
      const chapterExercises = (chapter.exercise_ids || [])
        .map((id) => state.bundle.exercises[id])
        .filter(Boolean);

      // Calculate chapter progress
      let chCompleted = 0;
      for (const ex of chapterExercises) {
        const exState = KubelingsStorage.getExerciseState(ex.id, ex.starter_code);
        if (exState.status === "completed") chCompleted++;
      }

      // Filter exercises by search query and completion filter
      const visibleExercises = chapterExercises.filter((ex) => {
        const exState = KubelingsStorage.getExerciseState(ex.id, ex.starter_code);
        if (filter === "completed" && exState.status !== "completed") return false;
        if (filter === "incomplete" && exState.status === "completed") return false;

        if (query) {
          const matchTitle = ex.title.toLowerCase().includes(query);
          const matchId = ex.id.toLowerCase().includes(query);
          const matchChapter = chapter.title.toLowerCase().includes(query);
          return matchTitle || matchId || matchChapter;
        }
        return true;
      });

      if (query && visibleExercises.length === 0) {
        continue;
      }

      matchingExerciseCount += visibleExercises.length;
      const isExpanded = query ? true : state.expandedChapters.has(chapter.number);
      const isChapterComplete = chCompleted === chapterExercises.length && chapterExercises.length > 0;

      html += `
        <div class="chapter-group ${isExpanded ? "expanded" : ""}" data-chapter-num="${chapter.number}">
          <div class="chapter-header" data-toggle-chapter="${chapter.number}">
            <div class="chapter-header-title">
              <span class="chapter-chevron">▸</span>
              <span class="chapter-num">${String(chapter.number).padStart(2, "0")}.</span>
              <span class="chapter-name" title="${escapeHtml(chapter.title)}">${escapeHtml(chapter.title)}</span>
            </div>
            <span class="chapter-badge-count ${isChapterComplete ? "complete" : ""}">
              ${chCompleted}/${chapterExercises.length} ${isChapterComplete ? "✓" : ""}
            </span>
          </div>
          <div class="chapter-exercise-list">
      `;

      for (const ex of visibleExercises) {
        const exState = KubelingsStorage.getExerciseState(ex.id, ex.starter_code);
        const isActive = ex.id === state.currentExerciseId;
        const status = exState.status;

        let statusIcon = "○";
        let statusClass = "status-unstarted";
        if (status === "completed") {
          statusIcon = "✓";
          statusClass = "status-done";
        } else if (status === "in_progress") {
          statusIcon = "⏳";
          statusClass = "status-progress";
        }

        html += `
          <div class="exercise-item ${isActive ? "active" : ""} ${statusClass}" data-exercise-id="${ex.id}">
            <span class="exercise-status-icon">${statusIcon}</span>
            <div class="exercise-item-content">
              <div class="exercise-item-title">
                <span class="exercise-item-id">${escapeHtml(ex.id)}:</span> ${escapeHtml(ex.title)}
              </div>
            </div>
            ${ex.requires_cluster ? '<span class="exercise-cluster-badge" title="Live Cluster Exercise">☸</span>' : ""}
          </div>
        `;
      }

      html += `
          </div>
        </div>
      `;
    }

    if (matchingExerciseCount === 0) {
      html = `<div class="sidebar-empty">No exercises found matching "${escapeHtml(query)}"</div>`;
    }

    treeEl.innerHTML = html;

    // Attach chapter toggle handlers
    treeEl.querySelectorAll("[data-toggle-chapter]").forEach((el) => {
      el.addEventListener("click", () => {
        const num = parseInt(el.getAttribute("data-toggle-chapter"), 10);
        if (state.expandedChapters.has(num)) {
          state.expandedChapters.delete(num);
        } else {
          state.expandedChapters.add(num);
        }
        renderSyllabusTree();
      });
    });

    // Attach exercise select handlers
    treeEl.querySelectorAll(".exercise-item").forEach((el) => {
      el.addEventListener("click", () => {
        const exId = el.getAttribute("data-exercise-id");
        if (exId) {
          selectExercise(exId);
        }
      });
    });
  }

  /**
   * Select and load an exercise into workspace.
   */
  function selectExercise(exerciseId) {
    if (!state.bundle || !state.bundle.exercises[exerciseId]) return;

    state.currentExerciseId = exerciseId;
    const ex = state.bundle.exercises[exerciseId];
    KubelingsStorage.state.lastActiveExerciseId = exerciseId;
    KubelingsStorage.persist();

    // Auto-expand current chapter
    if (ex.chapter_number) {
      state.expandedChapters.add(ex.chapter_number);
    }

    // Update Header
    if (state.elements.chapterBadge) {
      state.elements.chapterBadge.textContent = `Chapter ${String(ex.chapter_number || 1).padStart(2, "0")}: ${ex.chapter_title || ex.chapter}`;
    }
    if (state.elements.exerciseTitle) {
      state.elements.exerciseTitle.textContent = `${ex.id} — ${ex.title}`;
    }

    // Live cluster banners
    if (state.elements.clusterTag) {
      state.elements.clusterTag.style.display = ex.requires_cluster ? "inline-flex" : "none";
    }
    if (state.elements.clusterBanner) {
      state.elements.clusterBanner.style.display = ex.requires_cluster ? "flex" : "none";
      if (state.elements.clusterBannerEx) {
        state.elements.clusterBannerEx.textContent = ex.id;
      }
    }

    // Load saved user code from localStorage
    const savedState = KubelingsStorage.getExerciseState(exerciseId, ex.starter_code);
    state.revealedHints = savedState.hintsRevealed || 0;
    renderHints();

    // Update Monaco editor code
    if (state.editor) {
      state.editor.setValue(savedState.userCode || ex.starter_code || "");
    }

    // If diff editor is active, update diff models
    if (state.isDiffMode && state.diffEditor && window.monaco) {
      updateDiffModels();
    }

    // Update Next/Prev buttons
    updateStepperButtons();

    // Refresh syllabus tree highlight
    renderSyllabusTree();

    // Welcome terminal message
    if (state.elements.output) {
      state.elements.output.innerHTML = `
<span class="term-banner-info">📚 Loaded exercise: <strong>${escapeHtml(ex.id)}</strong> — ${escapeHtml(ex.title)}</span>
<span class="term-dim">Fix the manifest issues in the editor, then click </span><span class="term-pass">▶ Run Solution</span><span class="term-dim"> (Ctrl+Enter).</span>
`;
    }
  }

  function getOrderedExerciseList() {
    if (!state.bundle || !state.bundle.chapters) return [];
    const list = [];
    for (const ch of state.bundle.chapters) {
      if (ch.exercise_ids) {
        list.push(...ch.exercise_ids);
      }
    }
    return list;
  }

  function updateStepperButtons() {
    const list = getOrderedExerciseList();
    const idx = list.indexOf(state.currentExerciseId);

    if (state.elements.prevBtn) {
      state.elements.prevBtn.disabled = idx <= 0;
    }
    if (state.elements.nextBtn) {
      state.elements.nextBtn.disabled = idx < 0 || idx >= list.length - 1;
    }
  }

  function goToPreviousExercise() {
    const list = getOrderedExerciseList();
    const idx = list.indexOf(state.currentExerciseId);
    if (idx > 0) {
      selectExercise(list[idx - 1]);
    }
  }

  function goToNextExercise() {
    const list = getOrderedExerciseList();
    const idx = list.indexOf(state.currentExerciseId);
    if (idx >= 0 && idx < list.length - 1) {
      selectExercise(list[idx + 1]);
    }
  }

  /**
   * Render hint drawer cards.
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

  function toggleHint() {
    const ex = state.bundle && state.bundle.exercises[state.currentExerciseId];
    const hints = (ex && ex.hints) || [];
    if (hints.length === 0) return;

    if (state.revealedHints >= hints.length) {
      state.revealedHints = 0;
    } else {
      state.revealedHints++;
    }
    KubelingsStorage.setHintsRevealed(state.currentExerciseId, state.revealedHints);
    renderHints();
  }

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

  function resetEditorCode() {
    const ex = state.bundle && state.bundle.exercises[state.currentExerciseId];
    if (!ex || !state.editor) return;

    state.editor.setValue(ex.starter_code || "");
    KubelingsStorage.resetExercise(state.currentExerciseId, ex.starter_code);
    state.revealedHints = 0;
    renderHints();
    renderSyllabusTree();
    updateProgressUI();

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

  function handleRunResult(result) {
    state.isRunning = false;

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
      KubelingsStorage.markCompleted(result.exerciseId, state.bundle);
      updateProgressUI();
      renderSyllabusTree();

      const list = getOrderedExerciseList();
      const currentIdx = list.indexOf(result.exerciseId);
      const hasNext = currentIdx >= 0 && currentIdx < list.length - 1;
      const nextId = hasNext ? list[currentIdx + 1] : null;

      let outputHtml = `
<span class="term-banner-pass">✓ PASSED (${duration} ms) — Exercise '${escapeHtml(result.exerciseId)}' validated successfully!</span>
`;
      if (result.output) {
        outputHtml += `<span class="term-pass">${ansiToHtml(result.output)}</span>\n`;
      }
      outputHtml += `
<span class="term-dim">✨ All schema constraints and assertions passed in client-side WebAssembly!</span>
`;
      if (hasNext && nextId) {
        outputHtml += `
\n<span class="term-bold term-info">👉 Ready for next challenge?</span> <button id="pg-inline-next-btn" class="term-inline-btn">Advance to ${escapeHtml(nextId)} →</button>
`;
      } else {
        outputHtml += `\n<span class="term-bold term-pass">🎉 CONGRATULATIONS! You have completed all 114 exercises in the curriculum!</span>`;
      }

      outEl.innerHTML = outputHtml;

      const inlineNext = outEl.querySelector("#pg-inline-next-btn");
      if (inlineNext) {
        inlineNext.addEventListener("click", goToNextExercise);
      }
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
   * Setup Web Worker with Pyodide.
   */
  async function initWorker() {
    const workerUrl = resolveAssetUrl("playground-worker.js");
    let worker;

    try {
      worker = new Worker(workerUrl);
    } catch (e) {
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
<span class="term-banner-info">🚀 Kubelings WebAssembly Learning Platform Ready (Python 3.12 + PyYAML)</span>
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

    worker.postMessage({
      type: "INIT",
      bundle: state.bundle,
    });
  }

  async function loadBundle() {
    const candidateUrls = [
      resolveAssetUrl("playground-bundle.json"),
      "assets/playground/playground-bundle.json",
      "/assets/playground/playground-bundle.json",
      "../assets/playground/playground-bundle.json",
      "docs/assets/playground/playground-bundle.json",
    ];

    for (const url of candidateUrls) {
      try {
        const resp = await fetch(url);
        if (resp.ok) {
          const bundle = await resp.json();
          if (bundle && bundle.exercises) {
            return bundle;
          }
        }
      } catch (e) {
        // Continue trying fallback paths
      }
    }
    throw new Error("Could not load playground-bundle.json from any known path.");
  }

  function initMonaco() {
    if (state.monacoLoaded || !window.monaco) return;
    state.monacoLoaded = true;

    const editorEl = state.elements.editorContainer;
    const diffEl = state.elements.diffContainer;
    if (!editorEl || !diffEl) return;

    const theme = getMonacoTheme();
    const ex = state.bundle && state.bundle.exercises[state.currentExerciseId];
    const initialCode = KubelingsStorage.getExerciseState(state.currentExerciseId, ex ? ex.starter_code : "").userCode;

    state.editor = window.monaco.editor.create(editorEl, {
      value: initialCode,
      language: "python",
      theme: theme,
      automaticLayout: true,
      fontSize: 13,
      lineNumbers: "on",
      minimap: { enabled: false },
      scrollBeyondLastLine: false,
      tabSize: 4,
      insertSpaces: true,
      renderWhitespace: "selection",
      folding: true,
    });

    state.editor.onDidChangeModelContent(() => {
      const code = state.editor.getValue();
      KubelingsStorage.saveExerciseCode(state.currentExerciseId, code);
      renderSyllabusTree();
      if (state.isDiffMode) {
        updateDiffModels();
      }
    });

    state.editor.addCommand(
      window.monaco.KeyMod.CtrlCmd | window.monaco.KeyCode.Enter,
      runCurrentExercise
    );

    state.diffEditor = window.monaco.editor.createDiffEditor(diffEl, {
      theme: theme,
      automaticLayout: true,
      fontSize: 13,
      readOnly: true,
      renderSideBySide: true,
      minimap: { enabled: false },
      scrollBeyondLastLine: false,
    });
  }

  function loadMonacoScript() {
    if (window.monaco) {
      initMonaco();
      return;
    }

    if (window.require && typeof window.require === "function") {
      window.require.config({
        paths: {
          vs: "https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.45.0/min/vs",
        },
      });
      window.require(["vs/editor/editor.main"], function () {
        initMonaco();
      });
      return;
    }

    const loaderScript = document.createElement("script");
    loaderScript.src = "https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.45.0/min/vs/loader.min.js";
    loaderScript.onload = function () {
      window.require.config({
        paths: {
          vs: "https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.45.0/min/vs",
        },
      });
      window.require(["vs/editor/editor.main"], function () {
        initMonaco();
      });
    };
    document.head.appendChild(loaderScript);
  }

  function attachEventHandlers() {
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
    if (state.elements.prevBtn) {
      state.elements.prevBtn.addEventListener("click", goToPreviousExercise);
    }
    if (state.elements.nextBtn) {
      state.elements.nextBtn.addEventListener("click", goToNextExercise);
    }

    // Search filter input
    if (state.elements.searchInput) {
      state.elements.searchInput.addEventListener("input", (e) => {
        state.searchQuery = e.target.value;
        renderSyllabusTree();
      });
    }

    // Filter tabs (All, To Do, Done)
    if (state.elements.filterTabs) {
      state.elements.filterTabs.forEach((tab) => {
        tab.addEventListener("click", () => {
          state.elements.filterTabs.forEach((t) => t.classList.remove("active"));
          tab.classList.add("active");
          state.sidebarFilter = tab.getAttribute("data-filter") || "all";
          renderSyllabusTree();
        });
      });
    }

    // Export progress JSON
    if (state.elements.exportBtn) {
      state.elements.exportBtn.addEventListener("click", () => {
        const json = KubelingsStorage.exportJSON();
        const blob = new Blob([json], { type: "application/json" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        const date = new Date().toISOString().slice(0, 10);
        a.href = url;
        a.download = `kubelings-progress-${date}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      });
    }

    // Import progress JSON
    if (state.elements.importBtn && state.elements.importFile) {
      state.elements.importBtn.addEventListener("click", () => {
        state.elements.importFile.click();
      });
      state.elements.importFile.addEventListener("change", (e) => {
        const file = e.target.files && e.target.files[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = (evt) => {
          const content = evt.target.result;
          if (KubelingsStorage.importJSON(content, state.bundle)) {
            updateProgressUI();
            selectExercise(KubelingsStorage.state.lastActiveExerciseId || "pods01");
            alert("✓ Progress backup successfully restored!");
          } else {
            alert("❌ Failed to restore progress: invalid backup file.");
          }
        };
        reader.readAsText(file);
        e.target.value = "";
      });
    }

    // Reset All Progress
    if (state.elements.resetAllBtn) {
      state.elements.resetAllBtn.addEventListener("click", () => {
        if (confirm("⚠️ Are you sure you want to reset ALL progress across all 114 exercises? This cannot be undone.")) {
          KubelingsStorage.resetAll(state.bundle);
          updateProgressUI();
          selectExercise("pods01");
        }
      });
    }

    function toggleFullscreen() {
      const container = state.container;
      if (!container) return;

      const isFsNative = !!(document.fullscreenElement || document.webkitFullscreenElement);
      const isFsClass = container.classList.contains("is-fullscreen");

      if (isFsNative) {
        if (document.exitFullscreen) {
          document.exitFullscreen().catch(() => {});
        } else if (document.webkitExitFullscreen) {
          document.webkitExitFullscreen();
        }
      } else if (isFsClass) {
        container.classList.remove("is-fullscreen");
        if (state.elements.fullscreenBtn) {
          state.elements.fullscreenBtn.textContent = "⛶ Fullscreen";
        }
        setTimeout(() => {
          if (state.editor) state.editor.layout();
          if (state.diffEditor) state.diffEditor.layout();
        }, 100);
      } else {
        if (container.requestFullscreen) {
          container.requestFullscreen().catch(() => {
            container.classList.add("is-fullscreen");
            if (state.elements.fullscreenBtn) {
              state.elements.fullscreenBtn.textContent = "✕ Exit Fullscreen";
            }
            setTimeout(() => {
              if (state.editor) state.editor.layout();
              if (state.diffEditor) state.diffEditor.layout();
            }, 100);
          });
        } else if (container.webkitRequestFullscreen) {
          container.webkitRequestFullscreen();
        } else {
          container.classList.add("is-fullscreen");
          if (state.elements.fullscreenBtn) {
            state.elements.fullscreenBtn.textContent = "✕ Exit Fullscreen";
          }
          setTimeout(() => {
            if (state.editor) state.editor.layout();
            if (state.diffEditor) state.diffEditor.layout();
          }, 100);
        }
      }
    }

    const handleFsChange = () => {
      const isFs = !!(document.fullscreenElement || document.webkitFullscreenElement || (state.container && state.container.classList.contains("is-fullscreen")));
      if (state.elements.fullscreenBtn) {
        state.elements.fullscreenBtn.textContent = isFs ? "✕ Exit Fullscreen" : "⛶ Fullscreen";
      }
      setTimeout(() => {
        if (state.editor) state.editor.layout();
        if (state.diffEditor) state.diffEditor.layout();
      }, 100);
      setTimeout(() => {
        if (state.editor) state.editor.layout();
        if (state.diffEditor) state.diffEditor.layout();
      }, 300);
    };

    document.addEventListener("fullscreenchange", handleFsChange);
    document.addEventListener("webkitfullscreenchange", handleFsChange);

    if (state.elements.fullscreenBtn) {
      state.elements.fullscreenBtn.addEventListener("click", toggleFullscreen);
    }

    // Keyboard shortcuts
    document.addEventListener("keydown", (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
        e.preventDefault();
        runCurrentExercise();
      } else if (e.altKey && e.key === "ArrowLeft") {
        e.preventDefault();
        goToPreviousExercise();
      } else if (e.altKey && e.key === "ArrowRight") {
        e.preventDefault();
        goToNextExercise();
      } else if (e.key === "F11") {
        e.preventDefault();
        toggleFullscreen();
      } else if (e.key === "Escape" && state.container && state.container.classList.contains("is-fullscreen")) {
        toggleFullscreen();
      }
    });

    // Theme synchronization with MkDocs Material
    const observer = new MutationObserver(() => {
      const theme = getMonacoTheme();
      if (window.monaco && state.editor) {
        window.monaco.editor.setTheme(theme);
      }
      if (window.monaco && state.diffEditor) {
        window.monaco.editor.setTheme(theme);
      }
    });
    observer.observe(document.body, {
      attributes: true,
      attributeFilter: ["data-md-color-scheme"],
    });
  }

  /**
   * Main entry point.
   */
  async function initPlayground() {
    const container = document.getElementById("kubelings-playground");
    if (!container) return;
    state.container = container;

    renderPlaygroundSkeleton(container);
    bindElements(container);
    attachEventHandlers();

    try {
      updateStatus("loading", "⚡ Loading 114-exercise curriculum bundle...");
      state.bundle = await loadBundle();
      KubelingsStorage.init(state.bundle);

      const startExId = KubelingsStorage.state.lastActiveExerciseId || "pods01";
      state.currentExerciseId = state.bundle.exercises[startExId] ? startExId : "pods01";

      updateProgressUI();
      renderSyllabusTree();
      selectExercise(state.currentExerciseId);

      loadMonacoScript();
      await initWorker();
    } catch (err) {
      updateStatus("error", "Initialization failed: " + err.message);
      if (state.elements.output) {
        state.elements.output.innerHTML = `<span class="term-banner-fail">❌ Failed to initialize playground: ${escapeHtml(err.message)}</span>`;
      }
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initPlayground);
  } else {
    initPlayground();
  }
})();

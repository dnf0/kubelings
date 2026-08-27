/**
 * Web Worker for Kubelings Pyodide WebAssembly Runtime.
 *
 * Runs Pyodide v0.26+ in a background Web Worker, loads PyYAML, mounts the
 * in-memory Kubelings schema validator and models, and provides a sandboxed
 * execution environment with captured stdout and millisecond-level timing.
 */

/* global loadPyodide, importScripts */
importScripts("https://cdn.jsdelivr.net/pyodide/v0.26.2/full/pyodide.js");

let pyodide = null;
let bundleData = null;

/**
 * Initialize Pyodide WebAssembly runtime and mount Kubelings virtual modules.
 * @param {Object} bundle - Playground bundle containing models_code and validator_code.
 */
async function initPyodide(bundle) {
  bundleData = bundle;
  self.postMessage({
    type: "STATUS",
    stage: "loading_pyodide",
    message: "⚡ Initializing Python WebAssembly Runtime..."
  });

  pyodide = await loadPyodide({
    indexURL: "https://cdn.jsdelivr.net/pyodide/v0.26.2/full/"
  });

  self.postMessage({
    type: "STATUS",
    stage: "installing_packages",
    message: "📦 Loading PyYAML pure-Python engine..."
  });
  await pyodide.loadPackage(["pyyaml"]);

  self.postMessage({
    type: "STATUS",
    stage: "mounting_bundle",
    message: "🔧 Mounting Kubelings Schema Validator..."
  });

  // Create /lib/kubelings virtual package in Pyodide FS
  pyodide.FS.mkdirTree("/lib/kubelings");
  pyodide.FS.writeFile("/lib/kubelings/__init__.py", "");
  pyodide.FS.writeFile("/lib/kubelings/models.py", (bundle && bundle.models_code) || "");
  pyodide.FS.writeFile("/lib/kubelings/validator.py", (bundle && bundle.validator_code) || "");

  // Setup Python sys.path and in-memory test runner
  await pyodide.runPythonAsync(`
import sys
import io
import time
import importlib
import traceback

if "/lib" not in sys.path:
    sys.path.insert(0, "/lib")

import kubelings.validator as validator

def run_user_code(user_code_str, filename="exercise.py"):
    start_time = time.perf_counter()
    stdout_buf = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = stdout_buf
    
    global_env = {"__name__": "__main__"}
    try:
        exec(user_code_str, global_env)
        
        duration = (time.perf_counter() - start_time) * 1000
        output_str = stdout_buf.getvalue()
        return {
            "passed": True,
            "error": None,
            "output": output_str if output_str else "✓ Exercise passed all schema validations and assertions!",
            "durationMs": round(duration, 2)
        }
    except AssertionError as ae:
        duration = (time.perf_counter() - start_time) * 1000
        return {
            "passed": False,
            "error": str(ae) if str(ae) else "AssertionError: validation constraint failed",
            "output": stdout_buf.getvalue(),
            "durationMs": round(duration, 2)
        }
    except Exception as e:
        duration = (time.perf_counter() - start_time) * 1000
        tb = traceback.format_exc()
        return {
            "passed": False,
            "error": f"{type(e).__name__}: {e}",
            "traceback": tb,
            "output": stdout_buf.getvalue(),
            "durationMs": round(duration, 2)
        }
    finally:
        sys.stdout = old_stdout
`);

  self.postMessage({
    type: "STATUS",
    stage: "ready",
    message: "✅ Ready! Python 3.12 WebAssembly loaded."
  });
}

self.onmessage = async function(e) {
  const msg = e.data;
  if (!msg || !msg.type) return;

  if (msg.type === "INIT") {
    try {
      await initPyodide(msg.bundle || {});
    } catch (err) {
      self.postMessage({
        type: "STATUS",
        stage: "error",
        message: "Error initializing Pyodide: " + (err && err.message ? err.message : String(err))
      });
    }
  } else if (msg.type === "RUN_EXERCISE") {
    if (!pyodide) {
      self.postMessage({
        type: "RUN_RESULT",
        exerciseId: msg.exerciseId,
        passed: false,
        error: "Pyodide is still initializing...",
        output: "",
        durationMs: 0
      });
      return;
    }

    try {
      pyodide.globals.set("temp_code_str", msg.code || "");
      pyodide.globals.set("temp_filename", msg.filename || "exercise.py");

      const resProxy = await pyodide.runPythonAsync("run_user_code(temp_code_str, temp_filename)");
      const resultObj = resProxy.toJs({ dict_converter: Object.fromEntries });
      resProxy.destroy();

      self.postMessage({
        type: "RUN_RESULT",
        exerciseId: msg.exerciseId,
        output: "",
        ...resultObj
      });
    } catch (err) {
      self.postMessage({
        type: "RUN_RESULT",
        exerciseId: msg.exerciseId,
        passed: false,
        error: "Execution Error: " + (err && err.message ? err.message : String(err)),
        output: "",
        durationMs: 0
      });
    }
  }
};

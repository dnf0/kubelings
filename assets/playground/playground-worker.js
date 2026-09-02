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

  // Create /lib/kubelings and /lib/kubelings/validators virtual package in Pyodide FS
  pyodide.FS.mkdirTree("/lib/kubelings/validators");
  pyodide.FS.writeFile("/lib/kubelings/__init__.py", "");
  pyodide.FS.writeFile("/lib/kubelings/models.py", (bundle && bundle.models_code) || "");
  pyodide.FS.writeFile("/lib/kubelings/validator.py", (bundle && bundle.validator_code) || "");

  if (bundle && bundle.validators_modules) {
    for (const [modName, modCode] of Object.entries(bundle.validators_modules)) {
      pyodide.FS.writeFile(`/lib/kubelings/validators/${modName}`, modCode);
    }
  }

  // Setup Python sys.path, import all chapter validators, and define in-memory evaluator
  await pyodide.runPythonAsync(`
import os
import sys
import io
import time
import importlib
import traceback

if "/lib" not in sys.path:
    sys.path.insert(0, "/lib")

import yaml
import kubelings.validator as validator
from kubelings.validator import ManifestValidationError
import kubelings.validators as validators_pkg
from kubelings.validators import get_validator, _VALIDATORS

# Explicitly import every chapter module in /lib/kubelings/validators to ensure registry is populated
val_dir = "/lib/kubelings/validators"
if os.path.exists(val_dir):
    for fname in sorted(os.listdir(val_dir)):
        if fname.endswith(".py") and fname != "__init__.py":
            mod_name = fname[:-3]
            try:
                importlib.import_module(f"kubelings.validators.{mod_name}")
            except Exception as e:
                print(f"Warning importing {mod_name}: {e}")

INCOMPLETE_MARKERS = (
    "???",
    "___",
    "/* ??? */",
    "<!-- ANSWER -->",
    "I AM NOT DONE",
)

def format_yaml_error(err, filename):
    mark = getattr(err, "problem_mark", None)
    if mark is not None:
        line = mark.line + 1
        col = mark.column + 1
        problem = getattr(err, "problem", str(err))
        return f"❌ YAML Syntax Error in {filename}:\\n   Line {line}, Column {col}: {problem}"
    return f"❌ YAML Syntax Error in {filename}:\\n   {err}"

def run_exercise_eval(exercise_id, code_str, filename="exercise.yaml"):
    start_time = time.perf_counter()
    stdout_buf = io.StringIO()
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    sys.stdout = stdout_buf
    sys.stderr = stdout_buf
    
    try:
        if filename.endswith((".yaml", ".yml")):
            # 1. Check placeholder markers
            if any(marker in code_str for marker in INCOMPLETE_MARKERS):
                duration = (time.perf_counter() - start_time) * 1000.0
                return {
                    "passed": False,
                    "error": "Exercise still contains incomplete placeholder markers ('???'). Fill them in to complete the exercise.",
                    "output": stdout_buf.getvalue(),
                    "durationMs": round(duration, 2),
                }
            
            # 2. Parse YAML
            try:
                parsed_docs = list(yaml.safe_load_all(code_str))
            except yaml.YAMLError as exc:
                duration = (time.perf_counter() - start_time) * 1000.0
                return {
                    "passed": False,
                    "error": format_yaml_error(exc, filename),
                    "output": stdout_buf.getvalue(),
                    "durationMs": round(duration, 2),
                }
            
            docs = [d for d in parsed_docs if d is not None]
            manifest = docs[0] if len(docs) == 1 else (docs if len(docs) > 1 else {})
            
            # 3. Retrieve registered validator
            val_fn = get_validator(exercise_id)
            if val_fn is None:
                duration = (time.perf_counter() - start_time) * 1000.0
                return {
                    "passed": False,
                    "error": f"No validator registered for exercise '{exercise_id}'",
                    "output": stdout_buf.getvalue(),
                    "durationMs": round(duration, 2),
                }
            
            # 4. Run validator assertion
            val_fn(manifest, code_str)
            
            duration = (time.perf_counter() - start_time) * 1000.0
            output_str = stdout_buf.getvalue()
            return {
                "passed": True,
                "error": None,
                "output": output_str if output_str else f"✓ Exercise '{exercise_id}' passed all Kubernetes schema validations and assertions!",
                "durationMs": round(duration, 2),
            }
        else:
            # Python script exercise
            global_env = {"__name__": "__main__"}
            exec(code_str, global_env)
            duration = (time.perf_counter() - start_time) * 1000.0
            output_str = stdout_buf.getvalue()
            return {
                "passed": True,
                "error": None,
                "output": output_str if output_str else f"✓ Exercise '{exercise_id}' executed successfully!",
                "durationMs": round(duration, 2),
            }
    except (AssertionError, ManifestValidationError) as exc:
        duration = (time.perf_counter() - start_time) * 1000.0
        err_msg = str(exc)
        return {
            "passed": False,
            "error": err_msg if err_msg else "Validation constraint failed",
            "output": stdout_buf.getvalue(),
            "durationMs": round(duration, 2),
        }
    except BaseException as e:
        duration = (time.perf_counter() - start_time) * 1000.0
        tb = traceback.format_exc()
        return {
            "passed": False,
            "error": f"{type(e).__name__}: {e}",
            "traceback": tb,
            "output": stdout_buf.getvalue(),
            "durationMs": round(duration, 2),
        }
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr
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

    let resProxy = null;
    try {
      pyodide.globals.set("temp_exercise_id", msg.exerciseId || "");
      pyodide.globals.set("temp_code_str", msg.code || "");
      pyodide.globals.set("temp_filename", msg.filename || "exercise.yaml");

      resProxy = await pyodide.runPythonAsync("run_exercise_eval(temp_exercise_id, temp_code_str, temp_filename)");
      const resultObj = resProxy.toJs({ dict_converter: Object.fromEntries });

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
    } finally {
      if (resProxy && typeof resProxy.destroy === "function") {
        resProxy.destroy();
      }
    }
  }
};

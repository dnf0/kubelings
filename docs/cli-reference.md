# CLI Reference

Kubelings is powered by a high-performance CLI built on [Typer](https://typer.tiangolo.com/) and [Rich](https://github.com/Textualize/rich).

---

## `kubelings tour`

Launch the rich, 5-step interactive onboarding tour for new learners with live environment probes and guided exercise walkthrough.

```bash
kubelings tour [OPTIONS]
```

**Options:**
- `--step`, `-s` `INTEGER`: Jump directly to a specific tour step (1–5).
- `--non-interactive`: Run through all steps sequentially without waiting for interactive keypresses.
- `--json`: Output tour step metadata and structure in JSON format.

**Examples:**
```bash
kubelings tour
kubelings tour --step 4
kubelings tour --non-interactive
kubelings tour --json
```

---

## `kubelings watch`

Launch the continuous file-watching learning loop.

```bash
kubelings watch [OPTIONS]
```

**Options:**
- `--start`, `-s` `TEXT`: Exercise name to start watching from (e.g. `pods01`).

---

## `kubelings run`

Run and evaluate a specific exercise directly.

```bash
kubelings run <EXERCISE_NAME_OR_PATH>
```

**Examples:**
```bash
kubelings run pods01
kubelings run exercises/02_controllers/ctrl03.py
```

---

## `kubelings hint`

Display progressive hints for an exercise.

```bash
kubelings hint <EXERCISE_NAME_OR_PATH> [OPTIONS]
```

**Options:**
- `--hint-num`, `-n` `INTEGER`: Specific hint tier index to display (1, 2, 3...).

---

## `kubelings list`

Display the complete curriculum syllabus table with chapter breakdowns and exercise counts.

```bash
kubelings list
```

---

## `kubelings verify`

Evaluate the entire curriculum in memory and display a comprehensive pass/fail progress dashboard.

```bash
kubelings verify
```

---

## `kubelings test`

Verify reference solutions across all curriculum exercises or filter by chapter/exercise.

```bash
kubelings test [OPTIONS]
```

**Options:**
- `--chapter`, `-c` `TEXT`: Specific chapter name to test (e.g. `01_pods`).
- `--exercise`, `-e` `TEXT`: Specific exercise name to test (e.g. `pods01`).
- `--max-exercises`, `-m` `INTEGER`: Limit maximum number of exercises to test.

---

## `kubelings cluster`

Inspect Kubernetes cluster connectivity status and active context.

```bash
kubelings cluster
```

---

## `kubelings init`

Scaffold the standard curriculum exercises directory in any local workspace.

```bash
kubelings init [OPTIONS]
```

**Options:**
- `--dir`, `-d` `TEXT`: Target directory to initialize exercises in (defaults to `./exercises`).
- `--force`, `-f`: Overwrite existing files in the target directory.

---

## `kubelings reset`

Reset an exercise file back to its clean starter template.

```bash
kubelings reset <EXERCISE_NAME_OR_PATH>
```

---

## `kubelings tree`

Render an architectural relationship topology tree for Kubernetes resources.

```bash
kubelings tree [TARGET]
```

**Examples:**
```bash
kubelings tree pods01
kubelings tree deployment.yaml
```

---

## `kubelings lint`

Evaluate Kubernetes YAML/JSON manifests against security, reliability, and schema best-practices.

```bash
kubelings lint <PATH>
```

**Examples:**
```bash
kubelings lint exercises/01_pods/pods01.yaml
kubelings lint manifests/production/
```

---

## `kubelings tui` / `kubelings dashboard`

Launch the full-screen interactive terminal dashboard to explore curriculum chapters, inspect code, and run evaluations.

```bash
kubelings tui
# or
kubelings dashboard
```

---

## `kubelings version`

Print the currently installed Kubelings package version.

```bash
kubelings version
```


"""
Automated Migration Script: Converts 114 Python-based exercises and solutions into
native YAML manifest files and generates modular validator files under src/kubelings/validators/.
"""

import ast
import importlib.util
import re
from pathlib import Path
from typing import Any, List, Set, Tuple

import yaml

from kubelings.manifest import build_manifest


def format_docstring_to_yaml_comments(docstring: str, file_path_str: str) -> str:
    """Format docstring to YAML comments at the top of a manifest."""
    if not docstring:
        return f"# Exercise: {file_path_str}\n\n"

    lines = docstring.strip().splitlines()
    formatted = []
    for line in lines:
        cleaned = re.sub(r"\.py\b", ".yaml", line)
        if cleaned.strip():
            formatted.append(f"# {cleaned}")
        else:
            formatted.append("#")
    return "\n".join(formatted) + "\n\n"


def extract_manifest_str_from_module(mod_path: Path) -> Tuple[str, str]:
    """Extract docstring and raw YAML string from a Python module."""
    code = mod_path.read_text(encoding="utf-8")
    tree = ast.parse(code)
    docstring = ast.get_docstring(tree) or ""

    # Check top-level string constants (e.g. POD_MANIFEST, MANIFESTS, etc.)
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                        val = node.value.value.strip()
                        if any(
                            k in val
                            for k in (
                                "apiVersion:",
                                "kind:",
                                "metadata:",
                                "spec:",
                                "type: object",
                                "name:",
                            )
                        ):
                            return docstring, val

    # Check for inner manifest_yaml inside function
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            for inner in node.body:
                if isinstance(inner, ast.Assign):
                    for target in inner.targets:
                        if isinstance(target, ast.Name) and target.id in (
                            "manifest_yaml",
                            "manifest",
                        ):
                            if isinstance(inner.value, ast.Constant) and isinstance(
                                inner.value.value, str
                            ):
                                return docstring, inner.value.value.strip()

    return docstring, ""


def get_solution_manifest(sol_py_path: Path) -> Tuple[str, str]:
    """Get the solution docstring and YAML string from a solution .py file."""
    docstring, raw_yaml = extract_manifest_str_from_module(sol_py_path)
    if raw_yaml:
        return docstring, raw_yaml

    # Load module dynamically and call generator function if present
    spec = importlib.util.spec_from_file_location(f"sol_{sol_py_path.stem}", str(sol_py_path))
    if spec and spec.loader:
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        for attr_name in dir(mod):
            if attr_name in ("verify",) or attr_name.startswith("_"):
                continue
            attr = getattr(mod, attr_name)
            if callable(attr):
                try:
                    if attr_name == "build_admission_review_response":
                        res = attr("test-uid-123")
                    elif attr_name == "render_deployment":
                        values = {
                            "Chart": {"Name": "web"},
                            "Release": {"Name": "prod"},
                            "replicaCount": 3,
                            "image": {"repository": "nginx", "tag": "1.25-alpine"},
                            "service": {"port": 8080},
                        }
                        res = attr(values)
                    else:
                        res = attr()

                    if isinstance(res, (dict, list)):
                        if isinstance(res, list) and all(isinstance(x, dict) for x in res):
                            # Multi-doc
                            dumped = "\n---\n".join(
                                yaml.safe_dump(doc, sort_keys=False) for doc in res
                            )
                            return docstring, dumped.strip()
                        else:
                            dumped = yaml.safe_dump(res, sort_keys=False)
                            return docstring, dumped.strip()
                except Exception:
                    pass

    return docstring, ""


def mask_solution_to_starter(sol_yaml: str) -> str:
    """Mask concrete values in a YAML string with ??? to make a starter template."""

    def mask_value(val: Any, key_name: str = "") -> Any:
        if isinstance(val, dict):
            res = {}
            for k, v in val.items():
                if k in ("apiVersion", "kind"):
                    res[k] = v
                elif k == "name" and key_name == "metadata":
                    res[k] = "???"
                else:
                    res[k] = mask_value(v, k)
            return res
        elif isinstance(val, list):
            return [mask_value(x, key_name) for x in val]
        else:
            return "???"

    try:
        docs = list(yaml.safe_load_all(sol_yaml))
        masked_docs = [mask_value(d) for d in docs if d is not None]
        if len(masked_docs) > 1:
            return "\n---\n".join(yaml.safe_dump(d, sort_keys=False) for d in masked_docs).strip()
        elif len(masked_docs) == 1:
            return yaml.safe_dump(masked_docs[0], sort_keys=False).strip()
    except Exception:
        pass
    return "# ???\n"


def get_starter_manifest(ex_py_path: Path, sol_yaml: str) -> Tuple[str, str]:
    """Get starter docstring and starter YAML content."""
    docstring, raw_yaml = extract_manifest_str_from_module(ex_py_path)
    if raw_yaml and ("???" in raw_yaml or "TODO" in raw_yaml):
        return docstring, raw_yaml

    code = ex_py_path.read_text(encoding="utf-8")
    tree = ast.parse(code)
    docstring = ast.get_docstring(tree) or ""

    starter_yaml = mask_solution_to_starter(sol_yaml)
    return docstring, starter_yaml


GENERATOR_FUNCTIONS = {
    "get_argocd_application_manifest",
    "get_applicationset_manifest",
    "get_sync_policy_manifest",
    "get_rollout_manifest",
    "get_cilium_l7_policy",
    "get_peer_authentication_manifest",
    "get_clusterwide_egress_policy",
    "get_observable_pod_manifest",
    "get_kyverno_policy_manifest",
    "get_kyverno_mutation_manifest",
    "get_kyverno_generate_manifest",
    "get_gatekeeper_template_manifest",
    "get_subnamespace_anchor_manifest",
    "get_tenant_isolation_manifests",
    "get_vcluster_manifest",
    "get_tenant_network_isolation_policy",
    "get_mutating_webhook_manifest",
    "get_validating_webhook_manifest",
    "build_admission_review_response",
    "get_crd_conversion_manifest",
    "get_chart_metadata",
    "render_deployment",
    "get_values_schema",
    "get_parent_values",
    "get_kustomization_base",
    "get_generator_kustomization",
    "get_patch_kustomization",
    "get_prod_overlay",
    "build_gateway_resources",
    "build_http_route",
    "build_canary_route",
    "build_reference_grant",
    "build_xrd",
    "build_composition",
    "build_provider_and_resource",
    "build_developer_claim",
    "build_tracing_policy",
    "build_file_monitor_policy",
    "build_enforcement_policy",
    "build_socket_tracing_policy",
}


def convert_verify_body(body_nodes: List[ast.stmt], ex_name: str) -> List[str]:
    """Transform AST statements inside verify() or if __name__ == '__main__': into validator body."""
    lines: List[str] = []

    for stmt in body_nodes:
        # Filter out print(...) statements
        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
            if isinstance(stmt.value.func, ast.Name) and stmt.value.func.id == "print":
                continue

        # Filter out / adapt assignments
        if isinstance(stmt, ast.Assign):
            target_ids = [t.id for t in stmt.targets if isinstance(t, ast.Name)]
            val_unparsed = ast.unparse(stmt.value)

            if ex_name == "helm02" and target_ids == ["values"]:
                continue

            # Check safe_load_all
            if "safe_load_all" in val_unparsed:
                if target_ids:
                    lines.append(
                        f"{target_ids[0]} = manifest if isinstance(manifest, list) else [manifest]"
                    )
                    continue

            # Check safe_load of manifest string constants (e.g. POD_MANIFEST, MANIFEST, etc.)
            if "safe_load" in val_unparsed and any(k in val_unparsed for k in ("MANIFEST",)):
                if target_ids:
                    if target_ids[0] == "mutated":
                        lines.append("mutated = copy.deepcopy(manifest)")
                    elif target_ids[0] != "manifest":
                        lines.append(f"{target_ids[0]} = manifest")
                    continue

            # Check generator function calls
            for gen_fn in GENERATOR_FUNCTIONS:
                if gen_fn in val_unparsed:
                    if target_ids:
                        lines.append(f"{target_ids[0]} = manifest")
                        break
            else:
                pass
            if any(gen_fn in val_unparsed for gen_fn in GENERATOR_FUNCTIONS):
                continue

        # Unparse statement
        code_line = ast.unparse(stmt)
        # Replace validate_manifest_text(XXX_MANIFEST, ...) with validate_manifest_text(raw_yaml, ...)
        code_line = re.sub(
            r"validate_manifest_text\([A-Za-z0-9_]+,\s*",
            "validate_manifest_text(raw_yaml, ",
            code_line,
        )
        lines.append(code_line)

    return lines


def extract_helper_functions_and_verify(
    sol_py_path: Path, ex_name: str
) -> Tuple[List[Tuple[str, str]], List[str]]:
    """Extract helper functions, constants, and verification statements from solution .py."""
    code = sol_py_path.read_text(encoding="utf-8")
    tree = ast.parse(code)

    helper_funcs: List[Tuple[str, str]] = []
    verify_body: List[str] = []

    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            if node.name == "verify":
                verify_body = convert_verify_body(node.body, ex_name)
            else:
                # Helper function
                helper_funcs.append((node.name, ast.unparse(node)))
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            # Check if this is a helper constant like DEBUG_EPHEMERAL_CONTAINER
            target_name = ""
            if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
                target_name = node.targets[0].id
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                target_name = node.target.id
            if target_name and not target_name.endswith("_MANIFEST") and target_name != "MANIFEST":
                helper_funcs.append((target_name, ast.unparse(node)))
        elif isinstance(node, ast.If) and isinstance(node.test, ast.Compare):
            # Check for if __name__ == '__main__':
            test_str = ast.unparse(node.test)
            if "__name__" in test_str and "__main__" in test_str:
                # If verify() wasn't defined, verify statements are here
                if not verify_body:
                    verify_body = convert_verify_body(node.body, ex_name)

    return helper_funcs, verify_body


def main():
    repo_root = Path(__file__).resolve().parent.parent
    manifest_model = build_manifest()

    val_dir = repo_root / "src" / "kubelings" / "validators"
    val_dir.mkdir(parents=True, exist_ok=True)

    print(
        f"Processing {len(manifest_model.chapters)} chapters ({len(manifest_model.all_exercises)} exercises)..."
    )

    # Track files to delete
    py_files_to_delete = []

    for chapter in manifest_model.chapters:
        ch_num = f"{chapter.number:02d}"
        ch_slug = chapter.name.split("_", 1)[1] if "_" in chapter.name else chapter.name
        val_module_name = f"ch{ch_num}_{ch_slug}.py"
        val_file_path = val_dir / val_module_name

        print(
            f"Building validator module {val_module_name} for Chapter {chapter.number:02d} ({chapter.name})..."
        )

        module_code_parts: List[str] = [
            f'"""\nValidators for Chapter {chapter.number:02d}: {chapter.title}\n"""\n',
            "import base64",
            "import copy",
            "import ipaddress",
            "import json",
            "import re",
            "from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union",
            "import jsonschema",
            "import yaml",
            "from kubelings.validator import validate_manifest, validate_manifests, validate_manifest_text",
            "from kubelings.validators import register_validator\n\n",
        ]

        seen_helpers: Set[str] = set()

        for ex in chapter.exercises:
            ex_py_path = repo_root / ex.path
            sol_py_path = repo_root / ex.solution_path

            ex_yaml_path = repo_root / "exercises" / chapter.name / f"{ex.name}.yaml"
            sol_yaml_path = repo_root / "solutions" / chapter.name / f"{ex.name}.yaml"

            # Extract solution YAML & docstring
            sol_doc, sol_yaml = get_solution_manifest(sol_py_path)
            # Extract starter YAML & docstring
            ex_doc, starter_yaml = get_starter_manifest(ex_py_path, sol_yaml)

            # Write exercise YAML
            ex_header = format_docstring_to_yaml_comments(
                ex_doc, f"exercises/{chapter.name}/{ex.name}.yaml"
            )
            ex_yaml_path.parent.mkdir(parents=True, exist_ok=True)
            ex_yaml_path.write_text(ex_header + starter_yaml + "\n", encoding="utf-8")

            # Write solution YAML
            sol_header = format_docstring_to_yaml_comments(
                sol_doc, f"solutions/{chapter.name}/{ex.name}.yaml"
            )
            sol_yaml_path.parent.mkdir(parents=True, exist_ok=True)
            sol_yaml_path.write_text(sol_header + sol_yaml + "\n", encoding="utf-8")

            # Extract helper functions and validator body
            helper_funcs, verify_body = extract_helper_functions_and_verify(sol_py_path, ex.name)

            for hf_name, hf_code in helper_funcs:
                if hf_name not in seen_helpers:
                    seen_helpers.add(hf_name)
                    module_code_parts.append(hf_code + "\n\n")

            # Create validator function
            module_code_parts.append(f'@register_validator("{ex.name}")')
            module_code_parts.append(
                f'def validate_{ex.name}(manifest: Any, raw_yaml: str = "") -> None:'
            )
            if not verify_body:
                module_code_parts.append("    pass\n\n")
            else:
                for line in verify_body:
                    # Indent each line
                    indented = "\n".join(
                        "    " + line_str if line_str.strip() else ""
                        for line_str in line.splitlines()
                    )
                    module_code_parts.append(indented)
                module_code_parts.append("\n\n")

            py_files_to_delete.extend([ex_py_path, sol_py_path])

        # Write validator module
        val_file_path.write_text("\n".join(module_code_parts), encoding="utf-8")
        print(f"✓ Created {val_file_path}")

    # Delete old .py files in exercises and solutions
    print(f"Deleting {len(py_files_to_delete)} old .py files...")
    for p in py_files_to_delete:
        if p.exists():
            p.unlink()

    print("✓ Conversion script finished successfully!")


if __name__ == "__main__":
    main()

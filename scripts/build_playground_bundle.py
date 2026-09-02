#!/usr/bin/env python3
"""Build script to bundle Kubelings validator, models, chapters, and all exercises

into a single JSON asset for the Pyodide WebAssembly browser playground.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# Ensure repository src is prioritized for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from kubelings import __version__
from kubelings.manifest import get_manifest


def build_bundle(repo_root: Path | None = None) -> dict[str, Any]:
    """Extract validator code, models, chapters, and all exercises into a bundle dictionary."""
    if repo_root is None:
        repo_root = Path(__file__).resolve().parent.parent

    validator_path = repo_root / "src" / "kubelings" / "validator.py"
    models_path = repo_root / "src" / "kubelings" / "models.py"

    if not validator_path.exists():
        raise FileNotFoundError(f"Validator file not found at {validator_path}")
    if not models_path.exists():
        raise FileNotFoundError(f"Models file not found at {models_path}")

    validator_code = validator_path.read_text(encoding="utf-8")
    models_code = models_path.read_text(encoding="utf-8")

    manifest = get_manifest()

    chapters_data: list[dict[str, Any]] = []
    exercises_data: dict[str, Any] = {}

    for chapter in manifest.chapters:
        ch_exercise_ids = [ex.name for ex in chapter.exercises]
        chapters_data.append(
            {
                "number": chapter.number,
                "name": chapter.name,
                "title": chapter.title,
                "description": chapter.description,
                "exercise_ids": ch_exercise_ids,
            }
        )

        for manifest_ex in chapter.exercises:
            starter_path = repo_root / manifest_ex.file_path
            solution_path = repo_root / manifest_ex.solution_path

            if not starter_path.exists():
                raise FileNotFoundError(f"Starter exercise file not found at {starter_path}")
            if not solution_path.exists():
                raise FileNotFoundError(f"Solution exercise file not found at {solution_path}")

            starter_code = starter_path.read_text(encoding="utf-8")
            solution_code = solution_path.read_text(encoding="utf-8")

            exercises_data[manifest_ex.name] = {
                "id": manifest_ex.name,
                "title": manifest_ex.title,
                "chapter": manifest_ex.chapter_name,
                "chapter_number": chapter.number,
                "chapter_title": chapter.title,
                "filename": manifest_ex.file_path.name,
                "hints": manifest_ex.hints,
                "requires_cluster": manifest_ex.requires_cluster,
                "starter_code": starter_code,
                "solution_code": solution_code,
            }

    return {
        "version": __version__,
        "validator_code": validator_code,
        "models_code": models_code,
        "chapters": chapters_data,
        "exercises": exercises_data,
        "total_chapters": len(chapters_data),
        "total_exercises": len(exercises_data),
    }


def main() -> None:
    """Entry point for command line invocation."""
    parser = argparse.ArgumentParser(description="Build Kubelings Pyodide WebAssembly bundle")
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=None,
        help="Destination path for playground-bundle.json",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    if args.output:
        out_file = args.output
    else:
        out_dir = repo_root / "docs" / "assets" / "playground"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = out_dir / "playground-bundle.json"

    out_file.parent.mkdir(parents=True, exist_ok=True)
    bundle = build_bundle(repo_root)
    out_file.write_text(json.dumps(bundle, indent=2), encoding="utf-8")
    print(
        f"✓ Successfully generated playground bundle with {len(bundle['chapters'])} chapters and {len(bundle['exercises'])} exercises at {out_file}"
    )


if __name__ == "__main__":
    main()

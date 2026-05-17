#!/usr/bin/env python3
# this_file: validate.py
"""Validate every .vfj in corpus/ against the VFJ JSON Schema.

Usage:
    python validate.py [--schema PATH] [--corpus-dir PATH] [--quiet]

Default behaviour:
  - Uses the path passed via --schema or the VFJ_SCHEMA environment variable.
  - Runs a strict Draft 2020-12 JSON Schema validation pass. The historical
    KD-1..KD-22 lenient divergence catalog is closed; any schema error is now a
    real failure for this corpus gate.

Exit codes:
  0  all files pass strict schema validation
  1  one or more files fail
  2  schema not found (CI can use this to skip-with-notice)

Requirements:
    pip install jsonschema referencing
    (jsonschema >= 4.18 for draft-2020-12 support via referencing)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import NamedTuple

THIS = Path(__file__).resolve().parent


class ValidationResult(NamedTuple):
    """Result for one corpus file."""

    path: Path
    passed: bool
    errors: list[str]


def find_schema(explicit: str | None) -> Path | None:
    """Resolve the schema path from CLI or environment."""

    candidates: list[Path] = []
    if explicit:
        candidates.append(Path(explicit))
    env_schema = os.environ.get("VFJ_SCHEMA")
    if env_schema:
        candidates.append(Path(env_schema))

    for candidate in candidates:
        expanded = candidate.expanduser()
        if expanded.is_file():
            return expanded
    return None


def load_json(path: Path) -> object:
    """Load one JSON file and raise a contextual ValueError on parse failure."""

    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except json.JSONDecodeError as error:
        raise ValueError(f"JSON parse error at line {error.lineno}, column {error.colno}: {error.msg}") from error


def validate_file(path: Path, validator) -> ValidationResult:
    """Validate one VFJ file with strict schema semantics."""

    try:
        data = load_json(path)
    except ValueError as error:
        return ValidationResult(path=path, passed=False, errors=[str(error)])

    errors = sorted(validator.iter_errors(data), key=lambda item: item.path)
    messages: list[str] = []
    for error in errors:
        location = "/".join(str(part) for part in error.absolute_path) or "<root>"
        messages.append(f"{location}: {error.message}")
    return ValidationResult(path=path, passed=not messages, errors=messages)


def build_validator(schema_path: Path):
    """Build a Draft 2020-12 validator for the bundled VFJ schema."""

    import jsonschema

    with schema_path.open("r", encoding="utf-8") as handle:
        schema = json.load(handle)
    return jsonschema.Draft202012Validator(schema)


def iter_corpus_files(corpus_root: Path) -> list[Path]:
    """Return all corpus VFJ files in stable order."""

    return sorted(corpus_root.rglob("*.vfj"))


def parse_args(argv: list[str]) -> argparse.Namespace:
    """Parse CLI arguments."""

    parser = argparse.ArgumentParser(description="Validate VFJ corpus against JSON Schema")
    parser.add_argument("--schema", help="Path to vfj.bundle.schema.json")
    parser.add_argument(
        "--corpus-dir",
        default=str(THIS / "corpus"),
        help="Corpus root to scan recursively for .vfj files",
    )
    parser.add_argument("--quiet", action="store_true", help="Only print the final summary")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    """Validate the selected corpus and return a process exit code."""

    args = parse_args(argv)
    schema_path = find_schema(args.schema)
    if schema_path is None:
        print(
            "Schema not found. Set VFJ_SCHEMA or pass --schema with an explicit "
            "path to vfj.bundle.schema.json.",
            file=sys.stderr,
        )
        return 2

    corpus_root = Path(args.corpus_dir).expanduser()
    files = iter_corpus_files(corpus_root)
    if not files:
        print(f"No .vfj files found under {corpus_root}", file=sys.stderr)
        return 1

    validator = build_validator(schema_path)
    results = [validate_file(path, validator) for path in files]

    if not args.quiet:
        print(f"Schema: {schema_path}")
        print(f"Corpus: {corpus_root}")
        print("Mode: strict")
        for result in results:
            rel = result.path.relative_to(corpus_root) if result.path.is_relative_to(corpus_root) else result.path
            status = "PASS" if result.passed else "FAIL"
            print(f"{status} {rel}")
            for message in result.errors[:10]:
                print(f"  - {message}")
            if len(result.errors) > 10:
                print(f"  ... {len(result.errors) - 10} more schema errors")

    failed = [result for result in results if not result.passed]
    error_count = sum(len(result.errors) for result in failed)
    print(
        f"Summary: total={len(results)} pass={len(results) - len(failed)} "
        f"fail={len(failed)} schema_errors={error_count}"
    )
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

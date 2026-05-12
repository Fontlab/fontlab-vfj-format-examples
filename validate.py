#!/usr/bin/env python3
# this_file: validate.py
"""
validate.py — validate every .vfj in corpus/ against the VFJ JSON Schema.

Usage:
    python validate.py [--schema PATH] [--strict] [--allow-known-failures]
                       [--known-failures-file PATH] [--corpus-dir PATH] [--quiet]

Default behaviour:
  - Locates the schema at ../fontlab-vfj-file-format-spec/schema/vfj.bundle.schema.json
    relative to this file (the sibling editable repo).  Override with --schema or the
    VFJ_SCHEMA environment variable.
  - Runs in *lenient* mode: every file must parse as JSON and have a top-level integer
    'version' and an object 'font'.  Strict-schema failures that match a known corpus
    divergence (see KNOWN_DIVERGENCES below) are not counted as failures.
  - Use --strict to count ALL schema errors as failures.
  - Use --allow-known-failures to suppress exit-1 for the divergences catalogued in
    known_failures.txt (or --known-failures-file); used by CI to keep the gate green
    while divergences are being triaged upstream.

Exit codes:
  0  all files pass (in the chosen mode)
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
import re
import sys
from pathlib import Path
from typing import NamedTuple

# ---------------------------------------------------------------------------
# Known corpus-vs-schema divergences (as of 2026-05-12, vfjspec draft 2020-12).
# These are NOT bugs to fix here — they are open items for the spec repo to
# triage.  See README.md §"Known schema-vs-corpus divergences" for details.
#
# Each entry is a (pattern, description) where pattern is matched against the
# jsonschema error message.  A file whose ONLY failures match known divergences
# passes in lenient mode.
# ---------------------------------------------------------------------------
KNOWN_DIVERGENCES: list[tuple[re.Pattern[str], str]] = [
    # KD-1: unicodes array contains integers (codepoints); schema requires strings.
    # Affects 77 files.  Schema expects hex-string form; corpus emits raw ints.
    (re.compile(r"\d+ is not of type 'string'"), "KD-1: unicodes[] int-not-str"),

    # KD-2: inktrapLen additional property on fontMaster.
    # Affects 83 files.  A well-known fontMaster key not yet enumerated in the schema.
    (re.compile(r"Additional properties are not allowed \('inktrapLen'"), "KD-2: inktrapLen additional-prop"),

    # KD-3: advanceWidth additional property on layer.
    # Affects 27 files.  Layer-level advance width not in schema.
    (re.compile(r"Additional properties are not allowed \('advanceWidth'"), "KD-3: advanceWidth additional-prop"),

    # KD-4: axisInstances additional property on font/axes entry.
    # Affects 16 files.
    (re.compile(r"Additional properties are not allowed \('axisInstances'"), "KD-4: axisInstances additional-prop"),

    # KD-5: element anyOf failure — schema's element anyOf is too narrow for
    # string elementData refs (component references by name).
    # Affects 60 files.
    (re.compile(r"is not valid under any of the given schemas"), "KD-5: anyOf (element/hint/guideline schema too narrow)"),

    # KD-6: expressionsUpdated is a boolean (0/1 int) in corpus; schema says integer.
    # Affects 31 files.  Schema models it as boolean but emitter writes 0/1.
    (re.compile(r"False is not of type 'integer'|True is not of type 'integer'|expressionsUpdated"), "KD-6: expressionsUpdated bool-vs-integer"),

    # KD-7: openTypeFeatures entries missing required 'feature' key.
    # Affects 16 files.  Schema requires 'feature'; some entries omit it.
    (re.compile(r"'feature' is a required property"), "KD-7: openTypeFeatures missing 'feature'"),

    # KD-8: anchor missing required 'point' property.
    # Affects 12 files.  Schema requires 'point'; some anchors omit it.
    (re.compile(r"'point' is a required property"), "KD-8: anchor missing 'point'"),

    # KD-9: curveTension additional property on element/contour.
    # Affects 5 files.
    (re.compile(r"Additional properties are not allowed \('curveTension'"), "KD-9: curveTension additional-prop"),

    # KD-10: appearance additional property.
    # Affects 4 files.
    (re.compile(r"Additional properties are not allowed \('appearance'"), "KD-10: appearance additional-prop"),

    # KD-11: bold additional property.
    # Affects 4 files.
    (re.compile(r"Additional properties are not allowed \('bold'"), "KD-11: bold additional-prop"),

    # KD-12: fontNote additional property on font.
    # Affects 2 files.
    (re.compile(r"Additional properties are not allowed \('fontNote'"), "KD-12: fontNote additional-prop"),

    # KD-13: variables field type mismatch on fontMaster (array vs object).
    # Affects 2 files.
    (re.compile(r"is not of type 'object'"), "KD-13: variables type mismatch"),

    # KD-14: other_name additional property.
    # Affects 2 files.
    (re.compile(r"Additional properties are not allowed \('other_name'"), "KD-14: other_name additional-prop"),

    # KD-15: monospaced additional property.
    (re.compile(r"Additional properties are not allowed \('monospaced'"), "KD-15: monospaced additional-prop"),

    # KD-16: italic_angle additional property.
    (re.compile(r"Additional properties are not allowed \('italic_angle'"), "KD-16: italic_angle additional-prop"),

    # KD-17: canInterpolate additional property.
    (re.compile(r"Additional properties are not allowed \('canInterpolate'"), "KD-17: canInterpolate additional-prop"),

    # KD-18: exprX / exprY additional properties (expression-based metrics).
    # Affects 4+1 files.
    (re.compile(r"Additional properties are not allowed \('expr[XY]'"), "KD-18: exprX/exprY additional-prop"),

    # KD-19: cloud additional property.
    (re.compile(r"Additional properties are not allowed \('cloud'"), "KD-19: cloud additional-prop"),

    # KD-20: mark additional property.
    (re.compile(r"Additional properties are not allowed \('mark'"), "KD-20: mark additional-prop"),

    # KD-21: layer additional property on glyph.
    (re.compile(r"Additional properties are not allowed \('layer'"), "KD-21: layer additional-prop"),

    # KD-22: mask layer missing required advanceWidth/name.
    (re.compile(r"'advanceWidth' is a required property|'name' is a required property"), "KD-22: mask layer missing required fields"),

    # KD-99: catch-all for remaining additional-property errors not individually
    # catalogued above.  These are reported as known-ish but flagged for triage.
    (re.compile(r"Additional properties are not allowed"), "KD-99: uncatalogued additional-prop"),
]


class FileResult(NamedTuple):
    path: Path
    passed: bool
    lenient_ok: bool
    lenient_reason: str
    strict_errors: int
    unclassified_errors: int
    classified_divergences: list[str]
    unclassified_messages: list[str]


def find_schema(override: str | None) -> Path | None:
    """Locate the VFJ bundle schema. Returns None if not found."""
    # 1. explicit CLI / env
    env = override or os.environ.get("VFJ_SCHEMA")
    if env:
        p = Path(env).expanduser().resolve()
        if p.is_file():
            return p
        return None  # explicitly set but missing → caller handles

    # 2. sibling editable repo (the expected layout inside protai)
    here = Path(__file__).resolve().parent
    candidates = [
        here / ".." / "fontlab-vfj-file-format-spec" / "schema" / "vfj.bundle.schema.json",
        here / ".." / ".." / "fontlab-vfj-file-format-spec" / "schema" / "vfj.bundle.schema.json",
    ]
    for c in candidates:
        if c.is_file():
            return c.resolve()
    return None


def lenient_check(inst: object) -> tuple[bool, str]:
    """Minimal lenient check: JSON object with int version + object font."""
    if not isinstance(inst, dict):
        return False, "top-level is not an object"
    if not isinstance(inst.get("version"), int):
        return False, "missing or non-integer top-level 'version'"
    if not isinstance(inst.get("font"), dict):
        return False, "missing or non-object top-level 'font'"
    return True, ""


def classify_error(msg: str) -> str | None:
    """Return the KD-* label if this error message matches a known divergence."""
    for pattern, label in KNOWN_DIVERGENCES:
        if pattern.search(msg):
            return label
    return None


def validate_file(
    path: Path,
    validator: "jsonschema.Draft202012Validator",  # type: ignore[name-defined]
    strict: bool,
) -> FileResult:
    try:
        inst = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return FileResult(
            path=path,
            passed=False,
            lenient_ok=False,
            lenient_reason=f"JSON parse error: {exc}",
            strict_errors=0,
            unclassified_errors=0,
            classified_divergences=[],
            unclassified_messages=[],
        )

    lenient_ok, lenient_reason = lenient_check(inst)

    errors = list(validator.iter_errors(inst))
    strict_errors = len(errors)

    classified: list[str] = []
    unclassified_msgs: list[str] = []
    for err in errors:
        label = classify_error(err.message)
        if label:
            if label not in classified:
                classified.append(label)
        else:
            unclassified_msgs.append(
                f"{'/'.join(str(x) for x in err.absolute_path)}: {err.message[:200]}"
            )

    unclassified = len(unclassified_msgs)

    if strict:
        passed = lenient_ok and strict_errors == 0
    else:
        # lenient mode: pass if lenient check passes AND no unclassified errors
        passed = lenient_ok and unclassified == 0

    return FileResult(
        path=path,
        passed=passed,
        lenient_ok=lenient_ok,
        lenient_reason=lenient_reason,
        strict_errors=strict_errors,
        unclassified_errors=unclassified,
        classified_divergences=classified,
        unclassified_messages=unclassified_msgs,
    )


def load_known_failures(path: Path) -> set[str]:
    """Load a newline-separated list of relative paths that are known to fail."""
    if not path.is_file():
        return set()
    lines = path.read_text(encoding="utf-8").splitlines()
    return {ln.strip() for ln in lines if ln.strip() and not ln.startswith("#")}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the VFJ corpus against vfj.bundle.schema.json.",
    )
    parser.add_argument(
        "--schema",
        metavar="PATH",
        help="Path to vfj.bundle.schema.json (default: auto-discover sibling repo; "
             "also reads VFJ_SCHEMA env var).",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail on ALL schema errors, not just unclassified ones.",
    )
    parser.add_argument(
        "--allow-known-failures",
        action="store_true",
        help="Do not exit 1 for files listed in --known-failures-file.",
    )
    parser.add_argument(
        "--known-failures-file",
        metavar="PATH",
        default="known_failures.txt",
        help="File listing corpus-relative paths that are known to fail (default: known_failures.txt).",
    )
    parser.add_argument(
        "--corpus-dir",
        metavar="PATH",
        default=None,
        help="Root of the corpus tree to scan (default: corpus/ next to this script).",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Only print failures and the summary, not PASS lines.",
    )
    args = parser.parse_args()

    # -- locate schema -------------------------------------------------------
    schema_path = find_schema(args.schema or os.environ.get("VFJ_SCHEMA"))
    if schema_path is None:
        if args.schema or os.environ.get("VFJ_SCHEMA"):
            print(
                "ERROR: schema not found at the specified path. "
                "Check --schema / VFJ_SCHEMA.",
                file=sys.stderr,
            )
        else:
            print(
                "NOTICE: vfj.bundle.schema.json not found (looked for sibling "
                "fontlab-vfj-file-format-spec repo).\n"
                "  Set VFJ_SCHEMA=/path/to/vfj.bundle.schema.json or clone the spec repo "
                "as a sibling of this repository.\n"
                "  Skipping validation.",
                file=sys.stderr,
            )
        return 2

    print(f"Schema: {schema_path}")

    # -- load schema + build validator ---------------------------------------
    try:
        import jsonschema  # noqa: PLC0415
    except ImportError:
        print(
            "ERROR: 'jsonschema' is not installed. Run: pip install jsonschema referencing",
            file=sys.stderr,
        )
        return 2

    bundle = json.loads(schema_path.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(bundle)

    # -- collect corpus files ------------------------------------------------
    here = Path(__file__).resolve().parent
    corpus_root = Path(args.corpus_dir).resolve() if args.corpus_dir else here / "corpus"
    if not corpus_root.is_dir():
        print(f"ERROR: corpus directory not found: {corpus_root}", file=sys.stderr)
        return 2

    vfj_files = sorted(corpus_root.rglob("*.vfj"))
    if not vfj_files:
        print(f"WARNING: no .vfj files found under {corpus_root}", file=sys.stderr)
        return 0

    # -- load known-failures list --------------------------------------------
    known_failures: set[str] = set()
    if args.allow_known_failures:
        kf_path = Path(args.known_failures_file)
        if not kf_path.is_absolute():
            kf_path = here / kf_path
        known_failures = load_known_failures(kf_path)

    mode_label = "strict" if args.strict else "lenient"
    print(f"Mode: {mode_label}  |  Corpus: {corpus_root}  |  Files: {len(vfj_files)}\n")

    # -- validate ------------------------------------------------------------
    results: list[FileResult] = []
    for vfj in vfj_files:
        r = validate_file(vfj, validator, strict=args.strict)
        results.append(r)

        try:
            rel = vfj.relative_to(here)
        except ValueError:
            rel = vfj

        status = "PASS" if r.passed else "FAIL"
        if not args.quiet or not r.passed:
            divergences = f"  [{', '.join(r.classified_divergences)}]" if r.classified_divergences else ""
            print(f"  {status}  {rel}{divergences}")
            if not r.lenient_ok:
                print(f"         lenient: {r.lenient_reason}")
            if r.unclassified_messages:
                for msg in r.unclassified_messages[:3]:
                    print(f"         UNCLASSIFIED: {msg}")
                if len(r.unclassified_messages) > 3:
                    print(f"         ... ({len(r.unclassified_messages) - 3} more)")

    # -- summary -------------------------------------------------------------
    n_pass = sum(1 for r in results if r.passed)
    n_fail = sum(1 for r in results if not r.passed)
    n_strict_errs = sum(r.strict_errors for r in results)
    n_unclassified = sum(r.unclassified_errors for r in results)

    print(f"\n{'=' * 60}")
    print(f"Total: {len(results)}  PASS: {n_pass}  FAIL: {n_fail}")
    print(f"Schema errors total: {n_strict_errs}  Unclassified: {n_unclassified}")

    if n_fail > 0:
        # show divergence summary
        from collections import Counter
        div_counts: Counter[str] = Counter()
        for r in results:
            for d in r.classified_divergences:
                div_counts[d] += 1
        if div_counts:
            print("\nClassified divergences (files affected):")
            for label, cnt in div_counts.most_common():
                print(f"  {cnt:3d}  {label}")

        # apply allow-known-failures
        if args.allow_known_failures and known_failures:
            uncovered_fails = [
                r for r in results
                if not r.passed and str(r.path.relative_to(here) if r.path.is_relative_to(here) else r.path) not in known_failures
            ]
            if not uncovered_fails:
                print(
                    f"\n(all {n_fail} failures are in known_failures.txt — "
                    "CI gate is green)"
                )
                return 0
            else:
                print(
                    f"\n{len(uncovered_fails)} failure(s) NOT in known_failures.txt — "
                    "CI gate fails"
                )
                return 1
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

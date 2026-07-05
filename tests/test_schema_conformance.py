# this_file: tests/test_schema_conformance.py
"""Strict Draft 2020-12 schema conformance for the whole corpus.

This mirrors the CI gate but runs in-process through ``validate.py``. It needs
the private ``vfj.bundle.schema.json`` from the fontlab-vfj-file-format-spec
repo; point ``VFJ_SCHEMA`` (or a sibling checkout) at it. When the schema is
not reachable the module skips, so contributors without spec access still get a
green ``pytest`` from the schema-independent integrity checks.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import validate  # noqa: E402

# Common locations the schema turns up in: an explicit env var, a sibling
# checkout of the spec repo, or a local checkout inside this repo.
_SIBLING = ROOT.parent / "fontlab-vfj-file-format-spec" / "schema" / "vfj.bundle.schema.json"
_LOCAL = ROOT / "fontlab-vfj-file-format-spec" / "schema" / "vfj.bundle.schema.json"


def _resolve_schema() -> Path | None:
    schema = validate.find_schema(None)
    if schema is not None:
        return schema
    for candidate in (_SIBLING, _LOCAL):
        if candidate.is_file():
            return candidate
    return None


SCHEMA = _resolve_schema()
pytestmark = pytest.mark.skipif(
    SCHEMA is None,
    reason="VFJ schema not found; set VFJ_SCHEMA to run strict conformance",
)


def test_corpus_passes_strict_schema() -> None:
    """Every corpus fixture validates cleanly against the bundled VFJ schema."""

    validator = validate.build_validator(SCHEMA)
    files = validate.iter_corpus_files(ROOT / "corpus")
    assert files, "no corpus files discovered"

    failures: list[str] = []
    for path in files:
        result = validate.validate_file(path, validator)
        if not result.passed:
            rel = path.relative_to(ROOT).as_posix()
            failures.append(f"{rel}: {'; '.join(result.errors[:3])}")

    assert not failures, "strict schema failures:\n" + "\n".join(failures)

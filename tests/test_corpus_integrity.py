# this_file: tests/test_corpus_integrity.py
"""Corpus-integrity checks that run without the private VFJ schema.

These guard the shape of the fixture set itself: the file count is stable,
every ``.vfj`` parses as JSON and looks like a VFJ document, and the two
generated manifests (``vfj-files.txt`` and ``feature-coverage.json``) stay in
sync with the corpus tree. The strict schema-conformance pass lives in
``test_schema_conformance.py`` and skips when the schema is absent.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "corpus"
sys.path.insert(0, str(ROOT / "scripts"))

import generate_coverage_report as coverage  # noqa: E402
import generate_file_list as file_list  # noqa: E402

# The corpus is a curated, intentionally fixed set. A change here should be a
# deliberate edit to this number, not an accident.
EXPECTED_FILE_COUNT = 130
LICENSE_BUCKETS = {"apache", "cc0", "ofl", "fontlab-eula"}

CORPUS_FILES = sorted(CORPUS.rglob("*.vfj"))


def test_corpus_file_count() -> None:
    """The corpus holds exactly the expected number of VFJ fixtures."""

    assert len(CORPUS_FILES) == EXPECTED_FILE_COUNT, (
        f"expected {EXPECTED_FILE_COUNT} .vfj files, found {len(CORPUS_FILES)}"
    )


def test_every_bucket_is_known() -> None:
    """Every fixture lives under one of the four documented license buckets."""

    buckets = {path.relative_to(CORPUS).parts[0] for path in CORPUS_FILES}
    assert buckets == LICENSE_BUCKETS


@pytest.mark.parametrize("path", CORPUS_FILES, ids=lambda p: p.relative_to(CORPUS).as_posix())
def test_vfj_parses_as_json(path: Path) -> None:
    """Each fixture is valid UTF-8 JSON."""

    with path.open("r", encoding="utf-8") as handle:
        json.load(handle)


@pytest.mark.parametrize("path", CORPUS_FILES, ids=lambda p: p.relative_to(CORPUS).as_posix())
def test_vfj_looks_like_a_font(path: Path) -> None:
    """Each fixture is a JSON object exposing a top-level ``font`` container."""

    data = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict), "top-level VFJ value must be an object"
    assert "font" in data, "VFJ document must contain a 'font' key"


def test_file_list_manifest_is_current() -> None:
    """``vfj-files.txt`` matches what the generator would produce."""

    assert file_list.MANIFEST.read_text(encoding="utf-8") == file_list.corpus_manifest(CORPUS)


def test_feature_coverage_is_current() -> None:
    """``feature-coverage.json`` matches a fresh regeneration from the corpus."""

    expected = coverage.build_report(CORPUS)
    actual = json.loads((ROOT / "feature-coverage.json").read_text(encoding="utf-8"))
    assert actual == expected, (
        "feature-coverage.json is stale; run scripts/generate_coverage_report.py"
    )

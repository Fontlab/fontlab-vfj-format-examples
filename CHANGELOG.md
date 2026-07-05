# Changelog

All notable changes to this corpus and its tooling are recorded here. The
format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the
project uses semantic versioning from git tags.

## [Unreleased]

### Added
- `pyproject.toml` pinning the validator's runtime deps and a `pytest` dev group
  under `uv` (`[tool.uv] package = false` — this stays a data repo, not a package).
- `tests/` pytest suite: `test_corpus_integrity.py` (file count, JSON
  parse-ability, top-level `font` container, and generated-manifest freshness —
  green without the private schema) and `test_schema_conformance.py` (strict
  Draft 2020-12 pass that skips when the schema is absent).
- `scripts/generate_file_list.py` — regenerates (and `--check`s) `vfj-files.txt`
  from the corpus so the manifest can never drift.
- `scripts/generate_corpus_index.py` — renders `docs/corpus-index.md`, a
  per-file table of the structural features each fixture exercises.
- Jekyll + Just the Docs site under `docs/`: home, validation, adding-fonts,
  and the generated corpus index.
- `docs/assets/icon.png` — project icon (line-art, under 500 KB).

### Changed
- CI (`validate.yml`) split into two jobs — schema-independent **integrity**
  (always runs, gates manifest freshness) and token-gated **schema** — with all
  actions pinned to commit SHAs and the Python setup migrated to `uv`.
- `README.md` documents the `uv` workflow, the test suite, generated manifests,
  and the docs site.
- `.gitignore` now covers `.DS_Store`, `.dccache`, Jekyll build output, the
  local spec checkout, and parity artifacts.
- `subsets/templated.txt` carries a comment explaining why it is intentionally
  empty.

## [1.0.1] - 2026-05-13

- Closed the historical KD-1..KD-22 / KD-99 schema divergence catalog; the full
  130-file corpus passes strict Draft 2020-12 validation and
  `known_failures.txt` is an empty placeholder.

## [1.0.0]

- Initial corpus of 130 real-world `.vfj` fonts across four license buckets
  (CC0, Apache 2.0, OFL, FontLab EULA) with the strict `validate.py` gate,
  subset manifests, and feature-coverage metadata.

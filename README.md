# VFJ Format Examples — FontLab JSON Font Format Corpus

This repository contains a collection of `.vfj` (Variable Font JSON) files representing real-world
fonts from various vendors under different open source licenses. These files serve as examples
and test cases for FontLab's JSON-based font format.

## Corpus Overview

The corpus is organized by license type in the `corpus/` directory:

### CC0 (Creative Commons Zero — Public Domain)
- **Designer**: Sora Sagano — cosm, deco, medi, veni, vize, plum (variable & italic variants)
- **Designer**: Echo Heo — baar
- **Designer**: Dmitriy Sychiov — star
- **Designer**: Khalfani — pixa
- **Credits**: OCR fonts by Retorillo & Jonh Sauter — ocra

### Apache License 2.0
- **Designer**: Christian Robertson — boto (variable font)
- **Designer**: Astigmatic (AOETI) — cafe, fest, hint, zotoemoji
- **Designer**: Google Fonts (Monotype Design Team) — extensive Zotosans (writing systems across 60+ scripts)
- **Designer**: Google Fonts (Danh Hong) — Zotoserif Indic scripts (Lao, Khmer)

### SIL Open Font License (OFL)
- **Designer**: Eduardo Tunni — club (variable font)
- **Designer**: Philippe Cochy — ptit
- **Designer**: Carrois Corporate & Edenspiekermann AG — rafi (variable & italic)
- **Designer**: Thomas Phinney, Vassil Kateliev, Brandon Buerkle — scig (variable)
- **Designer**: Juan Pablo del Peral — stroke-chan
- **Designer**: Wei Huang — stroke-grot
- **Designer**: John Hudson, Ross Mills, Paul Hanslow — STIX (Tiro Typeworks), Castoro

### FontLab EULA (Educational/Tutorial)
- **Designer**: Dave Lawrence — cal-* series (learning/tutorial examples covering family setup,
  weight/width axes, kerning, hinting, path operations, style groups, and more)

## File Listing

For a complete list of all `.vfj` files, see `vfj-files.txt` in the repository root.

## Corpus subsets and coverage tooling

The `subsets/` directory contains curated manifests for fast downstream checks:

- `minimal.txt` — small smoke-test fixtures across simple license buckets
- `static.txt` and `variable.txt` — static and variable-font coverage
- `complex.txt` and `edge-cases.txt` — richer fixtures for parser and round-trip stress
- `legacy.txt` — FontLab tutorial/EULA examples that exercise legacy workflows
- `templated.txt` — intentionally empty until real templated VFJ fixtures are supplied

Helper scripts live in `scripts/`:

```bash
# Run strict validation for the full corpus.
python scripts/run_validation.py --schema /path/to/vfj.bundle.schema.json

# Validate one subset manifest.
python scripts/run_subset.py variable --schema /path/to/vfj.bundle.schema.json

# Generate feature-coverage metadata for CI dashboards or downstream planning.
python scripts/generate_coverage_report.py --output feature-coverage.json

# Rebuild the generated manifests (file list + human-readable corpus index).
python scripts/generate_file_list.py
python scripts/generate_corpus_index.py

# Run an external parity command once downstream tools provide baselines.
python scripts/parity_test.py "my-parity-tool --input {vfj}" --output parity-results.json
```

`generate_coverage_report.py` derives mechanical coverage metadata from VFJ content.
Curated descriptions and authoritative parity baselines still need FontLab product-team
input.

`vfj-files.txt`, `feature-coverage.json`, and `docs/corpus-index.md` are all
**generated** — never hand-edit them. The scripts above rewrite them, and CI
fails if they drift from the corpus. When you add a font, rerun the generators
and bump `EXPECTED_FILE_COUNT` in `tests/test_corpus_integrity.py`. See
[`docs/adding-fonts.md`](docs/adding-fonts.md) for the full checklist.

## Documentation

Full docs live in [`docs/`](docs/) (a Jekyll + Just the Docs site): corpus
overview, how to use it as a test fixture, validation and subsets, adding a
font, and the per-file [corpus index](docs/corpus-index.md).

## Format Information

VFJ (Variable Font JSON) is FontLab's native JSON-based font format that serves as:
- A human-readable interchange format for fonts
- A structured representation of font data including glyphs, contours, components, axes,
  masters, instances, hints, and metadata
- A format intended for version control and collaborative development

## License Acknowledgments

All fonts in this corpus are used with the permission of their respective creators under the
terms of their specific licenses as listed above. Please refer to the individual font metadata
for detailed copyright and licensing information.

## Schema Validation

The corpus is validated in strict mode against
[`schema/vfj.bundle.schema.json`](https://github.com/Fontlab/fontlab-vfj-file-format-spec/blob/main/schema/vfj.bundle.schema.json)
from the [`fontlab-vfj-file-format-spec`](https://github.com/Fontlab/fontlab-vfj-file-format-spec)
repository using `validate.py` in this repo.

### Running validation locally

```bash
# With the spec repo checked out as a sibling (auto-discovered):
python validate.py

# With an explicit schema path:
python validate.py --schema /path/to/fontlab-vfj-file-format-spec/schema/vfj.bundle.schema.json

# Or via the VFJ_SCHEMA environment variable:
VFJ_SCHEMA=/path/to/vfj.bundle.schema.json python validate.py
```

Dependencies are pinned in `pyproject.toml`; use `uv` for a reproducible env:

```bash
uv sync
VFJ_SCHEMA=/path/to/vfj.bundle.schema.json uv run pytest
```

`requirements.txt` is retained for pip-only users (`pip install -r requirements.txt`).

`validate.py` exits 0 when all VFJ files pass strict validation, 1 on validation
failures, and 2 if the schema cannot be found.

### Test suite

`uv run pytest` runs two files: `tests/test_corpus_integrity.py` (file count,
JSON parse-ability, and generated-manifest freshness — green without the private
schema) and `tests/test_schema_conformance.py` (strict schema pass, which skips
unless `VFJ_SCHEMA` or a sibling spec checkout is present).

### CI

A GitHub Actions workflow (`.github/workflows/validate.yml`) runs on every push
or pull request that touches the corpus, scripts, tests, manifests, or workflow.
It has two jobs with actions pinned to commit SHAs:

- **integrity** — always runs. Confirms the generated manifests are current and
  runs the schema-independent corpus-integrity tests.
- **schema** — clones the private spec repo via a `SPEC_REPO_TOKEN` secret and
  runs strict validation. If the secret is absent, it skips with an explicit
  notice rather than silently running against a stale schema.

### Schema drift status

As of 2026-05-13, the historical KD-1 through KD-22 and KD-99 schema-vs-corpus
divergences are closed in `fontlab-vfj-file-format-spec`: all 130 VFJ files are
expected to pass strict Draft 2020-12 validation. `known_failures.txt` is retained
only as an empty quarantine placeholder for future temporary regressions.

If strict validation fails, treat it as a regression in either the corpus fixture
or the VFJ schema and fix it in the owning repository. Do not reintroduce lenient
classification in this examples repo.

## Notes

- The corpus totals 130 VFJ files across 4 license categories
  - CC0: 11 files
  - Apache License 2.0: 81 files (including 72 Zotosans writing system variants)
  - SIL Open Font License: 11 files
  - FontLab EULA: 27 files (tutorial examples)
- Files range from simple single-master fonts to complex variable fonts with multiple axes
- Some files demonstrate advanced features: components, hints, variation axes, smart components
- See individual file metadata for specific feature demonstrations

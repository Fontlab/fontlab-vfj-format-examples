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

The corpus is validated against
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

# Strict mode (fails on ALL schema errors, not just unclassified ones):
python validate.py --strict

# Requirements:
pip install jsonschema referencing
# or:
pip install -r requirements.txt
```

`validate.py` exits 0 on success, 1 on failures, and 2 if the schema cannot be
found (so CI without the sibling repo checked out degrades gracefully with a notice).

### CI

A GitHub Actions workflow (`.github/workflows/validate.yml`) runs `validate.py`
in lenient mode on every push or pull request that touches `corpus/`, `validate.py`,
or `known_failures.txt`.  The workflow clones the spec repo using a `SPEC_REPO_TOKEN`
secret; if that secret is absent, the validation step is skipped with a notice.

### Known schema-vs-corpus divergences

As of 2026-05-12, **all 130 files pass in lenient mode** (0 unclassified errors).
In strict mode, all 130 files fail — every error is classified against a known
divergence (KD-1 through KD-22 in `validate.py`).  The total strict error count is
~20 000 (mostly element `anyOf` failures across the 72-file Zotosans set).

These divergences reflect genuine gaps between the current `vfj.bundle.schema.json`
(which models the ideal/strict VFJ format) and real FontLab-9-emitted files.  They
are tracked in the spec repo's `drift.yaml` and `TODO.md §P4`.  **Do not loosen the
schema here** — fixes belong in `fontlab-vfj-file-format-spec`.

| ID | Files affected | Description |
|---|---|---|
| KD-1 | 77 | `unicodes[]` contains integers (codepoints); schema requires strings |
| KD-2 | 83 | `inktrapLen` additional property on `fontMaster` (not yet in schema) |
| KD-3 | 27 | `advanceWidth` additional property on layer |
| KD-4 | 16 | `axisInstances` additional property on axis entry |
| KD-5 | 60 | element/hint/guideline `anyOf` too narrow (string `elementData` refs, etc.) |
| KD-6 | 31 | `expressionsUpdated` is `0`/`1` (bool-ish int); schema type mismatch |
| KD-7 | 16 | `openTypeFeatures` entries missing required `feature` key |
| KD-8 | 12 | anchor missing required `point` property |
| KD-9 | 5 | `curveTension` additional property |
| KD-10 | 4 | `appearance` additional property |
| KD-11 | 4–7 | `bold` additional property |
| KD-12 | 2 | `fontNote` additional property on font |
| KD-13 | 2 | `variables` field type mismatch on `fontMaster` (array vs object) |
| KD-14 | 2 | `other_name` additional property |
| KD-15–22 | 1 each | `monospaced`, `italic_angle`, `canInterpolate`, `exprX`/`exprY`, `cloud`, `mark`, `layer`, mask required fields |
| KD-99 | 7 | Uncatalogued additional properties (to be individually identified) |

## Notes

- The corpus totals 130 VFJ files across 4 license categories
  - CC0: 11 files
  - Apache License 2.0: 81 files (including 72 Zotosans writing system variants)
  - SIL Open Font License: 11 files
  - FontLab EULA: 27 files (tutorial examples)
- Files range from simple single-master fonts to complex variable fonts with multiple axes
- Some files demonstrate advanced features: components, hints, variation axes, smart components
- See individual file metadata for specific feature demonstrations

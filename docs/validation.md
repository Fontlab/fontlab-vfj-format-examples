---
title: Validation
layout: default
nav_order: 2
---

# Validation

The corpus earns its keep only if every file in it is known-good. Two layers
enforce that: a strict JSON-Schema pass over the whole tree, and a pytest suite
that also checks the corpus's own bookkeeping.

## Strict schema validation

`validate.py` walks `corpus/`, loads every `.vfj`, and validates it against the
Draft 2020-12 bundle schema from the private
[`fontlab-vfj-file-format-spec`](https://github.com/Fontlab/fontlab-vfj-file-format-spec)
repo. There is no leniency: any schema error is a real failure. The historical
`KD-1..KD-22` divergence catalog is closed, so `known_failures.txt` is expected
to stay empty.

```bash
# Explicit schema path...
python validate.py --schema /path/to/schema/vfj.bundle.schema.json

# ...or via the environment.
export VFJ_SCHEMA=/path/to/schema/vfj.bundle.schema.json
python validate.py
```

Exit codes: `0` all pass, `1` one or more fail, `2` schema not found (CI uses
this to skip with a notice when the private schema isn't available).

## The pytest suite

`uv run pytest` runs two files:

- `tests/test_corpus_integrity.py` — schema-independent. Confirms the file
  count, that every fixture parses as JSON and carries a top-level `font`
  container, and that the generated manifests (`vfj-files.txt`,
  `feature-coverage.json`, `docs/corpus-index.md`) are current. This is green
  even without spec access.
- `tests/test_schema_conformance.py` — the strict schema pass, in-process. It
  **skips** unless the schema is reachable (via `VFJ_SCHEMA` or a sibling
  `fontlab-vfj-file-format-spec/` checkout).

```bash
uv sync
VFJ_SCHEMA=/path/to/schema/vfj.bundle.schema.json uv run pytest
```

## Subsets

`subsets/` holds curated manifests for faster, targeted checks:

| Subset | Purpose |
|---|---|
| `minimal.txt` | Small smoke-test set across license buckets |
| `static.txt` / `variable.txt` | Static vs. variable coverage |
| `complex.txt` / `edge-cases.txt` | Richer parser and round-trip stress |
| `legacy.txt` | FontLab tutorial/EULA legacy workflows |
| `templated.txt` | Intentionally empty until real templated fixtures land |

```bash
python scripts/run_subset.py variable --schema /path/to/schema/vfj.bundle.schema.json
```

## Coverage metadata

`feature-coverage.json` records, per file, its license bucket, variable flag,
feature tags, and structural marker counts. Regenerate it whenever the corpus
changes; CI fails if it drifts:

```bash
python scripts/generate_coverage_report.py
python scripts/generate_corpus_index.py   # rebuild the human-readable index
```

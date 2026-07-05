---
title: Adding a font
layout: default
nav_order: 3
---

# Adding a font

The corpus grows one real, redistributable font at a time. A new fixture is
only useful if its license permits redistribution and it exercises something
the corpus doesn't already cover well.

## License first

Every file must be legally shippable inside this public repo. Only four buckets
exist, and a font goes in exactly one:

| Bucket | License | Requirement |
|---|---|---|
| `cc0/` | Creative Commons Zero | Public domain; keep `LICENSE.txt` in the bucket |
| `apache/` | Apache 2.0 | Keep `LICENSE.txt`; preserve any upstream `NOTICE` |
| `ofl/` | SIL Open Font License | Keep `LICENSE.txt`; retain the OFL reserved-name terms |
| `fontlab-eula/` | FontLab EULA | FontLab tutorial fonts only |

If a font's license isn't one of these, it does not belong here. When in doubt,
leave it out.

## Filename convention

- Lowercase, hyphen-separated, matching the family/style: `zotosans-cham.vfj`.
- Variable fonts carry a `-var` suffix: `cosm-var.vfj`, and italic variable
  cuts add `-italic-var`: `cosm-italic-var.vfj`.
- Place the `.vfj` beside its source artifacts (`.ttf`, `.yaml`, `.md`) in a
  per-family folder under the right bucket.

## The checklist

1. Save the font from FontLab as `.vfj` into the correct bucket folder.
2. Regenerate the manifests so the bookkeeping stays honest:
   ```bash
   python scripts/generate_file_list.py
   python scripts/generate_coverage_report.py
   python scripts/generate_corpus_index.py
   ```
3. Bump the expected count in `tests/test_corpus_integrity.py`
   (`EXPECTED_FILE_COUNT`) — this is a deliberate edit, not an accident.
4. Validate locally against the schema:
   ```bash
   VFJ_SCHEMA=/path/to/schema/vfj.bundle.schema.json uv run pytest
   ```
5. Commit the font, its sources, and the regenerated manifests together.

CI re-runs the same checks. A stale manifest or an unaccounted file count fails
the build — by design.

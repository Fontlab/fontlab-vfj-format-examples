---
title: Home
layout: default
nav_order: 1
---

# 130 fonts, four licenses, one validator

This repository is a corpus. Not a library, not a tool — a curated pile of 130
real `.vfj` font files that exist so other software can be tested against them.
When a VFJ parser claims it reads the format, this is what you point it at. When
the VFJ schema changes, this is what proves the change didn't break real fonts.

Every file here is a genuine open-source typeface, dragged through FontLab and
saved as VFJ (FontLab's JSON font format). Together they cover static and
variable fonts, sixty-plus writing systems, kerning, hinting, anchors,
components, and the awkward legacy corners that only turn up in fonts people
actually shipped.

![Corpus icon](assets/icon.png){: style="max-width:220px" }

## What's in the box

The corpus lives under `corpus/`, split into four buckets by license:

| Bucket | License | What it holds |
|---|---|---|
| `cc0/` | Creative Commons Zero | Public-domain display and text faces, several variable |
| `apache/` | Apache 2.0 | Google-family scripts — Zotosans across 60+ writing systems |
| `ofl/` | SIL Open Font License | Variable families, STIX/Castoro math and text |
| `fontlab-eula/` | FontLab EULA | Tutorial fonts exercising legacy and edge-case workflows |

The exact file list is generated, never hand-edited — see
[`vfj-files.txt`](https://github.com/Fontlab/fontlab-vfj-format-examples/blob/main/vfj-files.txt)
and the [corpus index](corpus-index.md) for the feature-by-feature breakdown.

## Use it as a test fixture

Point your parser or schema at the tree and sweep it:

```bash
# Strict schema validation of every file (needs the VFJ spec schema).
python validate.py --schema /path/to/vfj.bundle.schema.json

# Or run the pytest integrity + conformance suite.
VFJ_SCHEMA=/path/to/vfj.bundle.schema.json uv run pytest
```

Downstream projects (`fontlab-vfjlib-rs`, `-py`, `-js`) consume this corpus
directly for their round-trip tests. If a font parses here, it should parse
there.

## Next steps

- [Validation](validation.md) — how the corpus is checked, subsets, coverage.
- [Adding a font](adding-fonts.md) — license rules and filename conventions.
- [Corpus index](corpus-index.md) — every file and the features it exercises.

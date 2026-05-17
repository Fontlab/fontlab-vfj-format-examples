#!/usr/bin/env python3
# this_file: scripts/generate_coverage_report.py

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "corpus"
DEFAULT_OUTPUT = ROOT / "feature-coverage.json"
FEATURE_TAG_RE = re.compile(r"\bfeature\s+([A-Za-z0-9]{4})\b")
TAG_VALUE_RE = re.compile(r"^[A-Za-z0-9]{4}$")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate VFJ corpus feature coverage metadata.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--corpus-dir", type=Path, default=CORPUS)
    return parser.parse_args(argv)


def count_nested(value: Any, key: str) -> int:
    if isinstance(value, dict):
        total = 1 if key in value else 0
        for child in value.values():
            total += count_nested(child, key)
        return total
    if isinstance(value, list):
        total = 0
        for child in value:
            total += count_nested(child, key)
        return total
    return 0


def feature_tags_from_string(text: str) -> set[str]:
    tags: set[str] = set()
    if TAG_VALUE_RE.fullmatch(text):
        tags.add(text)
    for match in FEATURE_TAG_RE.finditer(text):
        tags.add(match.group(1))
    return tags


def collect_feature_tags(value: Any) -> set[str]:
    tags: set[str] = set()
    if isinstance(value, dict):
        feature = value.get("feature")
        if isinstance(feature, str):
            tags.update(feature_tags_from_string(feature))
        for child in value.values():
            tags.update(collect_feature_tags(child))
    elif isinstance(value, list):
        for child in value:
            tags.update(collect_feature_tags(child))
    return tags


def file_metadata(path: Path, corpus_root: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    relative = path.relative_to(ROOT).as_posix()
    lower_name = path.name.lower()
    tags = sorted(collect_feature_tags(data))
    axes = count_nested(data, "axisTag") + count_nested(data, "axisInstances")
    glyphs = count_nested(data, "glyphs")
    components = count_nested(data, "component") + count_nested(data, "components")
    anchors = count_nested(data, "anchors")
    kerning = count_nested(data, "kerning")
    hints = count_nested(data, "hints") + count_nested(data, "hint")
    masks = count_nested(data, "mask") + count_nested(data, "masks")
    images = count_nested(data, "image") + count_nested(data, "images")
    builders = count_nested(data, "builder") + count_nested(data, "shapeBuilder")
    variable = axes > 0 or "var" in lower_name or "axis" in lower_name
    return {
        "path": relative,
        "license_bucket": path.relative_to(corpus_root).parts[0],
        "is_variable": variable,
        "feature_tags": tags,
        "counts": {
            "glyph_containers": glyphs,
            "axis_markers": axes,
            "component_markers": components,
            "anchor_markers": anchors,
            "kerning_markers": kerning,
            "hint_markers": hints,
            "mask_markers": masks,
            "image_markers": images,
            "builder_markers": builders,
        },
    }


def build_report(corpus_root: Path) -> dict[str, Any]:
    files = sorted(corpus_root.rglob("*.vfj"))
    entries = [file_metadata(path, corpus_root) for path in files]
    license_counts = Counter(entry["license_bucket"] for entry in entries)
    variable_count = sum(1 for entry in entries if entry["is_variable"])
    all_tags = sorted({tag for entry in entries for tag in entry["feature_tags"]})
    return {
        "schema_profile": "strict-vfj-draft-2020-12",
        "total_files": len(entries),
        "license_counts": dict(sorted(license_counts.items())),
        "variable_files": variable_count,
        "static_files": len(entries) - variable_count,
        "feature_tags": all_tags,
        "files": entries,
    }


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    report = build_report(args.corpus_dir)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

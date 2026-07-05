#!/usr/bin/env python3
# this_file: scripts/generate_file_list.py
"""Regenerate ``vfj-files.txt`` from the corpus tree.

The manifest is a flat, sorted list of every ``.vfj`` fixture, expressed as a
repository-relative POSIX path. Keeping it generated (rather than hand-edited)
means it can never drift from the actual corpus contents. CI verifies the file
matches this script's output; run the script whenever fonts are added.

Usage:
    python scripts/generate_file_list.py            # rewrite vfj-files.txt
    python scripts/generate_file_list.py --check     # exit 1 if out of date
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "corpus"
MANIFEST = ROOT / "vfj-files.txt"


def corpus_manifest(corpus_root: Path) -> str:
    """Return the sorted, newline-terminated list of corpus VFJ paths."""

    paths = sorted(
        path.relative_to(ROOT).as_posix() for path in corpus_root.rglob("*.vfj")
    )
    return "".join(f"{line}\n" for line in paths)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify vfj-files.txt is current without rewriting it",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Regenerate or verify the corpus manifest."""

    args = parse_args(argv)
    expected = corpus_manifest(CORPUS)

    if args.check:
        actual = MANIFEST.read_text(encoding="utf-8") if MANIFEST.exists() else ""
        if actual != expected:
            print(
                "vfj-files.txt is out of date; run scripts/generate_file_list.py",
                file=sys.stderr,
            )
            return 1
        print("vfj-files.txt is up to date")
        return 0

    MANIFEST.write_text(expected, encoding="utf-8")
    print(f"Wrote {MANIFEST} ({expected.count(chr(10))} fixtures)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

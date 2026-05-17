#!/usr/bin/env python3
# this_file: scripts/run_subset.py
"""Validate a named subset manifest by materializing a temporary corpus tree."""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "validate.py"
SUBSETS = ROOT / "subsets"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a named VFJ corpus subset.")
    parser.add_argument("subset", help="Subset name, for example: variable")
    parser.add_argument("--schema", type=Path, help="Explicit vfj.bundle.schema.json path")
    parser.add_argument("--quiet", action="store_true", help="Only print the final summary")
    return parser.parse_args(argv)


def manifest_path(name: str) -> Path:
    path = SUBSETS / f"{name}.txt"
    if not path.exists():
        available = ", ".join(sorted(p.stem for p in SUBSETS.glob("*.txt")))
        raise FileNotFoundError(f"unknown subset '{name}'. Available subsets: {available}")
    return path


def manifest_entries(manifest: Path) -> list[str]:
    entries = []
    for line in manifest.read_text(encoding="utf-8").splitlines():
        entry = line.strip()
        if entry and not entry.startswith("#"):
            entries.append(entry)
    return entries


def make_subset_tree(entries: list[str], target: Path) -> None:
    for entry in entries:
        source = ROOT / entry
        if not source.is_file():
            raise FileNotFoundError(f"Subset entry does not exist: {entry}")
        destination = target / entry
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)



def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        manifest = manifest_path(args.subset)
        entries = manifest_entries(manifest)
        if not entries:
            print(f"Subset {args.subset!r} has no VFJ fixtures; nothing to validate.")
            return 0
        with tempfile.TemporaryDirectory(prefix=f"vfj-subset-{args.subset}-") as tmp:
            subset_root = Path(tmp)
            make_subset_tree(entries, subset_root)
            command = [sys.executable, str(VALIDATOR), "--corpus-dir", str(subset_root)]
            if args.schema is not None:
                command.extend(["--schema", str(args.schema)])
            if args.quiet:
                command.append("--quiet")
            result = subprocess.run(command, cwd=ROOT, check=False)
            return result.returncode
    except FileNotFoundError as error:
        print(error, file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

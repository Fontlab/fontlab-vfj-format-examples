#!/usr/bin/env python3
# this_file: scripts/run_validation.py
"""Run strict VFJ schema validation for the examples corpus."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "validate.py"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments for the validation wrapper."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schema", type=Path, help="Explicit vfj.bundle.schema.json path")
    parser.add_argument("--corpus-dir", type=Path, help="Corpus or subset directory to validate")
    parser.add_argument("--quiet", action="store_true", help="Only print the final summary")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Execute validate.py with stable repository-relative defaults."""
    args = parse_args(argv)
    command = [sys.executable, str(VALIDATOR)]
    if args.schema is not None:
        command.extend(["--schema", str(args.schema)])
    if args.corpus_dir is not None:
        command.extend(["--corpus-dir", str(args.corpus_dir)])
    if args.quiet:
        command.append("--quiet")
    result = subprocess.run(command, cwd=ROOT, check=False)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
# this_file: scripts/parity_test.py

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "vfj-files.txt"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run an external parity command for each VFJ fixture.")
    parser.add_argument("command", nargs="+", help="Command to run; use {vfj} as the fixture placeholder")
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--output", type=Path, default=ROOT / "parity-results.json")
    parser.add_argument("--fail-fast", action="store_true")
    return parser.parse_args(argv)


def manifest_entries(path: Path) -> list[str]:
    entries: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        entry = line.strip()
        if entry:
            entries.append(entry)
    return entries


def command_for_fixture(template: list[str], fixture: Path) -> list[str]:
    return [part.replace("{vfj}", str(fixture)) for part in template]


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    results = []
    failed = False
    for entry in manifest_entries(args.manifest):
        fixture = ROOT / entry
        command = command_for_fixture(args.command, fixture)
        completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
        record = {
            "path": entry,
            "command": command,
            "returncode": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }
        results.append(record)
        if completed.returncode != 0:
            failed = True
            print(f"FAIL {entry}: {completed.returncode}")
            if args.fail_fast:
                break
        else:
            print(f"PASS {entry}")
    args.output.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

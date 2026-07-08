#!/usr/bin/env python3
"""Run every top-level RPG test script without shell/CRLF filename issues."""
from __future__ import annotations

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
SELF = Path(__file__).resolve()

TESTS = sorted(
    p
    for p in (
        set(ROOT.glob("*test*.py"))
        | set(ROOT.glob("test_*.py"))
    )
    if p.is_file() and p.resolve() != SELF
)


def main() -> int:
    failures: list[str] = []
    for path in TESTS:
        rel = path.relative_to(ROOT)
        print(f"--- {rel} ---", flush=True)
        result = subprocess.run(
            [sys.executable, str(path)],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        print(result.stdout, end="" if result.stdout.endswith("\n") else "\n")
        print(f"exit={result.returncode}", flush=True)
        if result.returncode:
            failures.append(str(rel))

    print("FAILURES:", failures)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

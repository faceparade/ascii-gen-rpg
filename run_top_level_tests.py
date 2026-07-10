#!/usr/bin/env python3
"""Run every top-level RPG test script without shell/CRLF filename issues."""
from __future__ import annotations

from pathlib import Path
import subprocess  # nosec B404 -- this local test runner intentionally launches Python files
import sys

ROOT = Path(__file__).resolve().parent
SELF = Path(__file__).resolve()

TESTS = sorted(
    {
        p
        for pattern in ("test_*.py", "*_test.py", "*_tests.py")
        for p in ROOT.glob(pattern)
        if p.is_file() and p.resolve() != SELF
    }
)


def main() -> int:
    failures: list[str] = []
    for path in TESTS:
        rel = path.relative_to(ROOT)
        print(f"--- {rel} ---", flush=True)
        result = subprocess.run(  # nosec B603 -- executable and paths are local, discovered test files
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

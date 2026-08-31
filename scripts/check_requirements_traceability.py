"""Check that requirements and traceability IDs are equal, unique, and paired."""
from __future__ import annotations

import re
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ID_PATTERN = re.compile(r"^\|\s*(REQ-[A-Z0-9-]+)\s*\|")

def ids(path: Path) -> list[str]:
    return [match.group(1) for line in path.read_text(encoding="utf-8").splitlines() if (match := ID_PATTERN.match(line))]

def duplicate(values: list[str]) -> list[str]:
    return sorted({value for value in values if values.count(value) > 1})

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    root = parser.parse_args(argv).root.resolve()
    req_files = (root / "docs/REQUIREMENTS.md", root / "docs/REQUIREMENTS.vi.md")
    trace_files = (root / "docs/TRACEABILITY_MATRIX.md", root / "docs/TRACEABILITY_MATRIX.vi.md")
    failures: list[str] = []
    requirement_ids = [ids(path) for path in req_files]
    trace_ids = [ids(path) for path in trace_files]
    if requirement_ids[0] != requirement_ids[1]:
        failures.append("requirements English/Vietnamese ID sets or order differ")
    if trace_ids[0] != trace_ids[1]:
        failures.append("traceability English/Vietnamese ID sets or order differ")
    if duplicate(requirement_ids[0]):
        failures.append("duplicate requirement IDs: " + ", ".join(duplicate(requirement_ids[0])))
    if duplicate(trace_ids[0]):
        failures.append("duplicate traceability IDs: " + ", ".join(duplicate(trace_ids[0])))
    if sorted(requirement_ids[0]) != sorted(trace_ids[0]):
        failures.append("requirements and traceability IDs are missing or extra")
    if failures:
        print("Requirements traceability check: FAIL")
        print("\n".join(failures))
        return 1
    print(f"Requirements traceability check: PASS ({len(requirement_ids[0])} unique IDs, exact bilingual and matrix match)")
    return 0

if __name__ == "__main__":
    sys.exit(main())

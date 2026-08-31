"""Check source-ledger IDs, pinned identities, claims, and licenses."""
from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
ROW = re.compile(r"^\|\s*(SRC-[A-Z0-9-]+)\s*\|")
FORBIDDEN = ("TBD", "current docs", "current page", "to verify", "not pinned", "versionless")

def rows(path: Path) -> list[tuple[str, list[str]]]:
    result = []
    for line in path.read_text(encoding="utf-8").splitlines():
        match = ROW.match(line)
        if match:
            result.append((match.group(1), [part.strip() for part in line.strip().strip("|").split("|")]))
    return result

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    root = parser.parse_args(argv).root.resolve()
    paths = (root / "docs/SOURCE_LEDGER.md", root / "docs/SOURCE_LEDGER.vi.md")
    failures: list[str] = []
    parsed = [rows(path) for path in paths]
    if [item[0] for item in parsed[0]] != [item[0] for item in parsed[1]]:
        failures.append("English/Vietnamese source IDs differ")
    for path, source_rows in zip(paths, parsed):
        seen = [item[0] for item in source_rows]
        for source_id in sorted(set(seen)):
            if seen.count(source_id) > 1:
                failures.append(f"{path.relative_to(root).as_posix()}: duplicate {source_id}")
        for source_id, fields in source_rows:
            if len(fields) < 6:
                failures.append(f"{path.relative_to(root).as_posix()}: {source_id}: missing ledger field")
                continue
            lower = " ".join(fields).lower()
            for marker in FORBIDDEN:
                if marker.lower() in lower:
                    failures.append(f"{path.relative_to(root).as_posix()}: {source_id}: forbidden placeholder {marker}")
            if not re.search(r"commit|tag|version|content identity", fields[2], re.IGNORECASE):
                failures.append(f"{path.relative_to(root).as_posix()}: {source_id}: missing pinned identity")
            if not re.search(r"GPL-3\.0|Apache-2\.0|OpenAI terms", fields[4], re.IGNORECASE):
                failures.append(f"{path.relative_to(root).as_posix()}: {source_id}: missing explicit license")
    if failures:
        print("Source ledger check: FAIL")
        print("\n".join(sorted(set(failures))))
        return 1
    print(f"Source ledger check: PASS ({len(parsed[0])} bilingual pinned source rows)")
    return 0

if __name__ == "__main__":
    sys.exit(main())

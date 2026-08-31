"""Check first-party Markdown pairing in both directions."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_PARTS = {".git"}

def is_excluded(path: Path, root: Path) -> bool:
    """Return whether a path is exempt from first-party pairing checks."""
    parts = path.relative_to(root).parts
    return any(part in EXCLUDED_PARTS for part in parts) or (
        len(parts) >= 2 and parts[0] == "evidence" and parts[1] == "imported"
    )

def find_orphans(root: Path) -> list[tuple[str, str]]:
    """Return stable relative paths and reasons for every missing sibling."""
    files = sorted(path for path in root.rglob("*.md") if not is_excluded(path, root))
    known = set(files)
    failures = []
    for path in files:
        relative = path.relative_to(root).as_posix()
        if path.name.endswith(".vi.md"):
            sibling = path.with_name(path.name[:-len(".vi.md")] + ".md")
            reason = "missing English sibling"
        else:
            sibling = path.with_name(path.stem + ".vi.md")
            reason = "missing Vietnamese sibling"
        if sibling not in known:
            failures.append((relative, reason))
    return sorted(failures)

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=REPOSITORY_ROOT)
    root = parser.parse_args(argv).root.resolve()
    failures = find_orphans(root)
    if failures:
        print("Markdown pair check: FAIL")
        for path, reason in failures:
            print(f"{path}: {reason}")
        return 1
    print("Markdown pair check: PASS")
    return 0

if __name__ == "__main__":
    sys.exit(main())

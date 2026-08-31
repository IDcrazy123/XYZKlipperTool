"""Fail if a first-party Markdown file has no .vi.md sibling."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SKIP_PARTS = {".git", "evidence"}

def main() -> int:
    orphaned = []
    for path in ROOT.rglob("*.md"):
        if any(part in SKIP_PARTS for part in path.parts):
            continue
        if path.name.endswith(".vi.md"):
            continue
        sibling = path.with_name(f"{path.stem}.vi.md")
        if not sibling.exists():
            orphaned.append(path.relative_to(ROOT).as_posix())
    if orphaned:
        for item in orphaned:
            print(f"ORPHANED_MARKDOWN {item}")
        return 1
    print("Markdown pair check: PASS")
    return 0

if __name__ == "__main__":
    sys.exit(main())

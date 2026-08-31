"""Negative tests for source-ledger placeholder and field validation."""
from pathlib import Path
import tempfile

from check_source_ledger import main as check_main

ROW = "| SRC-001 | https://example.invalid | current docs; compatibility commit TBD | claim | license to verify | follow-up |\n"
GOOD = "| SRC-001 | https://example.invalid | commit `abc123`; accessed 2026-08-31 | claim | GPL-3.0 | follow-up |\n"

def main() -> int:
    with tempfile.TemporaryDirectory(prefix="source-ledger-") as directory:
        root = Path(directory) / "docs"
        root.mkdir()
        for name in ("SOURCE_LEDGER.md", "SOURCE_LEDGER.vi.md"):
            (root / name).write_text(ROW, encoding="utf-8")
        assert check_main(["--root", str(root.parent)]) == 1
        for name in ("SOURCE_LEDGER.md", "SOURCE_LEDGER.vi.md"):
            (root / name).write_text(GOOD, encoding="utf-8")
        assert check_main(["--root", str(root.parent)]) == 0
    print("Source ledger negative fixtures: PASS (placeholder fields fail in temp root)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

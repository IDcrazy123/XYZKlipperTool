"""Negative and positive tests for the Markdown pair checker."""
from pathlib import Path
import tempfile

from check_markdown_pairs import find_orphans, main as check_main

def expect(root: Path, expected: list[tuple[str, str]]) -> None:
    actual = find_orphans(root)
    assert actual == expected, f"expected {expected!r}, got {actual!r}"

def main() -> int:
    with tempfile.TemporaryDirectory(prefix="markdown-pairs-") as directory:
        root = Path(directory)
        (root / "english-only.md").write_text("# English\n", encoding="utf-8")
        expect(root, [("english-only.md", "missing Vietnamese sibling")])
        assert check_main(["--root", str(root)]) == 1
        (root / "english-only.md").unlink()
        (root / "vietnamese-only.vi.md").write_text("# Việt\n", encoding="utf-8")
        expect(root, [("vietnamese-only.vi.md", "missing English sibling")])
        assert check_main(["--root", str(root)]) == 1
        (root / "vietnamese-only.md").write_text("# English\n", encoding="utf-8")
        expect(root, [])
    print("Markdown pair negative fixtures: PASS (missing VI and missing EN both fail)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

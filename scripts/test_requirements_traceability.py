"""Negative tests for missing, extra, and duplicate traceability IDs."""
from pathlib import Path
import tempfile

from check_requirements_traceability import ID_PATTERN, duplicate, main as check_main

def parse(text: str) -> list[str]:
    return [match.group(1) for line in text.splitlines() if (match := ID_PATTERN.match(line))]

def main() -> int:
    with tempfile.TemporaryDirectory(prefix="requirements-traceability-") as directory:
        root = Path(directory)
        requirements = "| REQ-A-001 | one | `PLANNED` | ASSUMPTION |\n| REQ-B-001 | two | `PLANNED` | ASSUMPTION |\n"
        traceability = "| REQ-A-001 | source | design | test |\n| REQ-A-001 | source | design | test |\n"
        req_ids, trace_ids = parse(requirements), parse(traceability)
        assert req_ids != trace_ids, "extra/missing ID fixture did not differ"
        assert duplicate(trace_ids) == ["REQ-A-001"], "duplicate fixture was not detected"
        (root / "docs").mkdir()
        for name in ("REQUIREMENTS.md", "REQUIREMENTS.vi.md"):
            (root / "docs" / name).write_text(requirements, encoding="utf-8")
        for name in ("TRACEABILITY_MATRIX.md", "TRACEABILITY_MATRIX.vi.md"):
            (root / "docs" / name).write_text(traceability, encoding="utf-8")
        assert check_main(["--root", str(root)]) == 1
    print("Requirements traceability negative fixtures: PASS (missing/extra and duplicate IDs detected)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

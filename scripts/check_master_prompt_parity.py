"""Check master-prompt heading structure and code/command token parity."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
ENGLISH = ROOT / "PROJECT_BUILD_PROMPT.md"
VIETNAMESE = ROOT / "PROJECT_BUILD_PROMPT.vi.md"


def headings(text: str) -> list[tuple[int, str]]:
    return [(len(match.group(1)), match.group(2).strip()) for match in re.finditer(r"^(#{1,6}) (.+)$", text, re.MULTILINE)]


def code_tokens(text: str) -> set[str]:
    # Fenced repository trees are structural examples, not inline command tokens.
    unfenced = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    return set(re.findall(r"`([^`\n]+)`", unfenced))


def main() -> int:
    english = ENGLISH.read_text(encoding="utf-8")
    vietnamese = VIETNAMESE.read_text(encoding="utf-8")
    en_headings = headings(english)
    vi_headings = headings(vietnamese)
    failures: list[str] = []
    if len(en_headings) != 42 or len(vi_headings) != 42:
        failures.append(f"heading count: English={len(en_headings)}, Vietnamese={len(vi_headings)}, expected=42")
    if [level for level, _ in en_headings] != [level for level, _ in vi_headings]:
        failures.append("heading levels do not match")
    en_sections = [title for level, title in en_headings if level == 2 and re.match(r"^\d+\. ", title)]
    vi_sections = [title for level, title in vi_headings if level == 2 and re.match(r"^\d+\. ", title)]
    if len(en_sections) != 18 or len(vi_sections) != 18:
        failures.append(f"numbered sections: English={len(en_sections)}, Vietnamese={len(vi_sections)}, expected=18")
    missing_tokens = sorted(code_tokens(english) - code_tokens(vietnamese))
    if missing_tokens:
        failures.append("missing code/command tokens: " + ", ".join(missing_tokens))
    if failures:
        print("MASTER PROMPT PARITY: FAIL")
        print("\n".join(failures))
        return 1
    print("MASTER PROMPT PARITY: PASS (18 sections, 42 headings, all code/command tokens present)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

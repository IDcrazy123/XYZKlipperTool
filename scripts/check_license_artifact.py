"""Validate the repository's canonical GPL-3.0 license artifact."""
from pathlib import Path
import hashlib
import sys

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SHA256 = "e57f1c320b8cf8798a7d2ff83a6f9e06a33a03585f6e065fea97f1d86db84052"

def main() -> int:
    path = ROOT / "LICENSE"
    data = path.read_bytes()
    text = data.decode("utf-8")
    failures = []
    if hashlib.sha256(data).hexdigest() != EXPECTED_SHA256:
        failures.append("LICENSE SHA-256 differs from the normalized official GNU GPL-3.0 text")
    if not text.startswith("                    GNU GENERAL PUBLIC LICENSE\n                       Version 3, 29 June 2007"):
        failures.append("missing GPL heading/version")
    if "15. Disclaimer of Warranty." not in text or "THERE IS NO WARRANTY FOR THE PROGRAM" not in text:
        failures.append("missing warranty disclaimer")
    if "16. Limitation of Liability." not in text:
        failures.append("missing liability disclaimer")
    if "                     END OF TERMS AND CONDITIONS" not in text:
        failures.append("missing end-of-terms marker")
    if not text.endswith("<https://www.gnu.org/licenses/why-not-lgpl.html>.\n\n"):
        failures.append("unexpected license ending")
    if failures:
        print("License artifact check: FAIL")
        print("\n".join(failures))
        return 1
    print("License artifact check: PASS (official GPL-3.0 text, normalized SHA-256, warranty and ending verified)")
    return 0

if __name__ == "__main__":
    sys.exit(main())

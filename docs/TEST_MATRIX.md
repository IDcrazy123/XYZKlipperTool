# Phase 00 test matrix

| ID | Check | Command/approach | Expected |
|---|---|---|---|
| TEST-001 | Markdown pairing | `python scripts/check_markdown_pairs.py` | pass, no orphan |
| TEST-002 | Evidence hashes | `Get-FileHash` vs manifest | all match |
| TEST-003 | Raw immutability | compare source/destination hashes | all match |
| TEST-004 | Secret scan | `rg -n -i` credential patterns | no findings in imported evidence |
| TEST-005 | Link scan | local Markdown target audit | no missing local targets |
| TEST-006 | License/provenance | ledger and notices review | every upstream row pinned or follow-up recorded |
| TEST-007 | Production-code boundary | file inventory/search | no `src/`, `klippy/`, or measurement implementation |

# Phase 00 test matrix

| ID | Check | Command/approach | Expected |
|---|---|---|---|
| TEST-001 | Markdown pairing | `python scripts/check_markdown_pairs.py` | bidirectional pass, stable path+reason failures |
| TEST-009 | Markdown negative fixtures | `python scripts/test_markdown_pairs.py` | missing VI and missing EN both fail in temp root; no fixture remains in repository |
| TEST-002 | Evidence hashes | `Get-FileHash` vs manifest | all match |
| TEST-003 | Raw immutability | compare source/destination hashes | all match |
| TEST-004 | Secret scan | `rg -n -i` credential patterns | no findings in imported evidence |
| TEST-005 | Link scan | local Markdown target audit | no missing local targets |
| TEST-006 | License/provenance | ledger and notices review | every upstream row pinned or follow-up recorded |
| TEST-007 | Production-code boundary | file inventory/search | no `src/`, `klippy/`, or measurement implementation |
| TEST-008 | Master prompt parity | `python scripts/check_master_prompt_parity.py` | 18 sections, 42 headings and all code/command tokens present |

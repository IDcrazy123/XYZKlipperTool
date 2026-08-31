# Phase 00 test matrix

| ID | Check | Command/approach | Expected |
|---|---|---|---|
| TEST-001 | Markdown pairing | `python scripts/check_markdown_pairs.py` | bidirectional pass, stable path+reason failures |
| TEST-009 | Markdown negative fixtures and exemptions | `python scripts/test_markdown_pairs.py` | missing VI, missing EN, and artifacts orphan fail; raw evidence/imported Markdown is exempt; no fixture remains in repository |
| TEST-010 | Requirements/traceability IDs | `python scripts/check_requirements_traceability.py` and `python scripts/test_requirements_traceability.py` | no missing, extra, duplicate, or bilingual ID mismatch; negative fixtures fail in temp root |
| TEST-011 | Source ledger pin/license fields | `python scripts/check_source_ledger.py` and `python scripts/test_source_ledger.py` | every bilingual row has URL, access/content identity, claim, explicit license, and no forbidden placeholder |
| TEST-012 | Canonical license artifact | `python scripts/check_license_artifact.py` | official GPL-3.0 heading/version, warranty/liability disclaimer, end marker, ending, and normalized SHA-256 pass |
| TEST-002 | Evidence hashes | `Get-FileHash` vs manifest | all match |
| TEST-003 | Raw immutability | compare source/destination hashes | all match |
| TEST-004 | Secret scan | `rg -n -i` credential patterns | no findings in imported evidence |
| TEST-005 | Link scan | local Markdown target audit | no missing local targets |
| TEST-006 | License/provenance | ledger and notices review | every upstream row pinned or follow-up recorded |
| TEST-007 | Production-code boundary | file inventory/search | no `src/`, `klippy/`, or measurement implementation |
| TEST-008 | Master prompt parity | `python scripts/check_master_prompt_parity.py` | 18 sections, 42 headings and all code/command tokens present |

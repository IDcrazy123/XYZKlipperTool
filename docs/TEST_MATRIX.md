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
| TEST-013 | Phase 01 domain unit/property/fault | `set PYTHONPATH=src; python -m unittest discover -s tests -v` | all domain, statistics, provider, schema, evidence-fixture tests pass |
| TEST-014 | Phase 01 import boundary | static import scan of `src/xyz_klipper_tool/domain` | no framework, filesystem, network, or service imports |
| TEST-015 | Phase 01 schema artifact | schema JSON parse plus schema codec tests | version 1 artifact and round-trip/backward compatibility pass |
| TEST-016 | Phase 01 schema contract | `set PYTHONPATH=src; python -m unittest tests.test_schema -v` | both provider schemas enforce required/const/enum/finite contract and codec faults pass |
| TEST-017 | Phase 01 coverage | `python -m coverage run -m unittest discover -s tests; python -m coverage report -m` | 16 tests pass; TOTAL coverage 95% |
| TEST-018 | Phase 01 pinned type checks | isolated venv; `python -m mypy`; `pyright` using pinned requirements | PASS: mypy and pyright clean |
| TEST-019 | Phase 02 port/fake/station contracts | `PYTHONPATH=src; python -m unittest discover -s tests -v` | ports, deterministic fakes, dynamic tools, station workflows, and writer isolation pass |
| TEST-020 | Phase 02 persistence fault matrix | `PYTHONPATH=src; python -m unittest tests.test_phase02 -v` | atomic temp/flush/replace, corruption, checksum, version, and backup faults fail closed |
| TEST-021 | Phase 02 schemas and fingerprint | pinned `jsonschema` Draft 2020-12 plus configuration fingerprint tests | station envelope contract, canonical ordering, redaction, and change detection pass |
| TEST-022 | Phase 03 capture/calibration/detectors | `PYTHONPATH=src; python -m unittest tests.test_phase03` | bounded capture, local allowlist, calibration round-trip/corruption, candidate diagnostics pass |
| TEST-023 | Phase 03 corpus leakage | `PYTHONPATH=src; python -m unittest tests.test_phase03` | session-separated split has no leakage; real-corpus reliability gate remains NEEDS_WORK |
| TEST-024 | Phase 03 calibration persistence fault matrix | `PYTHONPATH=src; python -m unittest tests.test_phase03 -v` | bounded schema/checksum, pre-replace preservation, and backup rotation fault stages pass |
| TEST-025 | Phase 03 corpus inventory and benchmark contracts | `PYTHONPATH=src; python -m unittest tests.test_phase03 -v` | confined relative paths, hashes, whole-session split, and both synthetic candidate reports pass |
| TEST-026 | Phase 03 Draft 2020-12 schemas | `pinned venv; PYTHONPATH=src; python -m unittest tests.test_phase03.Phase03Tests.test_phase03_schemas_are_draft202012_contracts` | calibration, corpus, and benchmark schemas validate positive instances and reject extra/UTC-invalid fields |
| TEST-027 | Phase 03 recovery integrity | `pinned venv; PYTHONPATH=src; python -m unittest tests.test_phase03.Phase03Tests.test_recovery_validates_backup_before_non_destructive_replace` | corrupt/traversal backup is rejected before current or backup changes |
| TEST-028 | Phase 03 committed synthetic corpus | `pinned venv; PYTHONPATH=src; python -m unittest tests.test_phase03.Phase03Tests.test_committed_synthetic_fixture_and_benchmark_artifact_validate` | three-session PGM fixture hashes, labels, relative paths, manifest and benchmark reports validate |

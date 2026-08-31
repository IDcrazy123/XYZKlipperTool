# Phase 00 plan — Governance, source audit, license, and evidence import

## Scope

Establish the repository governance and evidence foundation for XYZ Klipper Tool: bilingual documentation parity, source/license provenance, requirements traceability, sanitized immutable evidence import, threat/risk context, and reproducible offline checks.

## Non-goals

No production measurement code, printer motion, heating, probing, tool changes, firmware restart, configuration apply, service deployment, or HIL execution. Historical coordinates, offsets, temperatures, camera scale, tool count, and tolerances remain evidence only.

## Deliverables

- Repository identity, first-party GPL-3.0-or-later decision, and complete license artifact.
- 24 stable requirements and one-to-one bilingual traceability matrix.
- Pinned source ledger, third-party notices, and clean-room/provenance policy.
- 2 X/Y evidence files and 21 Z JSON files, including `WARNING` and `INVALID`, with SHA-256 manifest.
- Architecture context, threat model, risk register, decision log, roadmap, and bilingual parity checker.
- Source-ledger, requirements-traceability, master-prompt-parity, license, and Markdown-pair checkers with negative fixtures.
- Machine-readable test artifact under `artifacts/test-runs/phase-00-closure/`.

## Sources and inputs

Primary sources are recorded in [SOURCE_LEDGER.md](../SOURCE_LEDGER.md), including pinned Klipper, Moonraker, Cartographer docs, OpenCV, kTAMV, KTC, and klipper-toolchanger identities. Inputs include the reviewed bootstrap files and the All-Config X/Y report/CSV plus related Z history. No upstream source code is copied.

## Assumptions and decisions

- First-party license: SPDX `GPL-3.0-or-later`.
- Package slug: `xyz_klipper_tool`.
- Imported raw files are byte-preserving and immutable after commit.
- `evidence/imported` is provenance-bound raw material; other Markdown is first-party unless an explicit exemption is added with provenance.
- Offline checks cannot prove physical safety or hardware compatibility.

## Acceptance tests

1. All first-party Markdown pairs pass in both directions; missing English, missing Vietnamese, and `artifacts/` orphans fail in temporary fixtures.
2. Master prompt has 18 sections/42 headings and all code/command tokens are present in Vietnamese.
3. Requirements and traceability have exactly the same 24 unique IDs in both languages and one row per ID; negative missing/extra/duplicate fixtures fail.
4. Source ledger has 11 bilingual rows with URL, access/content identity, claim, explicit license, and no forbidden placeholders; negative placeholder fixture fails.
5. License artifact matches the recorded normalized SHA-256 and required GPL markers.
6. Imported evidence parses, matches manifest hashes, preserves `WARNING`/`INVALID`, and contains no secret findings.
7. Link, diff, and production-boundary checks pass.

## HIL boundary and gate

All physical capability claims remain `REQUIRES_HIL`. The phase closes only for offline governance/evidence deliverables and stops at supervisor review. No production behavior is authorized by this plan.

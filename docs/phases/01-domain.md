# Phase 01 — Domain model, units, signs, and statistics

## Scope

Implement only pure, deterministic domain logic for typed quantities, coordinate/sign contracts, identities, provider-specific measurement results, verdicts/reason codes, run-state transitions, robust statistics, outlier decisions, apply-plan/freshness/rollback data, and versioned in-memory schemas.

## Non-goals

No camera, Klipper, Moonraker, filesystem, network, service, installer, hardware adapter, production I/O, printer motion, heating, probing, tool change, restart, deployment, configuration apply, or HIL execution. Historical evidence is a test fixture only; it must not become a product default.

## Deliverables

- Typed millimetre, pixel, second, and Celsius quantities; vectors, coordinate frames, sign conventions, and reversible conversions.
- Independent run, outer-cycle, tool-visit, and frame-sample identities and separate switch/Cartographer Touch result models.
- Claim/verdict states, explicit reason codes, and a deterministic fail-closed run state machine.
- Raw-preserving robust summaries with valid/invalid/warning counts, mean, median, sample standard deviation, MAD, bounds, range, uncertainty, drift, and declared outlier policy; n=0 and n=1 are typed outcomes.
- Side-effect-free apply, freshness, and rollback plans.
- Versioned machine-readable schemas with round-trip and unknown-field compatibility tests.
- Unit, table-driven, property/metamorphic, and fault-case tests, including a sanitized kTAMV T3 evidence fixture.

## Sources and assumptions

The Phase 00 source ledger, evidence baseline, requirements, and traceability records are the governing inputs. No new external claim is introduced by this phase. Existing evidence values remain provenance-bound and immutable. Robust uncertainty is explicitly labelled as an estimator output, not a physical safety guarantee; insufficient samples produce a typed result. Provider sign/coordinate semantics remain explicit contracts and unresolved physical compatibility remains `REQUIRES_HIL`.

## Acceptance tests

- Domain modules import only the Python standard library and have no framework or I/O dependency.
- Every boundary quantity names its unit; frame and sign contracts have docstrings and bidirectional conversion tests.
- Switch and Cartographer Touch results are structurally separate; invalid samples never enter estimators.
- n=0, n=1, `INVALID`, `WARNING`, uncertainty, drift, outlier rejection, illegal transition, stale fingerprint, and rollback paths are covered.
- Schema versioning, round-trip serialization, backward-compatible unknown fields, and unsupported-version failure are covered.
- Bilingual Markdown parity, links, secrets, license, formatting, type/lint, unit/property/fault tests, coverage, and machine-readable artifact checks pass.

## HIL boundary and gate

This phase performs no physical action and cannot establish physical safety. HIL remains required for machine-specific station teaching, provider compatibility, travel envelopes, probing, tool state, and operator abort validation. Completion stops at supervisor review of the pushed `phase/01-domain` branch; no merge to `main` and no release is permitted.

## Test strategy

Run `python -m unittest discover -s tests -v`, import-boundary and schema checks, available lint/type/coverage checks, all Phase 00 governance checkers, and `git diff --check`. Record exact commands, exit codes, counts, and artifact hashes in the Phase 01 progress record and test-run JSON.

## Correction-pass closure criteria

The correction pass must keep the gate `NEEDS_WORK` unless pinned mypy/pyright dependencies are installed and run successfully. Contract tests must exercise both Z providers, hierarchy and provider isolation, finite/non-empty validation, explicit rejection records, reference drift, schema required/type/enum/finite constraints, freshness/apply/rollback invariants, and all listed negative paths.

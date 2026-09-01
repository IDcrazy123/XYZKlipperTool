# Phase 00 traceability matrix

Every requirement below occurs exactly once.

| Requirement | Evidence/source | Design artifact | Planned/actual test gate |
|---|---|---|---|
| REQ-IDENT-001 | ADR-0001 | repository identity ADR | actual: commit identity review |
| REQ-CMD-001 | SRC-001; Master prompt | command contract in master prompt | planned: command contract tests |
| REQ-STATION-001 | EVID-XY-001; Master prompt | architecture context; station policy | planned: teach contract; coordinate-default scan |
| REQ-STATE-001 | Master prompt; ASSUMPTION | `domain/models.py` hierarchy identities; `state_machine.py` | actual: `tests/test_domain.py` non-empty hierarchy and terminal/fault transitions |
| REQ-TOOL-001 | EVID-XY-001; Master prompt | adapter contract; measurement protocol | planned: dynamic discovery tests |
| REQ-PROVIDER-001 | EVID-Z-001; SRC-008 | `domain/models.py` SwitchZ/CartographerTouch results and homogeneous series | actual: `tests/test_domain.py`, `tests/test_schema.py` provider isolation/round-trip |
| REQ-MOTION-001 | AGENTS; SRC-001; ASSUMPTION | threat model; safety reason-code catalog | planned: fault-injection invariant tests |
| REQ-SAMPLE-001 | EVID-XY-001 | sampling hierarchy design | planned: three outer-cycle test |
| REQ-STAT-001 | EVID-XY-001; Master prompt | `domain/statistics.py` Summary/StatisticResult | actual: `tests/test_domain.py` sufficiency, counts, SD/MAD/uncertainty/reference drift |
| REQ-OUTLIER-001 | EVID-XY-001 | `statistics.py` immutable raw plus unfiltered/filtered summaries and Rejection | actual: reasoned rejection, invalid exclusion, threshold validation tests |
| REQ-VISION-001 | SRC-009; Master prompt | host vision boundary | planned: stale/ambiguous/corrupt frame tests |
| REQ-CORPUS-001 | SRC-009; SRC-010 | corpus and evaluation plan | planned: session split/holdout gate |
| REQ-PERSIST-001 | Master prompt; ASSUMPTION | persistence policy | planned: atomic write/power-loss tests |
| REQ-SCHEMA-001 | Master prompt; ASSUMPTION | `domain/schema.py`; paired v1 JSON Schemas | actual: `tests/test_schema.py` contract, round-trip, malformed/version/enum/non-finite faults |
| REQ-EVID-001 | Phase 00 import; EVID-Z-INVALID-001 | provenance policy; evidence manifest | actual: 23/23 hash and 21/21 JSON checks |
| REQ-APPLY-001 | EVID-Z-001; Master prompt | `domain/models.py` side-effect-free ApplyPlan/RollbackPlan | actual: `tests/test_domain.py` preview-only/rollback invariants; writer remains out of scope |
| REQ-FRESH-001 | Master prompt; ASSUMPTION | `domain/models.py` FreshnessExpectation/FreshnessResult | actual: typed stale reason model; adapter validation remains later phase |
| REQ-SEC-001 | Master prompt; ASSUMPTION | threat model; security policy | actual: secret scan; planned: SSRF/bounds tests |
| REQ-RESOURCE-001 | Master prompt; ASSUMPTION | resource-limit policy | planned: payload/job/history limit tests |
| REQ-PORT-001 | SRC-002; Master prompt | pure `domain/` package boundary | actual: standard-library import-boundary scan |
| REQ-PORT-002 | Master prompt; ASSUMPTION | `ports/contracts.py` typed boundary protocols | actual: `tests/test_phase02.py`; mypy/pyright |
| REQ-SIM-001 | Master prompt; EVID-XY-001 | `adapters/fakes.py`; `tool_selection.py` | actual: dynamic ordering, duplicate/mismatch, no-writer tests |
| REQ-STATION-002 | Master prompt; ASSUMPTION | `stations/models.py`; `stations/use_cases.py` | actual: safe-Z, namespace, show/clear and current-pose tests |
| REQ-PERSIST-002 | Master prompt; ASSUMPTION | `persistence/json_store.py`; station schema | actual: corruption, fault-stage, checksum/version and recovery tests |
| REQ-LOCK-001 | Master prompt; ASSUMPTION | `adapters/fakes.py` `FakeRunLock` | actual: double acquire, wrong release, cleanup tests |
| REQ-NONBLOCK-001 | SRC-002; SRC-003 | host/Klippy boundary | planned: fake reactor non-blocking tests |
| REQ-INSTALL-001 | Master prompt; ASSUMPTION | roadmap; installer policy | planned: sandbox idempotency tests |
| REQ-OPS-001 | Master prompt; ASSUMPTION | progress/reporting records | actual: parity/link/diff checks; planned release docs gate |
| REQ-HIL-001 | EVID-Z-INVALID-001; Master prompt | risk register; HIL run-sheet gate | actual: no physical action; planned supervised canary |
| REQ-CAMERA-001 | Master prompt; SRC-009 | `vision/capture.py` bounded local capture contracts | actual: `tests/test_phase03.py`; resource/security gate |
| REQ-CALIB-001 | Master prompt; SRC-010 | `vision/calibration.py` versioned checksummed store | actual: round-trip/corruption tests |
| REQ-DETECT-001 | Master prompt; SRC-009 | `vision/detectors.py` plugin and diagnostics model | actual: candidate/zero/ambiguous tests |
| REQ-CORPUS-002 | Master prompt; ASSUMPTION | `vision/corpus.py` immutable inventory/session split | actual: leakage test; real-corpus gate NEEDS_WORK |
| REQ-CALIB-002 | Master prompt; ASSUMPTION | `vision/calibration.py`; calibration envelope schema | actual: checksum, bounds and pre-replace fault tests |
| REQ-CORPUS-003 | Master prompt; ASSUMPTION | `vision/corpus.py` inventory/verifier | actual: relative path, hash and mismatch tests |
| REQ-BENCH-001 | Master prompt; ASSUMPTION | `vision/corpus.py` evaluate_benchmark | actual: synthetic labeled metric test; real corpus NEEDS_WORK |

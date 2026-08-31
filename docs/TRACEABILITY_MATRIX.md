# Phase 00 traceability matrix

Every requirement below occurs exactly once.

| Requirement | Evidence/source | Design artifact | Planned/actual test gate |
|---|---|---|---|
| REQ-IDENT-001 | ADR-0001 | repository identity ADR | actual: commit identity review |
| REQ-CMD-001 | SRC-001; Master prompt | command contract in master prompt | planned: command contract tests |
| REQ-STATION-001 | EVID-XY-001; Master prompt | architecture context; station policy | planned: teach contract; coordinate-default scan |
| REQ-STATE-001 | Master prompt; ASSUMPTION | `src/xyz_klipper_tool/domain/models.py`; `state_machine.py` | actual: `tests/test_domain.py` identity and illegal-transition cases |
| REQ-TOOL-001 | EVID-XY-001; Master prompt | adapter contract; measurement protocol | planned: dynamic discovery tests |
| REQ-PROVIDER-001 | EVID-Z-001; SRC-008 | `src/xyz_klipper_tool/domain/models.py` provider-specific results | actual: `tests/test_domain.py` switch/HIL separation |
| REQ-MOTION-001 | AGENTS; SRC-001; ASSUMPTION | threat model; safety reason-code catalog | planned: fault-injection invariant tests |
| REQ-SAMPLE-001 | EVID-XY-001 | sampling hierarchy design | planned: three outer-cycle test |
| REQ-STAT-001 | EVID-XY-001; Master prompt | `src/xyz_klipper_tool/domain/statistics.py` | actual: `tests/test_domain.py` n=0/n=1, counts, SD/MAD/uncertainty/drift |
| REQ-OUTLIER-001 | EVID-XY-001 | `statistics.py` declared policy and raw/filtered summaries | actual: outlier and invalid exclusion tests |
| REQ-VISION-001 | SRC-009; Master prompt | host vision boundary | planned: stale/ambiguous/corrupt frame tests |
| REQ-CORPUS-001 | SRC-009; SRC-010 | corpus and evaluation plan | planned: session split/holdout gate |
| REQ-PERSIST-001 | Master prompt; ASSUMPTION | persistence policy | planned: atomic write/power-loss tests |
| REQ-SCHEMA-001 | Master prompt; ASSUMPTION | `domain/schema.py`; `schemas/switch-measurement-result.v1.schema.json` | actual: `tests/test_schema.py` round-trip/unknown/version fault |
| REQ-EVID-001 | Phase 00 import; EVID-Z-INVALID-001 | provenance policy; evidence manifest | actual: 23/23 hash and 21/21 JSON checks |
| REQ-APPLY-001 | EVID-Z-001; Master prompt | `domain/models.py` side-effect-free ApplyPlan/RollbackPlan | actual: model construction only; writer remains out of scope |
| REQ-FRESH-001 | Master prompt; ASSUMPTION | `domain/models.py` FreshnessExpectation/FreshnessResult | actual: typed stale reason model; adapter validation remains later phase |
| REQ-SEC-001 | Master prompt; ASSUMPTION | threat model; security policy | actual: secret scan; planned: SSRF/bounds tests |
| REQ-RESOURCE-001 | Master prompt; ASSUMPTION | resource-limit policy | planned: payload/job/history limit tests |
| REQ-PORT-001 | SRC-002; Master prompt | pure `domain/` package boundary | actual: standard-library import-boundary scan |
| REQ-NONBLOCK-001 | SRC-002; SRC-003 | host/Klippy boundary | planned: fake reactor non-blocking tests |
| REQ-INSTALL-001 | Master prompt; ASSUMPTION | roadmap; installer policy | planned: sandbox idempotency tests |
| REQ-OPS-001 | Master prompt; ASSUMPTION | progress/reporting records | actual: parity/link/diff checks; planned release docs gate |
| REQ-HIL-001 | EVID-Z-INVALID-001; Master prompt | risk register; HIL run-sheet gate | actual: no physical action; planned supervised canary |

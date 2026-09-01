# Ma trận traceability Phase 00

Mỗi requirement dưới đây xuất hiện đúng một lần.

| Requirement | Bằng chứng/nguồn | Artifact thiết kế | Cổng test planned/actual |
|---|---|---|---|
| REQ-IDENT-001 | ADR-0001 | ADR danh tính kho | actual: review identity commit |
| REQ-CMD-001 | SRC-001; Master prompt | command contract trong master prompt | planned: command contract test |
| REQ-STATION-001 | EVID-XY-001; Master prompt | architecture context; station policy | planned: teach contract; scan default tọa độ |
| REQ-STATE-001 | Master prompt; ASSUMPTION | hierarchy identity trong `domain/models.py`; `state_machine.py` | actual: non-empty hierarchy và transition terminal/fault trong `tests/test_domain.py` |
| REQ-TOOL-001 | EVID-XY-001; Master prompt | adapter contract; protocol đo | planned: dynamic discovery test |
| REQ-PROVIDER-001 | EVID-Z-001; SRC-008 | kết quả SwitchZ/CartographerTouch và series đồng nhất trong `domain/models.py` | actual: test cô lập provider/round-trip trong `tests/test_domain.py`, `tests/test_schema.py` |
| REQ-MOTION-001 | AGENTS; SRC-001; ASSUMPTION | threat model; reason-code safety | planned: fault-injection invariant test |
| REQ-SAMPLE-001 | EVID-XY-001 | thiết kế sampling hierarchy | planned: test ba outer-cycle |
| REQ-STAT-001 | EVID-XY-001; Master prompt | Summary/StatisticResult trong `domain/statistics.py` | actual: test sufficiency, counts, SD/MAD/uncertainty/reference drift trong `tests/test_domain.py` |
| REQ-OUTLIER-001 | EVID-XY-001 | raw bất biến, summary unfiltered/filtered và Rejection trong `statistics.py` | actual: test rejection có lý do, loại invalid, validate threshold |
| REQ-VISION-001 | SRC-009; Master prompt | ranh giới vision host | planned: test frame cũ/mơ hồ/hỏng |
| REQ-CORPUS-001 | SRC-009; SRC-010 | kế hoạch corpus/evaluation | planned: session split/holdout |
| REQ-PERSIST-001 | Master prompt; ASSUMPTION | persistence policy | planned: atomic write/power-loss |
| REQ-SCHEMA-001 | Master prompt; ASSUMPTION | `domain/schema.py`; cặp JSON Schema v1 | actual: test contract, round-trip, malformed/version/enum/non-finite fault trong `tests/test_schema.py` |
| REQ-EVID-001 | Import Phase 00; EVID-Z-INVALID-001 | provenance policy; manifest | actual: hash 23/23 và JSON 21/21 |
| REQ-APPLY-001 | EVID-Z-001; Master prompt | ApplyPlan/RollbackPlan không side effect trong `domain/models.py` | actual: invariant preview-only/rollback trong `tests/test_domain.py`; writer để phase sau |
| REQ-FRESH-001 | Master prompt; ASSUMPTION | FreshnessExpectation/FreshnessResult trong `domain/models.py` | actual: model reason stale có kiểu; adapter validation để phase sau |
| REQ-SEC-001 | Master prompt; ASSUMPTION | threat model; security policy | actual: secret scan; planned: SSRF/bounds |
| REQ-RESOURCE-001 | Master prompt; ASSUMPTION | resource-limit policy | planned: limit payload/job/history |
| REQ-PORT-001 | SRC-002; Master prompt | boundary package thuần `domain/` | actual: scan import standard library |
| REQ-PORT-002 | Master prompt; ASSUMPTION | protocol boundary có kiểu trong `ports/contracts.py` | actual: `tests/test_phase02.py`; mypy/pyright |
| REQ-SIM-001 | Master prompt; EVID-XY-001 | `adapters/fakes.py`; `tool_selection.py` | actual: test thứ tự động, duplicate/mismatch, không writer |
| REQ-STATION-002 | Master prompt; ASSUMPTION | `stations/models.py`; `stations/use_cases.py` | actual: test safe-Z, namespace, show/clear và current-pose |
| REQ-PERSIST-002 | Master prompt; ASSUMPTION | `persistence/json_store.py`; schema station | actual: test corrupt, fault-stage, checksum/version và recovery |
| REQ-LOCK-001 | Master prompt; ASSUMPTION | `FakeRunLock` trong `adapters/fakes.py` | actual: test double acquire, wrong release, cleanup |
| REQ-NONBLOCK-001 | SRC-002; SRC-003 | boundary host/Klippy | planned: fake reactor non-blocking |
| REQ-INSTALL-001 | Master prompt; ASSUMPTION | roadmap; installer policy | planned: sandbox idempotency |
| REQ-OPS-001 | Master prompt; ASSUMPTION | progress/reporting records | actual: parity/link/diff; planned release docs |
| REQ-HIL-001 | EVID-Z-INVALID-001; Master prompt | risk register; HIL run-sheet gate | actual: không hành động vật lý; planned canary |
| REQ-CAMERA-001 | Master prompt; SRC-009 | contract capture local bounded trong `vision/capture.py` | actual: `tests/test_phase03.py`; gate resource/security |
| REQ-CALIB-001 | Master prompt; SRC-010 | store versioned checksum trong `vision/calibration.py` | actual: test round-trip/corruption |
| REQ-DETECT-001 | Master prompt; SRC-009 | model plugin/diagnostic trong `vision/detectors.py` | actual: test candidate/zero/ambiguous |
| REQ-CORPUS-002 | Master prompt; ASSUMPTION | inventory/split session trong `vision/corpus.py` | actual: test leakage; gate corpus thật NEEDS_WORK |
| REQ-CALIB-002 | Master prompt; ASSUMPTION | `vision/calibration.py`; schema envelope calibration | actual: test checksum, bound, rotation, recovery corrupt/traversal và fault trước replace |
| REQ-CORPUS-003 | Master prompt; ASSUMPTION | `vision/corpus.py` inventory/verifier | actual: test path tương đối, hash và mismatch |
| REQ-BENCH-001 | Master prompt; ASSUMPTION | `vision/corpus.py` evaluate_benchmark; artifact/schema benchmark synthetic | actual: test report hai candidate, TP/FP/FN/TN và center-error dẫn xuất; corpus thật NEEDS_WORK |

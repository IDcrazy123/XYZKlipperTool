# Ma trận traceability Phase 00

Mỗi requirement dưới đây xuất hiện đúng một lần.

| Requirement | Bằng chứng/nguồn | Artifact thiết kế | Cổng test planned/actual |
|---|---|---|---|
| REQ-IDENT-001 | ADR-0001 | ADR danh tính kho | actual: review identity commit |
| REQ-CMD-001 | SRC-001; Master prompt | command contract trong master prompt | planned: command contract test |
| REQ-STATION-001 | EVID-XY-001; Master prompt | architecture context; station policy | planned: teach contract; scan default tọa độ |
| REQ-STATE-001 | Master prompt; ASSUMPTION | requirements; schema persistence | planned: ID/state round-trip test |
| REQ-TOOL-001 | EVID-XY-001; Master prompt | adapter contract; protocol đo | planned: dynamic discovery test |
| REQ-PROVIDER-001 | EVID-Z-001; SRC-008 | ADR/contract provider | planned: fixture switch/Cartographer |
| REQ-MOTION-001 | AGENTS; SRC-001; ASSUMPTION | threat model; reason-code safety | planned: fault-injection invariant test |
| REQ-SAMPLE-001 | EVID-XY-001 | thiết kế sampling hierarchy | planned: test ba outer-cycle |
| REQ-STAT-001 | EVID-XY-001; Master prompt | yêu cầu statistics | planned: test n=0/n=1 và summary |
| REQ-OUTLIER-001 | EVID-XY-001 | estimator/outlier policy | planned: fixture outlier T3 được giữ |
| REQ-VISION-001 | SRC-009; Master prompt | ranh giới vision host | planned: test frame cũ/mơ hồ/hỏng |
| REQ-CORPUS-001 | SRC-009; SRC-010 | kế hoạch corpus/evaluation | planned: session split/holdout |
| REQ-PERSIST-001 | Master prompt; ASSUMPTION | persistence policy | planned: atomic write/power-loss |
| REQ-SCHEMA-001 | Master prompt; ASSUMPTION | schema/version plan | planned: migration/round-trip |
| REQ-EVID-001 | Import Phase 00; EVID-Z-INVALID-001 | provenance policy; manifest | actual: hash 23/23 và JSON 21/21 |
| REQ-APPLY-001 | EVID-Z-001; Master prompt | boundary ADR apply transaction | planned: fault test preview/backup/rollback |
| REQ-FRESH-001 | Master prompt; ASSUMPTION | freshness validation | planned: reject stale/mismatch |
| REQ-SEC-001 | Master prompt; ASSUMPTION | threat model; security policy | actual: secret scan; planned: SSRF/bounds |
| REQ-RESOURCE-001 | Master prompt; ASSUMPTION | resource-limit policy | planned: limit payload/job/history |
| REQ-PORT-001 | SRC-002; Master prompt | architecture context; ports | planned: domain import/fake adapter |
| REQ-NONBLOCK-001 | SRC-002; SRC-003 | boundary host/Klippy | planned: fake reactor non-blocking |
| REQ-INSTALL-001 | Master prompt; ASSUMPTION | roadmap; installer policy | planned: sandbox idempotency |
| REQ-OPS-001 | Master prompt; ASSUMPTION | progress/reporting records | actual: parity/link/diff; planned release docs |
| REQ-HIL-001 | EVID-Z-INVALID-001; Master prompt | risk register; HIL run-sheet gate | actual: không hành động vật lý; planned canary |

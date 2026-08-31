# Initial risk register

| ID | Risk | State | Mitigation/owner |
|---|---|---|---|
| RISK-001 | Historical coordinates become defaults | `OPEN` | station teach only; domain owner |
| RISK-002 | Missing/ambiguous provider sign semantics | `OPEN` | source-pinned contracts and fixtures; Z owner |
| RISK-003 | Outlier or invalid evidence is aggregated | `OPEN` | immutable raw, status-aware estimator; domain owner |
| RISK-004 | Reactor blocked by camera/network work | `OPEN` | host job boundary and fake-Klipper test |
| RISK-005 | Apply mutates production without rollback | `OPEN` | separate preview/backup/confirmation transaction |
| RISK-006 | Imported evidence contains secrets | `MITIGATED-PHASE-00` | scan found none; repeat on support bundles |
| RISK-007 | Offline tests mistaken for physical safety | `OPEN` | explicit `REQUIRES_HIL`, supervised run sheet |
| RISK-008 | Partial station write becomes current state | `MITIGATED-PHASE-02` | atomic temp/flush/replace, checksum, backup, and fault tests; persistence owner |
| RISK-009 | Ambiguous tool or provider state is selected | `MITIGATED-PHASE-02` | typed runtime validation, deterministic discovery, fail-closed selection; adapter owner |
| RISK-010 | SAFE_Z omission is treated as clearance | `MITIGATED-PHASE-02` | omitted SAFE_Z rejects with `UNSAFE_APPROACH`; station owner |

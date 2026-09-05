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
| RISK-011 | No reviewed, labeled, calibrated real camera-frame holdout is available for reliability evidence | `OPEN` | keep 75 hash-verified real frames `WARNING`/excluded; require reviewed center labels and independent session split; synthetic tests are mechanics-only; vision owner |
| RISK-012 | Platform directory durability after fsync/replace is not a portable guarantee | `OPEN` | best-effort file durability only; require platform-specific validation before production persistence claim |
| RISK-013 | HIL canary may proceed with ambiguous tool identity or unhomed axes | `OPEN` | fail closed; preserve partial evidence; require fresh explicit operator authorization and successful `xyz` homing before continuation |

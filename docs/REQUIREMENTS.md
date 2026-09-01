# Phase 00 requirements baseline

Each stable ID occurs once and has at least one `SRC-*`, `EVID-*`, or `ASSUMPTION` reference.

| ID | Requirement | State | Source/evidence |
|---|---|---|---|
| REQ-IDENT-001 | Preserve independent repository identity and package slug | `IMPLEMENTED` | ADR-0001 |
| REQ-CMD-001 | Preserve the v1 station, measurement, report, apply, and rollback command capabilities | `PLANNED` | Master prompt; SRC-001 |
| REQ-STATION-001 | Teach and persist camera/Z stations from current pose; never use historical coordinates as defaults | `PLANNED` | Master prompt; EVID-XY-001 |
| REQ-STATE-001 | Use explicit claim states, run/cycle/visit/sample IDs, station revision, fingerprint, and calibration identity | `PLANNED` | Master prompt; ASSUMPTION: IDs are immutable |
| REQ-TOOL-001 | Discover tools dynamically and select a reference | `PLANNED` | Master prompt; EVID-XY-001 |
| REQ-PROVIDER-001 | Keep switch and Cartographer Touch Z providers separate with explicit contracts | `PLANNED` | Master prompt; EVID-Z-001; SRC-008 |
| REQ-MOTION-001 | Enforce homing, limits, active-tool, clearance, bounded approach, abort, and recovery invariants | `PLANNED` | AGENTS; SRC-001; ASSUMPTION: provider owns approach envelope |
| REQ-SAMPLE-001 | Use three independent outer pickup cycles and retain inner-frame hierarchy | `PLANNED` | EVID-XY-001 |
| REQ-STAT-001 | Report mean, median, sample SD when `n >= 2`, MAD, range, drift, uncertainty, and verdict reasons | `PLANNED` | Master prompt; EVID-XY-001 |
| REQ-OUTLIER-001 | Declare outlier policy before evaluation; preserve raw and produce unfiltered/filtered summaries | `PLANNED` | Master prompt; EVID-XY-001 |
| REQ-VISION-001 | Bound camera capture/detection and reject stale, ambiguous, corrupt, or unsupported frames | `PLANNED` | Master prompt; SRC-009 |
| REQ-CORPUS-001 | Build session-separated labeled corpus and benchmark candidate vision methods | `PLANNED` | Master prompt; SRC-009; SRC-010 |
| REQ-PERSIST-001 | Write state atomically with backup rotation and never mutate completed raw evidence | `PLANNED` | Master prompt; ASSUMPTION: filesystem supports rename |
| REQ-SCHEMA-001 | Version schemas, support migrations/round trips, and fail closed on unsupported major versions | `PLANNED` | Master prompt; ASSUMPTION: schema versions are monotonic |
| REQ-EVID-001 | Preserve immutable raw evidence, hashes, status, provenance, errors, and cleanup events | `IMPLEMENTED` | Phase 00 import; EVID-Z-INVALID-001 |
| REQ-APPLY-001 | Keep report-only default and separate apply with preview, backup, confirmation, and rollback | `PLANNED` | Master prompt; EVID-Z-001 |
| REQ-FRESH-001 | Reject stale, mismatched, invalid, warning, or changed-configuration evidence during apply | `PLANNED` | Master prompt; ASSUMPTION: fingerprint is freshness authority |
| REQ-SEC-001 | Bind local services to loopback/Unix socket, redact secrets, prevent SSRF/path traversal, and disable cloud by default | `PLANNED` | Master prompt; ASSUMPTION: local-only default |
| REQ-RESOURCE-001 | Bound body/image/history/jobs/retries/queues/selectors/strings/numbers and pin dependencies | `PLANNED` | Master prompt; ASSUMPTION: configured limits are finite |
| REQ-PORT-001 | Keep domain independent and expose the required ports/adapters with fakes before hardware | `PLANNED` | Master prompt; SRC-002 |
| REQ-PORT-002 | Define typed printer-state/current-pose, clock, lock, store, reader, and writer boundaries with explicit side-effect contracts | `IMPLEMENTED` | Master prompt; ASSUMPTION: ports are dependency-inversion boundaries |
| REQ-SIM-001 | Provide deterministic scripted fakes, dynamic tool selection, and fault injection without physical actions | `IMPLEMENTED` | Master prompt; EVID-XY-001 |
| REQ-STATION-002 | Teach/show/clear provider-separated stations from explicit current pose; omitted SAFE_Z fails closed | `IMPLEMENTED` | Master prompt; ASSUMPTION: no validated clearance default |
| REQ-PERSIST-002 | Persist versioned station state atomically with checksum, bounded backup, recovery, and fail-closed corruption handling | `IMPLEMENTED` | Master prompt; ASSUMPTION: filesystem rename/fsync contract |
| REQ-LOCK-001 | Reject concurrent run/teach/apply ownership conflicts and preserve deterministic lock cleanup | `IMPLEMENTED` | Master prompt; ASSUMPTION: one active local owner |
| REQ-NONBLOCK-001 | Keep camera/network/filesystem work outside the Klipper reactor and use bounded coordination | `PLANNED` | SRC-002; SRC-003 |
| REQ-INSTALL-001 | Make install/update/rollback/uninstall idempotent, dry-run, scope-checked, and non-destructive by default | `PLANNED` | Master prompt; ASSUMPTION: no implicit purge |
| REQ-OPS-001 | Provide evidence, diagnostics, support redaction, documentation, and exact progress/reporting records | `PLANNED` | Master prompt; ASSUMPTION: report-only operations |
| REQ-HIL-001 | Keep physical compatibility and production readiness `REQUIRES_HIL` until a supervised canary passes | `REQUIRES_HIL` | Master prompt; EVID-Z-INVALID-001 |
| REQ-CAMERA-001 | Bound local-only camera capture, encoded data, dimensions, pixels, age, timeout, and retries | `IMPLEMENTED` | Master prompt; SRC-009 |
| REQ-CALIB-001 | Persist versioned camera calibration with transform, residual, uncertainty, identity, provenance, checksum, and atomicity | `IMPLEMENTED` | Master prompt; SRC-010; ASSUMPTION: calibration store is local |
| REQ-DETECT-001 | Provide detector plugins with typed zero/ambiguous/corrupt/stale/calibration-mismatch diagnostics | `IMPLEMENTED` | Master prompt; SRC-009 |
| REQ-CORPUS-002 | Keep immutable corpus hashes and session-separated holdout splits; synthetic data cannot establish reliability | `IMPLEMENTED` | Master prompt; ASSUMPTION: real sanitized corpus is unavailable |

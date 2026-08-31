# Phase 00 requirements baseline

| ID | Requirement | State | Source/evidence |
|---|---|---|---|
| REQ-IDENT-001 | Preserve independent identity and slug decision | `IMPLEMENTED` | ADR-0001 |
| REQ-STATION-001 | Teach and persist camera/Z stations from current pose; never use historical coordinates as defaults | `PLANNED` | Master prompt; EVID-XY-001 |
| REQ-PROVIDER-001 | Keep switch and Cartographer Touch Z providers separate | `PLANNED` | Master prompt; EVID-Z-001 |
| REQ-TOOL-001 | Discover tools dynamically and select a reference | `PLANNED` | Master prompt; EVID-XY-001 |
| REQ-SAMPLE-001 | Baseline three independent outer pickup cycles and retain inner-frame hierarchy | `PLANNED` | Master prompt; EVID-XY-001 |
| REQ-EVID-001 | Preserve immutable raw evidence, hashes, status and provenance | `IMPLEMENTED` | Phase 00 import and manifest |
| REQ-STAT-001 | Report robust statistics and explicit invalid/warning verdicts | `PLANNED` | Master prompt; EVID-XY-001 |
| REQ-APPLY-001 | Report-only default; separate previewed, backed-up, reversible apply transaction | `PLANNED` | Master prompt; EVID-Z-001 |
| REQ-SAFE-001 | Fail closed on unsafe or stale state; no implicit physical action | `PLANNED` | AGENTS; Klipper docs |
| REQ-SEC-001 | Loopback defaults, bounded inputs, redaction, no cloud upload by default | `PLANNED` | Master prompt |

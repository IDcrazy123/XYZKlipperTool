# Project Status

- Project: **XYZ Klipper Tool**
- Repository state: Phase 01 supervisor-approved at `9d58fecb6cc19342c1bcd9dd62eafb8bf03c1a0d`
- Production readiness: **NOT READY**
- Current phase: Phase 02 — ports, fake adapters, simulator, and station persistence
- Next gate: supervisor review of Phase 02; physical behavior remains `REQUIRES_HIL`
- Physical printer actions: none authorized by this repository state

## Phase ledger

| Phase | State | Evidence |
|---|---|---|
| 00 Governance, sources, license, evidence | `IMPLEMENTED` | Paired governance artifacts, 23-file SHA-256 manifest, 21 Z JSON imports, offline checks passed |
| 01 Domain model, units, signs, statistics | `PASS` | Supervisor-approved commit `9d58fecb6cc19342c1bcd9dd62eafb8bf03c1a0d`; 16/16 pinned tests, 95% coverage, all listed offline gates pass; physical behavior remains `REQUIRES_HIL` |
| 02 Adapters and simulator | `PASS` | Supervisor correction gates pass at `a6a3c9527e5870b10a53b5b9f6eb124d062fe7a7`; 26 tests, 91% coverage, physical behavior remains `REQUIRES_HIL` |
| 03 Camera and vision pipeline | `PLANNED` | Not started |
| 04 Independent-cycle X/Y orchestration | `PLANNED` | Not started |
| 05 Physical-switch Z provider | `PLANNED` | Not started |
| 06 Cartographer Touch Z provider | `PLANNED` | Not started |
| 07 Reviewed apply transaction and rollback | `PLANNED` | Not started |
| 08 Host API and service | `PLANNED` | Not started |
| 09 Klipper extension and commands | `PLANNED` | Not started |
| 10 Installer, update, uninstall | `PLANNED` | Not started |
| 11 Documentation, security, release gates | `PLANNED` | Not started |
| 12 Supervised HIL canary | `REQUIRES_HIL` | Not authorized |

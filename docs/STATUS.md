# Project Status

- Project: **XYZ Klipper Tool**
- Repository state: Phase 02 supervisor-approved at candidate `ce99ca14b4df5e870a79364ef188884c0394dc65`
- Production readiness: **NOT READY**
- Current phase: Phase 03 — camera capture, calibration, and detector framework
- Next gate: supervisor review of Phase 03; physical behavior remains `REQUIRES_HIL`
- Physical printer actions: none authorized by this repository state

## Phase ledger

| Phase | State | Evidence |
|---|---|---|
| 00 Governance, sources, license, evidence | `IMPLEMENTED` | Paired governance artifacts, 23-file SHA-256 manifest, 21 Z JSON imports, offline checks passed |
| 01 Domain model, units, signs, statistics | `PASS` | Supervisor-approved commit `9d58fecb6cc19342c1bcd9dd62eafb8bf03c1a0d`; 16/16 pinned tests, 95% coverage, all listed offline gates pass; physical behavior remains `REQUIRES_HIL` |
| 02 Adapters and simulator | `PASS` | Supervisor-approved candidate `ce99ca14b4df5e870a79364ef188884c0394dc65`; 27 tests and 91% coverage; directory durability remains OPEN and physical behavior `REQUIRES_HIL` |
| 03 Camera and vision pipeline | `IMPLEMENTED` | Offline candidate; real sanitized corpus unavailable, holdout/reliability gate `NEEDS_WORK`; physical behavior `REQUIRES_HIL` |
| 04 Independent-cycle X/Y orchestration | `PLANNED` | Not started |
| 05 Physical-switch Z provider | `PLANNED` | Not started |
| 06 Cartographer Touch Z provider | `PLANNED` | Not started |
| 07 Reviewed apply transaction and rollback | `PLANNED` | Not started |
| 08 Host API and service | `PLANNED` | Not started |
| 09 Klipper extension and commands | `PLANNED` | Not started |
| 10 Installer, update, uninstall | `PLANNED` | Not started |
| 11 Documentation, security, release gates | `PLANNED` | Not started |
| 12 Supervised HIL canary | `REQUIRES_HIL` | Not authorized |

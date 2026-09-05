# Project Status

- Project: **XYZ Klipper Tool**
- Repository state: Phase 02 supervisor-approved at candidate `ce99ca14b4df5e870a79364ef188884c0394dc65`
- Production readiness: **NOT READY**
- Current phase: Phase 03 — camera capture, calibration, and detector framework
- Phase state: `NEEDS_WORK` — offline evidence/persistence tooling is candidate only; real sanitized session-separated holdout is absent
- Next gate: Phase 03 remains `NEEDS_WORK`; partial HIL canary aborted fail-closed, synthetic holdout is not reliability evidence, and physical behavior remains `REQUIRES_HIL`
- Physical printer actions: blocked; fresh explicit operator authorization and successful `xyz` homing are required

## Phase ledger

| Phase | State | Evidence |
|---|---|---|
| 00 Governance, sources, license, evidence | `IMPLEMENTED` | Paired governance artifacts, 23-file SHA-256 manifest, 21 Z JSON imports, offline checks passed |
| 01 Domain model, units, signs, statistics | `PASS` | Supervisor-approved commit `9d58fecb6cc19342c1bcd9dd62eafb8bf03c1a0d`; 16/16 pinned tests, 95% coverage, all listed offline gates pass; physical behavior remains `REQUIRES_HIL` |
| 02 Adapters and simulator | `PASS` | Supervisor-approved candidate `ce99ca14b4df5e870a79364ef188884c0394dc65`; 27 tests and 91% coverage; directory durability remains OPEN and physical behavior `REQUIRES_HIL` |
| 03 Camera and vision pipeline | `NEEDS_WORK` | Bounded host JPEG adapter and independent candidate tests implemented; real user images remain unlabeled/excluded, synthetic reliability remains unproven, HIL partial run has 1 invalid T0 + 3 excluded LED-on T1 frames and 0 T2 frames; physical behavior `REQUIRES_HIL` |
| 04 Independent-cycle X/Y orchestration | `PLANNED` | Not started |
| 05 Physical-switch Z provider | `PLANNED` | Not started |
| 06 Cartographer Touch Z provider | `PLANNED` | Not started |
| 07 Reviewed apply transaction and rollback | `PLANNED` | Not started |
| 08 Host API and service | `PLANNED` | Not started |
| 09 Klipper extension and commands | `PLANNED` | Not started |
| 10 Installer, update, uninstall | `PLANNED` | Not started |
| 11 Documentation, security, release gates | `PLANNED` | Not started |
| 12 Supervised HIL canary | `REQUIRES_HIL` | Not authorized |

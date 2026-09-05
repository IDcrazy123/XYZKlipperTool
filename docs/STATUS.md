# Project Status

- Project: **XYZ Klipper Tool**
- Repository state: Phase 02 supervisor-approved at candidate `ce99ca14b4df5e870a79364ef188884c0394dc65`
- Production readiness: **NOT READY**
- Current phase: Phase 03 — camera capture, calibration, and detector framework
- Phase state: `NEEDS_WORK` — bounded host OpenCV adapter and archived pixel-candidate inspection are IMPLEMENTED; 75 new real frames are hash-verified but remain `WARNING`, unlabeled, uncalibrated, and excluded
- Next gate: Phase 03 remains `NEEDS_WORK`; reviewed center ground truth plus independent labeled calibration/development/holdout sessions are absent, synthetic holdout is not reliability evidence, and physical behavior remains `REQUIRES_HIL`
- Physical printer actions: blocked; every new run requires fresh explicit operator authorization and a new state/homing preflight

## Phase ledger

| Phase | State | Evidence |
|---|---|---|
| 00 Governance, sources, license, evidence | `IMPLEMENTED` | Paired governance artifacts, 23-file SHA-256 manifest, 21 Z JSON imports, offline checks passed |
| 01 Domain model, units, signs, statistics | `PASS` | Supervisor-approved commit `9d58fecb6cc19342c1bcd9dd62eafb8bf03c1a0d`; 16/16 pinned tests, 95% coverage, all listed offline gates pass; physical behavior remains `REQUIRES_HIL` |
| 02 Adapters and simulator | `PASS` | Supervisor-approved candidate `ce99ca14b4df5e870a79364ef188884c0394dc65`; 27 tests and 91% coverage; directory durability remains OPEN and physical behavior `REQUIRES_HIL` |
| 03 Camera and vision pipeline | `NEEDS_WORK` | Bounded host OpenCV adapter plus calibration-free candidate reports/overlays implemented; two new sessions provide 75 hash-verified real frames, all `WARNING`/excluded without ground truth or calibration; generic ROI contours remain ambiguous (3–28); physical behavior `REQUIRES_HIL` |
| 04 Independent-cycle X/Y orchestration | `PLANNED` | Not started |
| 05 Physical-switch Z provider | `PLANNED` | Not started |
| 06 Cartographer Touch Z provider | `PLANNED` | Not started |
| 07 Reviewed apply transaction and rollback | `PLANNED` | Not started |
| 08 Host API and service | `PLANNED` | Not started |
| 09 Klipper extension and commands | `PLANNED` | Not started |
| 10 Installer, update, uninstall | `PLANNED` | Not started |
| 11 Documentation, security, release gates | `PLANNED` | Not started |
| 12 Supervised HIL canary | `REQUIRES_HIL` | Not authorized |

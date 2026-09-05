# Imported evidence index

Imported under `evidence/imported/` on 2026-08-31. Source copies were compared by SHA-256 before commit; no secrets were found by the Phase 00 scan. Raw files are `OBSERVED`, immutable, report-only evidence.

| ID | Content | Count/status | Source |
|---|---|---|---|
| EVID-XY-001 | kTAMV CSV and companion report; 3 independent cycles, T0–T4 | 2 files; observed | All-Config experiments directory |
| EVID-Z-001 | Historical Z JSON, switch and Cartographer Touch | 21 files: 5 switch + 16 Cartographer; includes `WARNING` and `INVALID` | Two recorded All-Config backup locations |
| EVID-Z-INVALID-001 | `20260826-114524-081-z-switch-01.json` | `INVALID`, empty offsets, TMC ShortToSupply_A and cleanup failures | pre-resume backup |

The prior baseline said 20 Z files in one directory; the complete related evidence set is 21 after importing the separately located invalid run. Historical coordinates, temperatures, scale, tool names and tolerances are not product defaults.

## Phase 03 HIL partial run

`evidence/hil/phase-03/partial-run-manifest.json` records four raw JPEGs from the interrupted canary accounting: one `INVALID/WRONG_CAMERA_SOURCE` T0 frame and three `OBSERVED_LED_ON` T1 frames, all excluded from algorithm/corpus use. No T2 frame was captured or claimed. The run aborted fail-closed on ambiguous tool identity (`tool_number=-1`, `detected_tool_number=2`); a later supervisor check also found empty `homed_axes`. Raw byte sizes and SHA-256 values match metadata. Continuation requires fresh explicit authorization and successful `xyz` homing.

The user-created `picture/` directory was inventoried read-only in `evidence/hil/phase-03/user-provided-picture-inventory.json` as `USER_PROVIDED_UNLABELED`. Its 17 original files are excluded from all validated corpora pending supervisor review; session, ground-truth, tool, illumination, camera identity, and capture timestamp fields are missing.

## Phase 03 organized capture library

Two later operator-authorized VoronBed sessions are stored outside the repository under `D:\Desktop\XYZKlipperTool-Captures`: baseline `20260905T152727Z_VoronBed_L001_round01` (15 JPEGs) and stress sweep `20260905T153618Z_VoronBed_L004-L255_sweep01` (60 JPEGs). Captured photos are isolated under `01_PHOTOS/<session>/T0` through `T4`; immutable manifests/metadata are under `80_EVIDENCE`; derived reports and overlays are under `90_TESTS_ANALYSIS`. The tool names describe these observed sessions only and are not the product's tool-count model.

All 75 files (21,617,906 bytes) revalidated against manifest byte counts and SHA-256 with zero failures. The baseline and sweep manifest hashes are respectively `c36da555f54e7f5131073410224b4d6e0f41101523e66809a7324d8faa472f7e` and `0e01b74b3eee4d9d030981e650150b56dcc2076eaf866180a5f9b012620e4020`. Every record remains `WARNING_DEVELOPMENT_ONLY_REQUIRES_REVIEW`, `accepted=false`, and excluded from calibration/holdout. The sanitized repository summary is `artifacts/test-runs/phase-03-camera-cv/real-capture-development-analysis.json`; raw JPEGs and path-bearing generated reports are not committed. No later offline analysis grants continuing authority for printer motion or other HIL actions.

# Source ledger

Access date for all rows: 2026-08-31. No upstream implementation is copied.

| ID | URL | Pinned version | Claim supported | License | Ambiguity/follow-up |
|---|---|---|---|---|---|
| SRC-001 | https://www.klipper3d.org/G-Codes.html | current docs; compatibility commit TBD | G-Code/query/probe command surface | Klipper project GPL-3.0; docs terms to verify | Pin supported release before Phase 09 |
| SRC-002 | https://www.klipper3d.org/Code_Overview.html | current docs; compatibility commit TBD | reactor, extras, object/event architecture | Klipper project GPL-3.0 | Verify APIs against pinned commit |
| SRC-003 | https://github.com/Klipper3d/klipper | `f0892d82b0f1c1228454f09eb508eddde2250f4b` | source behavior | GPL-3.0 | Compatibility fixture required |
| SRC-004 | https://moonraker.readthedocs.io/en/latest/external_api/introduction/ | current docs | local HTTP/JSON-RPC/WebSocket concepts | Moonraker license to verify before code reuse | Pin supported version |
| SRC-005 | https://github.com/TypQxQ/kTAMV | `72421f2d54da0de8701c4f84449c6e6b7d060301` | behavioral comparison only | GPL-3.0 | No code copying |
| SRC-006 | https://github.com/TypQxQ/KTC | `b880e37a960c4746a370b7f6ac76a6a829430387` | candidate adapter behavior | GPL-3.0 | Contract tests before adapter |
| SRC-007 | https://github.com/viesturz/klipper-toolchanger | `94756dfde9b729fd69f9b8780067821c5c99a528` | alternate adapter semantics | GPL-3.0 | Verify sign semantics |
| SRC-008 | https://docs.cartographer3d.com/cartographer-probe/installation-and-setup/software-configuration/touch-calibration | current page | Touch flow and safety warnings | Documentation license/terms not pinned | Re-open and snapshot before HIL |
| SRC-009 | https://docs.opencv.org/4.12.0/d4/d70/tutorial_hough_circle.html | 4.12.0 docs | candidate circle detector | Apache-2.0 project; no code copied | Benchmark on labeled corpus |
| SRC-010 | https://docs.opencv.org/4.12.0/d4/d94/tutorial_camera_calibration.html | 4.12.0 docs | calibration concepts | Apache-2.0 project; no code copied | Define model/metrics |
| SRC-011 | https://developers.openai.com/api/docs/models/gpt-5.6-luna | current page | requested phase-agent setting | OpenAI terms | Operational instruction only |

Primary source access was observed, not a claim of hardware compatibility. Source URLs, versions and unresolved items must be updated before dependent implementation.

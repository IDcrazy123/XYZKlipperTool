# Primary Source Map

Status: `OBSERVED` during repository bootstrap on 2026-08-31. Phase 00 must re-open every source, pin applicable versions/commits, and record any changed behavior before implementation.

| Area | Primary source | Supported use | Required follow-up |
|---|---|---|---|
| Klipper G-Code and probing | <https://www.klipper3d.org/G-Codes.html> | Command names and official probing/query behavior | Pin the Klipper version supported by v1 and test command availability |
| Klipper host extension architecture | <https://www.klipper3d.org/Code_Overview.html> | `klippy/extras`, object lookup, event handlers, reactor constraints, status contract | Inspect the supported Klipper commit; prohibit blocking camera work in the reactor |
| Klipper source | <https://github.com/Klipper3d/klipper> | API behavior that public docs do not fully specify | Link each compatibility shim to a commit and test fixture |
| Moonraker external API | <https://moonraker.readthedocs.io/en/latest/external_api/introduction/> | HTTP, JSON-RPC, WebSocket events/responses, local Unix socket | Define versioned client contract, timeouts, authentication, and reconnect behavior |
| kTAMV upstream | <https://github.com/TypQxQ/kTAMV> | Behavioral comparison for camera/server split and operator workflow | Record exact commit; do not copy implementation before license/provenance review |
| KTC v2 | <https://github.com/TypQxQ/KTC> | One candidate toolchanger adapter and persistent-state behavior | Record exact supported version and create fake-state contract tests |
| Klipper Toolchanger | <https://github.com/viesturz/klipper-toolchanger> | Another adapter; dynamic tool/status/offset semantics | Pin docs/source commit and verify sign conventions against fixtures |
| Cartographer Touch calibration | <https://docs.cartographer3d.com/cartographer-probe/installation-and-setup/software-configuration/touch-calibration> | Provider command flow and physical safety warnings | Snapshot the exact docs, verify firmware compatibility and command outputs before HIL |
| OpenCV Hough circles | <https://docs.opencv.org/4.12.0/d4/d70/tutorial_hough_circle.html> | One candidate circle-detection technique | Treat as a candidate, benchmark against labeled nozzle corpus, reject if evidence loses |
| OpenCV camera calibration | <https://docs.opencv.org/4.12.0/d4/d94/tutorial_camera_calibration.html> | Calibration concepts and degeneracy warnings | Define the actual calibration model and acceptance metrics from representative frames |
| GPT-5.6 Luna | <https://developers.openai.com/api/docs/models/gpt-5.6-luna> | Requested cost-sensitive phase agent and supported reasoning settings | Use `gpt-5.6-luna`, reasoning `medium`, unless an ADR records a measured reason to change |

## Source policy

1. Use official documentation or the owning upstream repository first.
2. Search issues only to identify hypotheses; do not treat an issue comment as specification.
3. Record URL, access timestamp, version/commit, exact supported claim, conflict notes, and license.
4. When docs and observed behavior disagree, preserve both, reproduce on a simulator or approved HIL run, and block implementation until the contract is resolved.
5. No source may justify a machine-specific default coordinate. Stations are taught by command.

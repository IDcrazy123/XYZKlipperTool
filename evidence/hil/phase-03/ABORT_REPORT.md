# Phase 03 HIL partial-run abort report

Status: `ABORTED_FAIL_CLOSED`; this is evidence accounting, not a supervisor PASS and not a reliability result.

## Exact completed actions

- Preserved one legacy 8086-source JPEG as `INVALID` with reason `WRONG_CAMERA_SOURCE`; it is excluded from every corpus.
- Preserved exactly three VoronBed JPEGs for T1 as `OBSERVED_LED_ON`; all three are excluded from the LED-off and algorithm corpora.
- The attempted T2 LED-off continuation was stopped before accepted XY movement or capture. No T2 JPEG exists and no T2 result is claimed.
- The first malformed `SET_LED` attempt, subsequent valid runtime LED commands, and the ambiguous-tool stop remain in the operator/session logs outside this repository artifact.
- No product source, algorithm, raw JPEG, or metadata byte was rewritten during this recovery.

## Stop conditions

The initial T2 LED-off query showed all T0–T4 `color_data` channels exactly zero, but `toolchanger.tool_number=-1` conflicted with `detected_tool_number=2`; capture was therefore rejected fail-closed. A later supervisor query on 2026-09-05 observed the printer stationary at displayed X170 Y20 Z40 with T0 declared/detected and heater targets 0, but `homed_axes` was empty. No homing, motion, camera, LED, or Moonraker command is authorized by this report.

## Verification

The immutable partial-run manifest records four raw JPEGs: one `INVALID`, three `OBSERVED_LED_ON`, zero accepted LED-off frames, and zero T2 frames. Every raw byte size and SHA-256 matches its adjacent metadata. Physical camera compatibility and any algorithmic use remain `REQUIRES_HIL`; Phase 03 remains `NEEDS_WORK`.

Next prerequisite: fresh explicit operator authorization followed by successful `xyz` homing and a complete re-preflight before any physical continuation.

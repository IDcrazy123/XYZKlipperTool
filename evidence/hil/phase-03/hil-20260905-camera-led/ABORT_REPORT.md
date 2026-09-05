# Phase 03 HIL evidence run — 2026-09-05

## Outcome

`WARNING` / stopped fail-closed at the safe boundary after T1 pickup and station alignment. The operator clarified that `T0_LED`–`T4_LED` are per-tool top-down nozzle LEDs, not the camera illumination source. No further tool change, motion, or capture was issued after that clarification. The ESP32-C3/WS2812B equipment was not controlled.

## Authorized and executed actions

Authorization covered `G28`, bounded provider-owned tool changes, bounded motion, and the run-scoped station X=170 mm, Y=20 mm, Z=40 mm. Executed commands were `GET_POSITION`, `STATUS`, `G28`, `G91`, `G1 Z30 F900`, `G90`, `G1 X170 Y20 F1800`, `G1 Z40 F600`, `T0`, runtime `SET_LED` commands, provider-owned `T1`, `G1 X170 Y20 F1800`, and `G1 Z40 F600`. The first T0 set produced 9 raw VoronBed snapshots: 3 LED-off, 3 requested LOW, and 3 requested MEDIUM. The LOW/MEDIUM sets are now classified `OBSERVED_TOOL_LED_TOP_DOWN`; all 9 T0 attempts are `WARNING/METADATA_INCOMPLETE` and excluded from any camera-light acceptance corpus. No T1–T4 frames were captured.

The camera endpoint was exactly `http://192.168.1.43/webcam/?action=snapshot`. VoronBed UID was `48efbfd8-83c8-488a-9fb8-b409905e808b`; the source-identity fingerprint is recorded in `run-manifest.json`. Raw files and per-frame metadata are under this directory; raw JPEG bytes were not modified after capture.

## Final observed state

At the final query, Klipper/Moonraker were ready and connected, `homed_axes=xyz`, toolchanger status was ready with declared and detected `tool T1` / number 1, gcode position was [170, 20, 40] mm, and toolhead position was [169.841, 19.805, 40.236] mm. Heater targets were all 0 °C. Every T0–T4 `color_data` channel was exactly [0, 0, 0, 0]. No `SAVE_CONFIG`, offset apply, probing, heating, restart, production-config edit, or deployment occurred.

## Evidence counts and hashes

- 9 raw sample JPEGs; 9 per-frame metadata files; 0 accepted camera-corpus frames.
- T0: 3 LED-off warnings, 3 requested LOW reclassified top-down-tool-LED warnings, 3 requested MEDIUM reclassified top-down-tool-LED warnings.
- T1/T2/T3/T4: 0 frames.
- Preflight snapshot: 238,425 bytes, SHA-256 `f5e50ff5fad44a266fd9931e40c6f202a6cbfe5bc3d6952216fc810e98da8898`.
- Raw sample bytes: 2,385,626 total. The complete run manifest is `run-manifest.json`.

This run does not establish camera illumination compatibility, detector reliability, or physical safety beyond the observed supervised actions. A future run requires fresh explicit authorization and must define the actual camera illumination source before capture.

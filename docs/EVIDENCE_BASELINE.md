# Evidence Baseline

This document indexes existing machine evidence that motivated XYZ Klipper Tool. It is comparison input, not product defaults. Phase 00 must import a sanitized immutable copy into this repository, create SHA-256 manifests, and preserve original status fields.

## X/Y camera evidence (`OBSERVED`)

Source:

- `D:\Desktop\All-Config-Voron-main\Voron 5 Tool\extras\experiments\ktamv-xy-independent-cycles-20260831.csv`
- SHA-256: `f27715158d7a238509a6a2b20bead4b727723cfb59ef213a2a90615689130a6f`
- Companion report SHA-256: `0cadc499af50ee21d6aa477447ced05d689622fcf4b882da16b30c60559b19e3`

Observed protocol and context:

- Three independent pickup cycles, each running T0, T1, T2, T3, T4.
- The fixture did not contain a terminal T0 return measurement within each cycle; that stronger drift check is `PLANNED` and `REQUIRES_HIL`.
- Observed camera scale: `0.0570 mm/pixel`; calibration RSD: `6.3%`.
- Observed camera origin: `[168.716, 18.451]` and observed safe Z: `40 mm`; both are historical machine data and forbidden as defaults.
- Camera illumination was the camera's normal user-supplied illumination. The external ESP32-C3/WS2812B ring was a temporary workaround and is out of scope.
- No measured X/Y candidate was automatically applied.

Raw candidate X/Y values in millimetres, relative to the reference tool:

| Cycle | T0 | T1 | T2 | T3 | T4 |
|---|---|---|---|---|---|
| 1 | `(0.000, 0.000)` | `(+0.004, -0.078)` | `(+0.006, -0.130)` | `(+0.029, -0.073)` | `(+0.004, -0.078)` |
| 2 | `(+0.001, -0.026)` | `(+0.004, -0.078)` | `(+0.004, -0.078)` | `(+0.005, -0.104)` | `(+0.004, -0.078)` |
| 3 | `(+0.001, -0.026)` | `(+0.004, -0.078)` | `(+0.005, -0.104)` | `(+0.004, -0.078)` | `(+0.003, -0.052)` |

The T3 X values demonstrate why mean alone is insufficient: mean `+0.012667 mm`, median `+0.005 mm`. The new system must retain all raw observations and report robust statistics without silently removing the high value.

## Z evidence (`OBSERVED`)

Source directory:

`D:\Desktop\All-Config-Voron-main\Voron 5 Tool\extras\backups\pre-toolvision-ux-hil-20260826-161315\Generated-Data-ToolVision\tool-vision-history`

The recorded history directory contains 20 historical Z run files: 4 physical-switch runs and 16 Cartographer Touch runs. A related `INVALID` switch run is stored in the separate pre-resume backup listed below, so the complete imported set is 21 files: 5 physical-switch runs and 16 Cartographer Touch runs. Preserve failures; do not cherry-pick successful-looking values.

Representative report-only observations:

- Switch run `20260825-094715-333-z-switch-01.json`, SHA-256 `e398dd88599aa05bc6143e2b37b8f199b3dab16ae2860974a0ef0c159df9243a`: T0 `0`, T1 `+0.114`, T2 `-0.384`, T3 `-0.186`, T4 `+0.090 mm`; reference return drift `+0.034 mm`; status `WARNING` because the limit was not configured; `applied=false`.
- Cartographer run `20260825-133944-202-z-cartographer_touch-01.json`, SHA-256 `570ff8de65a327f656e4656c24cf742db80d03e7d166930ed706eb1a49d3200c`: T0 `0`, T1 `+0.260`, T2 `-0.254`, T3 `-0.184`, T4 `+0.100 mm`; reference return drift `+0.020 mm`; status `WARNING`; `applied=false`.
- Failed switch run `20260826-114524-081-z-switch-01.json` records `TMC 'stepper_x' ... ShortToSupply_A`, empty offsets, cleanup failures, and `INVALID`. It proves fault and recovery evidence must be first-class and must never be averaged into candidates.

Historical production values and earlier switch measurements differ because of switch force, measurement location, temperature, and print validation. Therefore v1 must keep provider-specific baselines and must not combine switch and Cartographer samples into one estimator.

## Required evidence protocol for XYZ Klipper Tool

1. Preserve outer independent pickup cycles separately from inner camera frames.
2. The default X/Y validation protocol is three outer cycles; each cycle reacquires every tool. The target enhanced sequence is reference → all selected tools → reference return.
3. Discover tools dynamically; T0–T4 are only the observed fixture.
4. Obtain the current safe pose and provider station through commands/configuration at run time. No fixed camera, dock, probe, switch, or safe-Z coordinate.
5. Record raw values, timestamps, tool state, station revision, configuration fingerprint, software versions, temperatures, image/calibration identity, failure and cleanup events.
6. Report mean, median, sample SD only when at least two valid points exist, MAD, range, reference drift, uncertainty, and explicit verdict reason codes.
7. Keep switch and Cartographer measurements separate. Document their sign conventions and compare each against the same configured reference semantics only after tests prove the mapping.
8. Measurements remain report-only until a separate reviewed apply transaction passes freshness and safety checks.

## Status limits

- Existing observations validate requirements and fixtures; they do not validate the new implementation.
- Camera X/Y and both Z providers remain `PLANNED` in XYZ Klipper Tool.
- Any claim of real-machine compatibility remains `REQUIRES_HIL` until a supervised canary is completed.

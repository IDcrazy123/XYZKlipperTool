# kTAMV independent pickup-cycle experiment — 2026-08-31

## Scope

Three independent XY measurement cycles were run on the installed Voron toolchanger. Each cycle was one complete `T0 -> T1 -> T2 -> T3 -> T4` sequence, with exactly one camera sample after each tool pickup. T0 was measured as a reference and was not modified. The first cycle was preceded by `T1 -> T0` so that its T0 reading also followed a real pickup. No `SAVE_CONFIG`, offset apply macro, or ToolVision deployment was performed during this experiment.

The camera's built-in/default nozzle illumination was used. The separate ESP32-C3 + WCMCU WS2812B 8-ring (temporary 5% workaround) was not controlled, assumed, or part of the measurement path. The active tool LEDs were explicitly turned off before every sample.

## Preconditions and method

- Klipper state: `ready`; axes homed with `G28`; active/detected tool matched for every sample.
- Heater targets: bed and all extruders `0`.
- kTAMV camera calibration: `mm_per_pixel=0.0570`, final calibration standard deviation `6.3%`.
- Camera origin: `[168.716, 18.451]` machine coordinates, set by `KTAMV_SET_ORIGIN` after centering T0.
- Measurement height command: `Z=40` (operator-approved safe Z for this run). The native routine first raises at the *current* XY pose and then travels to the calibrated camera origin; camera XY was not hard-coded as a transit pose.
- Immediately before every tool measurement, `GET_POSITION` was sent and the returned pose was recorded as the dynamic safe pose. The native command then ran `KTAMV_MEASURE_ACTIVE_TOOL_XY SAMPLES=1 Z=40 MAX_SPREAD=0.12`.
- Residual convention: the reported `(X,Y)` is nozzle-center residual relative to the T0 camera origin, in millimetres. A positive residual is the value that the existing guarded apply macro would add to the currently loaded XY offset; this experiment intentionally did not apply it.

Raw rows are in [ktamv-xy-independent-cycles-20260831.csv](ktamv-xy-independent-cycles-20260831.csv).

## Raw results

| Cycle | Tool | Dynamic safe pose from `GET_POSITION` (mm) | Residual X (mm) | Residual Y (mm) |
|---:|:---:|:---|---:|---:|
| 1 | T0 | (30.200, 120.000, 40.000) | 0.000 | 0.000 |
| 1 | T1 | (104.000, 120.000, 40.2464) | +0.004 | −0.078 |
| 1 | T2 | (176.000, 120.000, 39.7312) | +0.006 | −0.130 |
| 1 | T3 | (249.500, 120.000, 39.8104) | +0.029 | −0.073 |
| 1 | T4 | (321.500, 120.000, 40.1028) | +0.004 | −0.078 |
| 2 | T0 | (30.200, 120.000, 40.000) | +0.001 | −0.026 |
| 2 | T1 | (104.000, 120.000, 40.2464) | +0.004 | −0.078 |
| 2 | T2 | (176.000, 120.000, 39.7312) | +0.004 | −0.078 |
| 2 | T3 | (249.500, 120.000, 39.8104) | +0.005 | −0.104 |
| 2 | T4 | (321.500, 120.000, 40.1028) | +0.004 | −0.078 |
| 3 | T0 | (30.200, 120.000, 40.000) | +0.001 | −0.026 |
| 3 | T1 | (104.000, 120.000, 40.2464) | +0.004 | −0.078 |
| 3 | T2 | (176.000, 120.000, 39.7312) | +0.005 | −0.104 |
| 3 | T3 | (249.500, 120.000, 39.8104) | +0.004 | −0.078 |
| 3 | T4 | (321.500, 120.000, 40.1028) | +0.003 | −0.052 |

## Between-pickup statistics

Population standard deviation is not used for the apply gate; sample standard deviation and min/max range are shown for review. `median` is the robust outer-cycle estimator proposed for ToolVision; `mean` is shown because the existing kTAMV apply macro adds a mean residual.

| Tool | Mean X,Y (mm) | Median X,Y (mm) | Sample SD X,Y (mm) | Range X,Y (mm) |
|:---:|:---|:---|:---|:---|
| T0 reference | (+0.000667, −0.017333) | (+0.001, −0.026) | (0.000577, 0.015011) | (0.001, 0.026) |
| T1 | (+0.004000, −0.078000) | (+0.004, −0.078) | (0, 0) | (0, 0) |
| T2 | (+0.005000, −0.104000) | (+0.005, −0.104) | (0.001, 0.026) | (0.002, 0.052) |
| T3 | (+0.012667, −0.085000) | (+0.005, −0.078) | (0.014154, 0.016643) | (0.025, 0.031) |
| T4 | (+0.003667, −0.069333) | (+0.004, −0.078) | (0.000577, 0.015011) | (0.001, 0.026) |

T3 has a single high-X first-cycle observation; therefore a production implementation should retain all raw rows, report both estimators, and require an explicit review when mean and median differ materially. The largest between-pickup range is T3 X=0.025 mm, still below the current 0.12 mm spread gate, but the gate alone must not hide an outlier.

## Candidate offset effect (not applied)

Current loaded XY values before this run were T1 `(-0.159,-0.195)`, T2 `(+0.820,+0.240)`, T3 `(+0.326,+0.524)`, T4 `(+0.168,+0.268)` mm. If the guarded macro were run with the *mean* residuals, the staged values would be approximately:

| Tool | Candidate loaded + mean (mm) | Candidate loaded + median (mm) |
|:---:|:---|:---|
| T1 | (−0.155, −0.273) | (−0.155, −0.273) |
| T2 | (+0.825, +0.136) | (+0.825, +0.136) |
| T3 | (+0.3387, +0.4390) | (+0.331, +0.446) |
| T4 | (+0.1717, +0.1987) | (+0.172, +0.190) |

These are review-only candidates. Do not write them to `printer.cfg` without a separate supervised approval, fresh backup, and a post-apply validation cycle.

## Interpretation for the ToolVision rewrite

The former one-pickup/three-consecutive-sample approach produced zero within-pickup spread and therefore overstated repeatability. Independent cycles expose dock/pickup variation (especially T2/T3/T4). ToolVision should therefore model two levels: inner camera-detection repeatability and outer pickup-cycle repeatability; use an outer robust estimator, a T0 return-drift gate, and a human-reviewed apply transaction. Every cycle must obtain the current safe pose through a command/API such as `GET_POSITION` (or a dedicated `TOOLVISION_GET_SAFE_POSITION`) and must never embed fixed camera, dock, probe, or switch coordinates.

For Z, keep a provider abstraction with `cartographer` and physical-switch implementations. The probe/switch position must likewise come from the machine command/configuration at run time; it must not be copied from the XY camera path. XY camera illumination is the camera's supplied default light. The ESP32-C3/WS2812B ring is external, temporary, and out of scope.

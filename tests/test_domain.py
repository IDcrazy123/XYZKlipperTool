import math
import unittest
from typing import cast

from xyz_klipper_tool.domain.models import (
    ApplyPlan,
    Axis,
    FreshnessResult,
    ProviderKind,
    ReasonCode,
    RollbackEntry,
    RollbackPlan,
    RunId,
    Verdict,
)
from xyz_klipper_tool.domain.state_machine import RunState, RunStateMachine
from xyz_klipper_tool.domain.statistics import (
    Observation,
    OutlierPolicy,
    ReferencePair,
    SampleStatus,
    SampleSufficiency,
    summarize,
)
from xyz_klipper_tool.domain.units import (
    Celsius,
    CoordinateFrame,
    Millimetres,
    PixelScale,
    PixelVector2,
    Seconds,
    SignConvention,
    Vector2Mm,
    convert_sign,
)


def obs(
    value: float,
    sample: str,
    provider: ProviderKind = ProviderKind.SWITCH,
    axis: Axis = Axis.Z,
    status: SampleStatus = SampleStatus.VALID,
) -> Observation:
    return Observation(
        "run",
        "cycle",
        "visit",
        sample,
        "station-1",
        "fingerprint-1",
        "calibration-1",
        provider,
        axis,
        Millimetres(value),
        status,
    )


class DomainTests(unittest.TestCase):
    def test_units_sign_frame_and_bidirectional_conversion_table(self) -> None:
        for frame, sign in (
            (CoordinateFrame.CAMERA_IMAGE, SignConvention.REFERENCE_MINUS_MEASURED),
        ):
            value = PixelVector2(12.5, -3, frame, sign)
            restored = PixelScale(0.2, 0.4).to_pixels(PixelScale(0.2, 0.4).to_mm(value))
            self.assertAlmostEqual(restored.x_px, value.x_px)
            self.assertEqual(restored.sign, sign)
        self.assertEqual(
            convert_sign(
                Millimetres(2),
                SignConvention.REFERENCE_MINUS_MEASURED,
                SignConvention.CORRECTION_TO_APPLY,
            ).value_mm,
            -2,
        )
        with self.assertRaises(ValueError):
            PixelScale(0.2, 0.4).to_mm(
                PixelVector2(
                    1, 2, CoordinateFrame.TOOL, SignConvention.REFERENCE_MINUS_MEASURED
                )
            )
        with self.assertRaises(ValueError):
            convert_sign(
                Millimetres(2),
                SignConvention.PROVIDER_REPORTED,
                SignConvention.CORRECTION_TO_APPLY,
            )

    def test_units_reject_nan_inf_and_empty_ids(self) -> None:
        for constructor in (Millimetres, Seconds, Celsius):
            for value in (math.nan, math.inf, -math.inf):
                with self.assertRaises(ValueError):
                    constructor(value)
        with self.assertRaises(ValueError):
            obs(1, "")
        with self.assertRaises(ValueError):
            obs(1, "x", provider=cast(ProviderKind, "arbitrary-provider"))
        with self.assertRaises(ValueError):
            obs(1, "x", axis=cast(Axis, "Q"))

    def test_statistics_empty_singleton_invalid_warning_and_drift(self) -> None:
        empty = summarize([])
        one = summarize([obs(2, "a")])
        self.assertEqual(
            empty.filtered.sufficiency, SampleSufficiency.INSUFFICIENT_SAMPLES
        )
        self.assertIsNone(one.filtered.sample_sd_mm)
        result = summarize(
            [
                obs(1, "a"),
                obs(100, "bad", status=SampleStatus.INVALID),
                obs(3, "b", status=SampleStatus.WARNING),
            ],
            reference=ReferencePair(Millimetres(10), Millimetres(12)),
        )
        self.assertEqual(result.filtered.values_mm, (1.0, 3.0))
        self.assertEqual(result.invalid_count, 1)
        self.assertEqual(
            (result.verdict, result.reason_code),
            (Verdict.INVALID, ReasonCode.INVALID_SAMPLE),
        )
        self.assertEqual(result.reference_drift_mm, Millimetres(2))
        self.assertIsNotNone(result.filtered.uncertainty_mm)

    def test_outlier_rejection_is_reasoned_and_raw_is_immutable(self) -> None:
        with self.assertRaises(ValueError):
            OutlierPolicy("invalid", -1, True)
        result = summarize(
            [obs(1, "a"), obs(1.1, "b"), obs(9, "c")],
            OutlierPolicy("threshold", 0.2, True),
        )
        self.assertEqual(result.rejected_count, 1)
        self.assertEqual(result.rejections[0].reason_code, ReasonCode.OUTLIER_REJECTED)
        self.assertEqual(result.unfiltered.values_mm, (1, 1.1, 9))
        self.assertEqual(result.filtered.values_mm, (1, 1.1))

    def test_series_cannot_mix_provider_or_axis_and_limits_fail_closed(self) -> None:
        with self.assertRaises(ValueError):
            summarize(
                [obs(1, "a"), obs(2, "b", provider=ProviderKind.CARTOGRAPHER_TOUCH)]
            )
        result = summarize([obs(9, "a"), obs(10, "b")], limit_mm=5)
        self.assertEqual(
            (result.verdict, result.reason_code),
            (Verdict.INVALID, ReasonCode.LIMIT_EXCEEDED),
        )

    def test_state_machine_success_terminal_and_fault(self) -> None:
        m = RunStateMachine()
        self.assertTrue(m.transition(RunState.VALIDATING).accepted)
        self.assertTrue(m.transition(RunState.RUNNING).accepted)
        self.assertTrue(m.transition(RunState.COMPLETED).accepted)
        fault = m.transition(RunState.RUNNING)
        self.assertFalse(fault.accepted)
        self.assertEqual(m.state, RunState.COMPLETED)

    def test_apply_freshness_and_rollback_are_data_only_and_fail_closed(self) -> None:
        plan = ApplyPlan(RunId("run"), "fingerprint")
        self.assertTrue(plan.preview_only)
        with self.assertRaises(ValueError):
            ApplyPlan(RunId("run"), "fingerprint", False)
        self.assertFalse(FreshnessResult(False, ReasonCode.STALE_FINGERPRINT).fresh)
        rollback = RollbackPlan(
            (
                RollbackEntry(
                    "tool",
                    Vector2Mm(
                        1, 2, CoordinateFrame.MACHINE, SignConvention.PROVIDER_REPORTED
                    ),
                ),
            ),
            RunId("run"),
        )
        self.assertEqual(rollback.source_run_id.value, "run")


if __name__ == "__main__":
    unittest.main()

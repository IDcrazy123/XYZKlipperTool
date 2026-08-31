import unittest

from xyz_klipper_tool.domain.models import (
    ClaimState,
    ReasonCode,
    RunId,
    SwitchMeasurementResult,
    ToolVisitId,
    Verdict,
)
from xyz_klipper_tool.domain.state_machine import RunState, RunStateMachine
from xyz_klipper_tool.domain.statistics import (
    Observation,
    OutlierPolicy,
    SampleStatus,
    summarize,
)
from xyz_klipper_tool.domain.units import PixelScale, PixelVector2, Vector2Mm


class DomainTests(unittest.TestCase):
    def test_conversion_is_reversible(self):
        scale = PixelScale(0.2, 0.4)
        pixels = PixelVector2(12.5, -3.0)
        restored = scale.to_pixels(scale.to_mm(pixels))
        self.assertAlmostEqual(restored.x_px, pixels.x_px)
        self.assertAlmostEqual(restored.y_px, pixels.y_px)

    def test_statistics_empty_and_singleton_are_typed(self):
        empty = summarize([])
        one = summarize([Observation("s1", 2.0)])
        self.assertTrue(empty.insufficient_samples)
        self.assertIsNone(empty.sample_sd_mm)
        self.assertEqual(one.mean_mm, 2.0)
        self.assertIsNone(one.sample_sd_mm)

    def test_invalid_never_enters_estimator_and_warning_is_counted(self):
        result = summarize(
            [
                Observation("a", 1.0),
                Observation("b", 100.0, SampleStatus.INVALID),
                Observation("c", 3.0, SampleStatus.WARNING),
            ]
        )
        self.assertEqual(result.filtered_values_mm, (1.0, 3.0))
        self.assertEqual((result.invalid_count, result.warning_count), (1, 1))

    def test_outlier_policy_keeps_raw_and_filters_explicitly(self):
        result = summarize(
            [Observation("a", 1.0), Observation("b", 1.1), Observation("c", 9.0)],
            OutlierPolicy("median_threshold", 0.2, True),
        )
        self.assertEqual(result.total_count, 3)
        self.assertEqual(result.filtered_values_mm, (1.0, 1.1))
        self.assertEqual(len(result.raw_observations), 3)

    def test_metamorphic_translation_preserves_sd_mad_range(self):
        values = [Observation(str(i), float(i)) for i in range(1, 5)]
        shifted = [Observation(str(i), float(i) + 10) for i in range(1, 5)]
        a, b = summarize(values), summarize(shifted)
        self.assertAlmostEqual(a.sample_sd_mm, b.sample_sd_mm)
        self.assertAlmostEqual(a.mad_mm, b.mad_mm)
        self.assertAlmostEqual(a.range_mm, b.range_mm)

    def test_state_machine_rejects_illegal_transition_fail_closed(self):
        machine = RunStateMachine()
        result = machine.transition(RunState.RUNNING)
        self.assertFalse(result.accepted)
        self.assertEqual(machine.state, RunState.CREATED)
        self.assertEqual(result.reason_code.value, "INVALID_TRANSITION")

    def test_provider_result_is_explicit_and_hil(self):
        result = SwitchMeasurementResult(
            RunId("r"),
            ToolVisitId("v"),
            Vector2Mm(1, 2),
            Verdict.WARNING,
            ReasonCode.PROVIDER_CONTRACT_UNVERIFIED,
        )
        self.assertEqual(result.claim_state, ClaimState.REQUIRES_HIL)


if __name__ == "__main__":
    unittest.main()

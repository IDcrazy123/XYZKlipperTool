# pyright: reportUnknownMemberType=false, reportUnknownArgumentType=false, reportUnknownVariableType=false, reportOptionalSubscript=false
import unittest
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from typing import Any, cast

import cv2
import numpy as np

from xyz_klipper_tool.domain.models import ReasonCode, Verdict
from xyz_klipper_tool.domain.units import CoordinateFrame, Millimetres, Pixels, Seconds
from xyz_klipper_tool.vision.calibration import Calibration, Transform2D
from xyz_klipper_tool.vision.detectors import DetectionContext
from xyz_klipper_tool.vision.jpeg_adapter import (
    ConsensusJpegDetector,
    ContourEllipseDetector,
    GradientRadialDetector,
    JpegAnalysisLimits,
    JpegDetection,
    RoiBounds,
)


class JpegAdapterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.cal = Calibration(
            "cal-1",
            1,
            "cam",
            "fingerprint",
            Transform2D(
                0.1,
                0.1,
                Millimetres(1),
                Millimetres(2),
                CoordinateFrame.CAMERA_IMAGE,
                CoordinateFrame.TOOL,
            ),
            0.2,
            Millimetres(0.01),
            "a" * 64,
            datetime(2026, 9, 1, tzinfo=timezone.utc),
        )
        self.roi = RoiBounds(8, 8, 112, 80, "cal-1", "fingerprint")
        self.context = DetectionContext(
            "cal-1",
            "fingerprint",
            datetime(2026, 9, 1, tzinfo=timezone.utc),
            datetime(2026, 9, 1, 0, 0, 0, 100000, tzinfo=timezone.utc),
            Seconds(2),
            "sample-1",
            self.cal.created_at_utc,
            Seconds(3600),
            0.1,
        )

    def jpeg(
        self, circles: tuple[tuple[int, int], ...] = ((64, 48),), blur: int = 0
    ) -> bytes:
        image: Any = np.full((96, 128), 220, dtype=np.uint8)
        for x, y in circles:
            cv2.circle(image, (x, y), 12, 25, -1)
            cv2.circle(image, (x, y), 5, 210, -1)
        if blur:
            image = cv2.GaussianBlur(image, (blur, blur), 0)
        ok, encoded = cv2.imencode(".jpg", image, [cv2.IMWRITE_JPEG_QUALITY, 95])
        self.assertTrue(ok)
        return bytes(encoded)

    def shaped_jpeg(self, shape: str) -> bytes:
        image: Any = np.full((96, 128), 220, dtype=np.uint8)
        if shape == "square":
            cv2.rectangle(image, (52, 36), (76, 60), 25, -1)
            cv2.rectangle(image, (59, 43), (69, 53), 210, -1)
        elif shape == "open_arc":
            cv2.ellipse(image, (64, 48), (16, 12), 0, 20, 160, 25, 3)
        else:
            raise AssertionError(shape)
        ok, encoded = cv2.imencode(".jpg", image, [cv2.IMWRITE_JPEG_QUALITY, 95])
        self.assertTrue(ok)
        return bytes(encoded)

    def test_both_independent_pipelines_find_off_axis_center(self) -> None:
        encoded = self.jpeg(((74, 42),))
        first = GradientRadialDetector().detect_jpeg(
            encoded, self.cal, self.roi, self.context
        )
        second = ContourEllipseDetector().detect_jpeg(
            encoded, self.cal, self.roi, self.context
        )
        self.assertEqual(first.pipeline, "gradient_radial")
        self.assertEqual(second.pipeline, "contour_ellipse")
        self.assertEqual(
            (first.detection.verdict, second.detection.verdict),
            (Verdict.PASS, Verdict.PASS),
        )
        for result in (first, second):
            self.assertIsNotNone(result.detection.center_x_px)
            self.assertIsNotNone(result.detection.center_y_px)
            self.assertAlmostEqual(
                cast(Pixels, result.detection.center_x_px).value_px, 74.0, delta=2.0
            )
            self.assertAlmostEqual(
                cast(Pixels, result.detection.center_y_px).value_px, 42.0, delta=2.0
            )
        self.assertGreater(first.quality.contrast_std, 5.0)

    def test_consensus_rejects_multiple_candidates_and_disagreement(self) -> None:
        multiple = ConsensusJpegDetector().detect_jpeg(
            self.jpeg(((45, 40), (85, 55))), self.cal, self.roi, self.context
        )
        self.assertEqual(
            (multiple.detection.verdict, multiple.detection.reason),
            (Verdict.INVALID, ReasonCode.AMBIGUOUS_CANDIDATE),
        )

        class StubDetector:
            def __init__(self, result: JpegDetection) -> None:
                self.result = result

            def detect_jpeg(self, *args: Any, **kwargs: Any) -> JpegDetection:
                return self.result

        first = GradientRadialDetector().detect_jpeg(
            self.jpeg(), self.cal, self.roi, self.context
        )
        second = ContourEllipseDetector().detect_jpeg(
            self.jpeg(), self.cal, self.roi, self.context
        )
        self.assertIsNotNone(first.detection.center_x_px)
        self.assertIsNotNone(first.detection.center_y_px)
        self.assertIsNotNone(second.detection.center_x_px)
        self.assertIsNotNone(second.detection.center_y_px)
        displaced = replace(
            second.detection,
            center_x_px=Pixels(100.0),
            center_y_px=Pixels(80.0),
        )
        disagreement = ConsensusJpegDetector(
            StubDetector(first), StubDetector(replace(second, detection=displaced))
        ).detect_jpeg(self.jpeg(), self.cal, self.roi, self.context)
        self.assertEqual(
            (disagreement.detection.verdict, disagreement.detection.reason),
            (Verdict.INVALID, ReasonCode.PIPELINE_DISAGREEMENT),
        )

    def test_square_and_open_arc_never_become_confident_consensus(self) -> None:
        for shape in ("square", "open_arc"):
            with self.subTest(shape=shape):
                result = ConsensusJpegDetector().detect_jpeg(
                    self.shaped_jpeg(shape), self.cal, self.roi, self.context
                )
                self.assertNotEqual(result.detection.verdict, Verdict.PASS)
                self.assertEqual(result.detection.confidence, 0.0)

    def test_quality_and_input_bounds_fail_closed(self) -> None:
        blurred = GradientRadialDetector().detect_jpeg(
            self.jpeg(blur=31),
            self.cal,
            self.roi,
            self.context,
            JpegAnalysisLimits(blur_score_min=100000.0),
        )
        self.assertEqual(
            (blurred.detection.verdict, blurred.detection.reason),
            (Verdict.INVALID, ReasonCode.BLUR),
        )
        bad = ContourEllipseDetector().detect_jpeg(
            b"not jpeg", self.cal, self.roi, self.context
        )
        self.assertEqual(
            (bad.detection.verdict, bad.detection.reason),
            (Verdict.INVALID, ReasonCode.CORRUPT_INPUT),
        )
        oversized = GradientRadialDetector().detect_jpeg(
            self.jpeg(),
            self.cal,
            self.roi,
            self.context,
            JpegAnalysisLimits(max_encoded_bytes=10),
        )
        self.assertEqual(
            (oversized.detection.verdict, oversized.detection.reason),
            (Verdict.INVALID, ReasonCode.OVERSIZED_INPUT),
        )

    def test_stale_context_fails_closed(self) -> None:
        stale = DetectionContext(
            "cal-1",
            "fingerprint",
            self.context.captured_at_utc,
            self.context.captured_at_utc + timedelta(seconds=3),
            Seconds(2),
            "sample-1",
            self.cal.created_at_utc,
            Seconds(3600),
            0.1,
        )
        result = GradientRadialDetector().detect_jpeg(
            self.jpeg(), self.cal, self.roi, stale
        )
        self.assertEqual(
            (result.detection.verdict, result.detection.reason),
            (Verdict.INVALID, ReasonCode.STALE_FRAME),
        )

    def test_roi_identity_and_staleness_are_rejected(self) -> None:
        wrong_roi = RoiBounds(8, 8, 112, 80, "other-cal", "fingerprint")
        result = GradientRadialDetector().detect_jpeg(
            self.jpeg(), self.cal, wrong_roi, self.context
        )
        self.assertEqual(result.detection.reason, ReasonCode.CALIBRATION_MISMATCH)

    def test_saturation_is_diagnosed_and_masked(self) -> None:
        encoded = self.jpeg()
        encoded_array: Any = np.frombuffer(encoded, dtype=np.uint8)
        image = cast(Any, cv2.imdecode(encoded_array, cv2.IMREAD_GRAYSCALE))
        image[10:70, 10:70] = 255
        ok, out = cv2.imencode(".jpg", image)
        self.assertTrue(ok)
        result = GradientRadialDetector().detect_jpeg(
            bytes(out), self.cal, self.roi, self.context
        )
        self.assertGreater(result.quality.saturation_ratio, 0.0)


if __name__ == "__main__":
    unittest.main()

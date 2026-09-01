import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from xyz_klipper_tool.domain.models import ReasonCode, Verdict
from xyz_klipper_tool.domain.units import Millimetres, Seconds
from xyz_klipper_tool.vision import (
    BlobDetector,
    Calibration,
    CameraFrame,
    CaptureLimits,
    CaptureRequest,
    CircleCandidateDetector,
    CorpusEntry,
    CorpusSplit,
    DetectionContext,
    JsonCalibrationStore,
    Transform2D,
    deterministic_split,
    validate_camera_url,
)


class Phase03Tests(unittest.TestCase):
    def calibration(self) -> Calibration:
        return Calibration(
            "cal-1",
            1,
            "cam",
            "fingerprint",
            Transform2D(0.1, 0.1, Millimetres(1), Millimetres(2)),
            0.2,
            Millimetres(0.01),
            "a" * 64,
            datetime(2026, 9, 1, tzinfo=timezone.utc),
        )

    def frame(self, data: bytes) -> CameraFrame:
        return CameraFrame(b"P5\n10 10\n255\n" + data, 10, 10, Seconds(0.1))

    def context(self, cal: Calibration, age: float = 0.1) -> DetectionContext:
        captured = datetime(2026, 9, 1, tzinfo=timezone.utc)
        return DetectionContext(
            cal.calibration_id,
            cal.camera_fingerprint,
            captured,
            captured + timedelta(seconds=age),
            Seconds(2),
            "sample-1",
            "1/60s",
        )

    def test_capture_bounds_and_local_allowlist(self) -> None:
        CaptureRequest("http://127.0.0.1/camera", Seconds(1))
        CaptureRequest("device:/dev/video0", Seconds(1))
        with self.assertRaises(ValueError):
            validate_camera_url("http://example.com/camera")
        with self.assertRaises(ValueError):
            validate_camera_url("http://user:pass@127.0.0.1/camera")
        with self.assertRaises(ValueError):
            validate_camera_url("device:../camera")
        with self.assertRaises(ValueError):
            validate_camera_url("device:%2e%2e/camera")
        with self.assertRaises(ValueError):
            validate_camera_url("http://127.0.0.1/%2e%2e/private")
        with self.assertRaises(ValueError):
            self.frame(b"x" * (8 * 1024 * 1024 + 1)).validate(CaptureLimits())

    def test_detector_candidates_and_diagnostics(self) -> None:
        cal = self.calibration()
        limits = CaptureLimits()
        pixels = bytearray(100)
        pixels[44:47] = b"\xff\xff\xff"
        ok = BlobDetector().detect(
            self.frame(bytes(pixels)), cal, limits, self.context(cal)
        )
        self.assertEqual(
            (ok.verdict, ok.reason, ok.calibration_id),
            (Verdict.PASS, ReasonCode.NONE, "cal-1"),
        )
        self.assertEqual(
            CircleCandidateDetector()
            .detect(self.frame(bytes(100)), cal, limits, self.context(cal))
            .reason,
            ReasonCode.ZERO_CANDIDATE,
        )
        self.assertEqual(
            BlobDetector()
            .detect(
                self.frame(bytes([255] + [0] * 98 + [255])),
                cal,
                limits,
                self.context(cal),
            )
            .reason,
            ReasonCode.AMBIGUOUS_CANDIDATE,
        )
        empty = CameraFrame(b"", 1, 1, Seconds(0.1))
        self.assertEqual(
            BlobDetector().detect(empty, cal, limits, self.context(cal)).reason,
            ReasonCode.MISSING_INPUT,
        )
        stale = CameraFrame(b"P5\n10 10\n255\n" + bytes(100), 10, 10, Seconds(3))
        self.assertEqual(
            CircleCandidateDetector()
            .detect(stale, cal, limits, self.context(cal))
            .reason,
            ReasonCode.STALE_FRAME,
        )

    def test_detection_identity_freshness_and_overlay(self) -> None:
        cal = self.calibration()
        limits = CaptureLimits()
        blank = self.frame(bytes(100))
        self.assertEqual(
            BlobDetector().detect(blank, cal, limits).reason,
            ReasonCode.CALIBRATION_MISMATCH,
        )
        bad = DetectionContext(
            "other",
            cal.camera_fingerprint,
            datetime(2026, 9, 1, tzinfo=timezone.utc),
            datetime(2026, 9, 1, tzinfo=timezone.utc),
            Seconds(2),
            "s",
        )
        self.assertEqual(
            BlobDetector().detect(blank, cal, limits, bad).reason,
            ReasonCode.CALIBRATION_MISMATCH,
        )
        old = DetectionContext(
            cal.calibration_id,
            cal.camera_fingerprint,
            datetime(2026, 8, 1, tzinfo=timezone.utc),
            datetime(2026, 9, 1, tzinfo=timezone.utc),
            Seconds(2),
            "s",
        )
        self.assertEqual(
            BlobDetector().detect(blank, cal, limits, old).reason,
            ReasonCode.STALE_FRAME,
        )
        first = BlobDetector().detect(blank, cal, limits, self.context(cal))
        second = BlobDetector().detect(blank, cal, limits, self.context(cal))
        self.assertEqual(first.overlay_artifact, second.overlay_artifact)
        self.assertEqual(first.overlay_sha256, second.overlay_sha256)
        self.assertLessEqual(first.overlay_size_bytes, 4096)

    def test_bounded_camera_retries_and_decode_timeout(self) -> None:
        class Transport:
            def __init__(self) -> None:
                self.calls = 0

            def capture(self, timeout_s: Seconds) -> bytes:
                self.calls += 1
                if self.calls == 1:
                    raise TimeoutError()
                return b"frame"

        class Clock:
            def __init__(self) -> None:
                self.times = iter(
                    (
                        datetime(2026, 9, 1, tzinfo=timezone.utc),
                        datetime(2026, 9, 1, tzinfo=timezone.utc),
                        datetime(2026, 9, 1, 0, 0, 3, tzinfo=timezone.utc),
                    )
                )

            def now_utc(self) -> datetime:
                return next(self.times)

        from xyz_klipper_tool.vision.capture import BoundedCameraProvider

        provider = BoundedCameraProvider(
            Transport(),
            Clock(),
            CaptureLimits(max_retries=1, max_decode_time_s=Seconds(2)),
        )
        result = provider.capture(CaptureRequest("device:/dev/video0", Seconds(1)))
        self.assertEqual(
            (result.reason, result.attempts), (ReasonCode.DECODE_TIMEOUT, 2)
        )

    def test_calibration_round_trip_and_corruption(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = JsonCalibrationStore(Path(directory))
            cal = self.calibration()
            store.put(cal)
            self.assertEqual(store.get("cal-1"), cal)
            path = Path(directory) / "cal-1.json"
            data = json.loads(path.read_text())
            data["checksum"] = "0" * 64
            path.write_text(json.dumps(data))
            with self.assertRaises(ValueError):
                store.get("cal-1")
            with self.assertRaises(ValueError):
                store.put(
                    self.calibration().__class__(
                        "../escaped",
                        1,
                        "cam",
                        "fp",
                        self.calibration().transform,
                        0.2,
                        Millimetres(0.01),
                        "a" * 64,
                        datetime(2026, 9, 1, tzinfo=timezone.utc),
                    )
                )

    def test_corpus_split_has_no_session_leakage(self) -> None:
        entries = [
            CorpusEntry(f"e{i}", Path(f"f{i}.png"), f"s{i // 2}", "nozzle", "a" * 64)
            for i in range(8)
        ]
        split = deterministic_split(entries)
        owners = {
            entry.session_id: key for key, values in split.items() for entry in values
        }
        self.assertEqual(len(owners), 4)
        self.assertTrue(set(split))
        self.assertFalse(
            {e.session_id for e in split[CorpusSplit.HOLDOUT]}
            & {e.session_id for e in split[CorpusSplit.CALIBRATION]}
        )


if __name__ == "__main__":
    unittest.main()

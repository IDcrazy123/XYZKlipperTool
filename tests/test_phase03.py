import json
import tempfile
import unittest
from datetime import datetime, timezone
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
            self.frame(b"x" * (8 * 1024 * 1024 + 1)).validate(CaptureLimits())

    def test_detector_candidates_and_diagnostics(self) -> None:
        cal = self.calibration()
        limits = CaptureLimits()
        pixels = bytearray(100)
        pixels[44:47] = b"\xff\xff\xff"
        ok = BlobDetector().detect(self.frame(bytes(pixels)), cal, limits)
        self.assertEqual(
            (ok.verdict, ok.reason, ok.calibration_id),
            (Verdict.PASS, ReasonCode.NONE, "cal-1"),
        )
        self.assertEqual(
            CircleCandidateDetector()
            .detect(self.frame(bytes(100)), cal, limits)
            .reason,
            ReasonCode.ZERO_CANDIDATE,
        )
        self.assertEqual(
            BlobDetector()
            .detect(self.frame(bytes([255] + [0] * 98 + [255])), cal, limits)
            .reason,
            ReasonCode.AMBIGUOUS_CANDIDATE,
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

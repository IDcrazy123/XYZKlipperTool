import importlib
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, cast

from xyz_klipper_tool.domain.models import ReasonCode, Verdict
from xyz_klipper_tool.domain.units import CoordinateFrame, Millimetres, Seconds
from xyz_klipper_tool.vision import (
    BlobDetector,
    Calibration,
    CameraFrame,
    CaptureLimits,
    CaptureRequest,
    CaptureResult,
    CircleCandidateDetector,
    CorpusEntry,
    CorpusSplit,
    Detection,
    DetectionContext,
    JsonCalibrationStore,
    Transform2D,
    benchmark_detectors,
    build_inventory,
    deterministic_split,
    evaluate_benchmark,
    inventory_json,
    validate_camera_url,
    verify_inventory,
)
from xyz_klipper_tool.vision.calibration import calibration_payload

_jsonschema: Any = None
try:
    _jsonschema = importlib.import_module("jsonschema")
except ModuleNotFoundError:
    pass


class Phase03Tests(unittest.TestCase):
    def calibration(self) -> Calibration:
        return Calibration(
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

    def frame(self, data: bytes, cal: Calibration | None = None) -> CameraFrame:
        return CameraFrame(
            b"P5\n10 10\n255\n" + data,
            10,
            10,
            Seconds(0.1),
            "sample-1",
            cal.camera_fingerprint if cal is not None else "camera",
            datetime(2026, 9, 1, tzinfo=timezone.utc),
        )

    def context(self, cal: Calibration, age: float = 0.1) -> DetectionContext:
        captured = datetime(2026, 9, 1, tzinfo=timezone.utc)
        return DetectionContext(
            cal.calibration_id,
            cal.camera_fingerprint,
            captured,
            captured + timedelta(seconds=age),
            Seconds(2),
            "sample-1",
            captured,
            Seconds(3600),
            0.1,
            "1/60s",
        )

    def test_capture_bounds_and_local_allowlist(self) -> None:
        CaptureRequest("http://127.0.0.1/camera", Seconds(1), "sample", "camera")
        CaptureRequest("device:/dev/video0", Seconds(1), "sample", "camera")
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
            self.frame(bytes(pixels), cal), cal, limits, self.context(cal)
        )
        self.assertEqual(
            (ok.verdict, ok.reason, ok.calibration_id),
            (Verdict.PASS, ReasonCode.NONE, "cal-1"),
        )
        self.assertEqual(
            CircleCandidateDetector()
            .detect(self.frame(bytes(100), cal), cal, limits, self.context(cal))
            .reason,
            ReasonCode.ZERO_CANDIDATE,
        )
        self.assertEqual(
            BlobDetector()
            .detect(
                self.frame(bytes([255] + [0] * 98 + [255]), cal),
                cal,
                limits,
                self.context(cal),
            )
            .reason,
            ReasonCode.AMBIGUOUS_CANDIDATE,
        )
        empty = CameraFrame(
            b"",
            1,
            1,
            Seconds(0.1),
            "sample-1",
            cal.camera_fingerprint,
            datetime(2026, 9, 1, tzinfo=timezone.utc),
        )
        self.assertEqual(
            BlobDetector().detect(empty, cal, limits, self.context(cal)).reason,
            ReasonCode.MISSING_INPUT,
        )
        stale = CameraFrame(
            b"P5\n10 10\n255\n" + bytes(100),
            10,
            10,
            Seconds(3),
            "sample-1",
            cal.camera_fingerprint,
            datetime(2026, 9, 1, tzinfo=timezone.utc),
        )
        self.assertEqual(
            CircleCandidateDetector()
            .detect(stale, cal, limits, self.context(cal))
            .reason,
            ReasonCode.STALE_FRAME,
        )

    def test_detection_identity_freshness_and_overlay(self) -> None:
        cal = self.calibration()
        limits = CaptureLimits()
        blank = self.frame(bytes(100), cal)
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
            datetime(2026, 9, 1, tzinfo=timezone.utc),
            Seconds(3600),
            0.1,
        )
        self.assertEqual(
            BlobDetector().detect(blank, cal, limits, bad).reason,
            ReasonCode.CALIBRATION_MISMATCH,
        )
        spoofed = DetectionContext(
            cal.calibration_id,
            cal.camera_fingerprint,
            datetime(2026, 9, 1, tzinfo=timezone.utc),
            datetime(2026, 9, 1, tzinfo=timezone.utc),
            Seconds(2),
            "sample-1",
            datetime(2026, 8, 31, tzinfo=timezone.utc),
            Seconds(3600),
            0.1,
        )
        self.assertEqual(
            BlobDetector().detect(blank, cal, limits, spoofed).reason,
            ReasonCode.CALIBRATION_MISMATCH,
        )
        old = DetectionContext(
            cal.calibration_id,
            cal.camera_fingerprint,
            datetime(2026, 8, 1, tzinfo=timezone.utc),
            datetime(2026, 9, 1, tzinfo=timezone.utc),
            Seconds(2),
            "s",
            datetime(2026, 8, 1, tzinfo=timezone.utc),
            Seconds(2),
            0.1,
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

            def capture(self, target: str, timeout_s: Seconds) -> bytes:
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
        result = provider.capture(
            CaptureRequest("device:/dev/video0", Seconds(1), "sample", "camera")
        )
        self.assertEqual(
            (result.reason, result.attempts), (ReasonCode.CAPTURE_TIMEOUT, 2)
        )

    def test_detection_invariants_and_injected_decode_timeout(self) -> None:
        cal = self.calibration()
        with self.assertRaises(ValueError):
            Detection(
                "c",
                "s",
                "f",
                None,
                None,
                float("nan"),
                0,
                ReasonCode.NONE,
                Verdict.INVALID,
                0.0,
                0.1,
            )
        with self.assertRaises(ValueError):
            Detection(
                "c",
                "s",
                "f",
                None,
                None,
                0.0,
                -1,
                ReasonCode.INVALID_SAMPLE,
                Verdict.INVALID,
                0.0,
                0.1,
            )
        with self.assertRaises(ValueError):
            Detection(
                "c",
                "s",
                "f",
                None,
                None,
                0.0,
                0,
                ReasonCode.INVALID_SAMPLE,
                Verdict.INVALID,
                0.0,
                0.1,
                exposure_metadata="x" * 1025,
            )
        with self.assertRaises(ValueError):
            Detection(
                "c",
                "s",
                "f",
                None,
                None,
                0.0,
                0,
                ReasonCode.INVALID_SAMPLE,
                Verdict.INVALID,
                0.0,
                0.1,
                overlay_artifact=b"x" * 4097,
            )

        class SlowDecoder:
            def decode(
                self, frame: CameraFrame, limits: CaptureLimits
            ) -> tuple[int, int, bytes]:
                return 10, 10, bytes(100)

        class DecodeClock:
            def __init__(self) -> None:
                self.times = iter(
                    (
                        datetime(2026, 9, 1, tzinfo=timezone.utc),
                        datetime(2026, 9, 1, 0, 0, 3, tzinfo=timezone.utc),
                    )
                )

            def now_utc(self) -> datetime:
                return next(self.times)

        result = BlobDetector(DecodeClock(), SlowDecoder()).detect(
            self.frame(bytes(100), cal),
            cal,
            CaptureLimits(max_decode_time_s=Seconds(2)),
            self.context(cal),
        )
        self.assertEqual(result.reason, ReasonCode.DECODE_TIMEOUT)

    def test_capture_contract_fault_matrix_and_benchmark(self) -> None:
        captured = datetime(2026, 9, 1, tzinfo=timezone.utc)
        for kwargs in (
            {"max_encoded_bytes": 0},
            {"max_width_px": 0},
            {"max_height_px": 0},
            {"max_retries": -1},
            {"max_pixels": 0},
            {"max_decode_time_s": Seconds(0)},
        ):
            with self.assertRaises(ValueError):
                CaptureLimits(**cast(Any, kwargs))
        with self.assertRaises(ValueError):
            CaptureRequest("device:/dev/video0", Seconds(1), "", "fp")
        with self.assertRaises(ValueError):
            CaptureRequest(
                "device:/dev/video0",
                Seconds(1),
                "s",
                "fp",
                cast(Any, datetime(2026, 9, 1, tzinfo=timezone(timedelta(hours=1)))),
            )
        with self.assertRaises(ValueError):
            CaptureRequest("device:/dev/video0", Seconds(1), "s", "fp", "x" * 1025)
        with self.assertRaises(ValueError):
            CaptureResult(None, ReasonCode.NONE, 0, 0, "s", "fp", captured, 100)
        with self.assertRaises(ValueError):
            CaptureResult(None, ReasonCode.NONE, 1, -1, "s", "fp", captured, 100)
        with self.assertRaises(ValueError):
            CaptureResult(
                None,
                ReasonCode.NONE,
                cast(Any, 1),
                0,
                "s",
                "fp",
                datetime(2026, 9, 1, tzinfo=timezone(timedelta(hours=1))),
                100,
            )
        with self.assertRaises(ValueError):
            CameraFrame(
                b"x",
                10,
                10,
                Seconds(0.1),
                "s",
                "camera",
                datetime(2026, 9, 1, tzinfo=timezone.utc),
                "x" * 1025,
            )
        with self.assertRaises(ValueError):
            CameraFrame(
                b"x",
                0,
                1,
                Seconds(0.1),
                "s",
                "camera",
                datetime(2026, 9, 1, tzinfo=timezone.utc),
            ).validate(CaptureLimits())
        with self.assertRaises(ValueError):
            CameraFrame(
                b"x",
                10,
                10,
                Seconds(-1),
                "s",
                "camera",
                datetime(2026, 9, 1, tzinfo=timezone.utc),
            ).validate(CaptureLimits())
        cal = self.calibration()
        self.assertEqual(
            benchmark_detectors(
                {"blob": BlobDetector(), "circle": CircleCandidateDetector()},
                [(self.frame(bytes(100), cal), cal)],
                CaptureLimits(),
            )["blob"]["dataset_label"],
            "SYNTHETIC",
        )

    def test_metadata_and_detection_negative_matrix(self) -> None:
        captured = datetime(2026, 9, 1, tzinfo=timezone.utc)
        bad_contexts = (
            ("", "fp", captured, captured, Seconds(1), "s", captured, Seconds(1)),
            ("c", "", captured, captured, Seconds(1), "s", captured, Seconds(1)),
            (
                "c",
                "fp",
                captured.replace(tzinfo=None),
                captured,
                Seconds(1),
                "s",
                captured,
                Seconds(1),
            ),
            (
                "c",
                "fp",
                captured,
                captured.replace(tzinfo=None),
                Seconds(1),
                "s",
                captured,
                Seconds(1),
            ),
            ("c", "fp", captured, captured, Seconds(-1), "s", captured, Seconds(1)),
            ("c", "fp", captured, captured, Seconds(1), "", captured, Seconds(1)),
        )
        for values in bad_contexts:
            with self.assertRaises(ValueError):
                DetectionContext(*cast(Any, (*values, 0.1)))
        with self.assertRaises(ValueError):
            CameraFrame(b"x", 1, 1, Seconds(0.1), "", "camera", captured)
        with self.assertRaises(ValueError):
            CameraFrame(b"x", 1, 1, Seconds(0.1), "s", "", captured)
        for kwargs in (
            {"confidence": 2.0},
            {"candidate_count": -1},
            {"frame_age_s": -1.0},
            {"uncertainty_mm": float("inf")},
            {"center_residual_px": -1.0},
            {"reason": "NONE"},
            {"verdict": "INVALID"},
            {"candidate_shapes": ("x" * 65,)},
            {"overlay_artifact": "not-bytes"},
        ):
            base: dict[str, Any] = {
                "calibration_id": "c",
                "frame_sample_id": "s",
                "camera_fingerprint": "fp",
                "center_x_px": None,
                "center_y_px": None,
                "confidence": 0.0,
                "candidate_count": 0,
                "reason": ReasonCode.INVALID_SAMPLE,
                "verdict": Verdict.INVALID,
                "frame_age_s": 0.0,
                "uncertainty_mm": 0.1,
            }
            base.update(kwargs)
            with self.assertRaises(ValueError):
                Detection(**base)
        with self.assertRaises(ValueError):
            DetectionContext(
                "c",
                "fp",
                captured,
                captured,
                Seconds(1),
                "s",
                captured,
                Seconds(1),
                0.1,
                cast(Any, 1),
            )
        with self.assertRaises(ValueError):
            Detection(
                "",
                "s",
                "fp",
                None,
                None,
                0.0,
                0,
                ReasonCode.INVALID_SAMPLE,
                Verdict.INVALID,
                0.0,
                0.1,
            )
        with self.assertRaises(ValueError):
            Detection(
                "c",
                "",
                "fp",
                None,
                None,
                0.0,
                0,
                ReasonCode.INVALID_SAMPLE,
                Verdict.INVALID,
                0.0,
                0.1,
            )
        with self.assertRaises(ValueError):
            Detection(
                "c",
                "s",
                "",
                None,
                None,
                0.0,
                0,
                ReasonCode.INVALID_SAMPLE,
                Verdict.INVALID,
                0.0,
                0.1,
            )
        with self.assertRaises(ValueError):
            Detection(
                "c",
                "s",
                "fp",
                None,
                None,
                0.0,
                0,
                ReasonCode.NONE,
                Verdict.PASS,
                0.0,
                0.1,
            )
        with self.assertRaises(ValueError):
            Detection(
                "c",
                "s",
                "fp",
                cast(Any, 1),
                None,
                0.0,
                0,
                ReasonCode.INVALID_SAMPLE,
                Verdict.INVALID,
                0.0,
                0.1,
            )
        with self.assertRaises(ValueError):
            Detection(
                "c",
                "s",
                "fp",
                None,
                cast(Any, 1),
                0.0,
                0,
                ReasonCode.INVALID_SAMPLE,
                Verdict.INVALID,
                0.0,
                0.1,
            )
        with self.assertRaises(ValueError):
            Detection(
                "c",
                "s",
                "fp",
                None,
                None,
                0.0,
                0,
                ReasonCode.INVALID_SAMPLE,
                Verdict.INVALID,
                0.0,
                0.1,
                center_residual_px=1,
            )
        successful = BlobDetector().detect(
            self.frame(bytes(100), self.calibration()),
            self.calibration(),
            CaptureLimits(),
            self.context(self.calibration()),
        )
        self.assertGreater(
            successful.combined_uncertainty_mm, successful.uncertainty_mm - 1e-12
        )

    def test_detector_corrupt_and_capture_terminal_faults(self) -> None:
        cal = self.calibration()
        context = self.context(cal)
        corrupt = CameraFrame(
            b"not-pgm",
            1,
            1,
            Seconds(0.1),
            "sample-1",
            cal.camera_fingerprint,
            context.captured_at_utc,
        )
        self.assertEqual(
            BlobDetector().detect(corrupt, cal, CaptureLimits(), context).reason,
            ReasonCode.CORRUPT_INPUT,
        )
        self.assertEqual(
            CircleCandidateDetector()
            .detect(corrupt, cal, CaptureLimits(), context)
            .reason,
            ReasonCode.CORRUPT_INPUT,
        )

        class Clock:
            def now_utc(self) -> datetime:
                return datetime(2026, 9, 1, tzinfo=timezone.utc)

        class Transport:
            def __init__(self, value: object) -> None:
                self.value = value

            def capture(self, target: str, timeout_s: Seconds) -> bytes:
                if isinstance(self.value, BaseException):
                    raise self.value
                return self.value  # type: ignore[return-value]

        from xyz_klipper_tool.vision.capture import BoundedCameraProvider

        request = CaptureRequest("device:/dev/video0", Seconds(1), "sample", "camera")
        self.assertEqual(
            BoundedCameraProvider(Transport(ValueError()), Clock(), CaptureLimits())
            .capture(request)
            .reason,
            ReasonCode.CORRUPT_INPUT,
        )
        self.assertEqual(
            BoundedCameraProvider(Transport(b""), Clock(), CaptureLimits())
            .capture(request)
            .reason,
            ReasonCode.MISSING_INPUT,
        )
        self.assertEqual(
            BoundedCameraProvider(
                Transport(b"123"), Clock(), CaptureLimits(max_encoded_bytes=2)
            )
            .capture(request)
            .reason,
            ReasonCode.OVERSIZED_INPUT,
        )
        self.assertEqual(
            BoundedCameraProvider(
                Transport(TimeoutError()), Clock(), CaptureLimits(max_retries=0)
            )
            .capture(request)
            .reason,
            ReasonCode.CAPTURE_TIMEOUT,
        )
        large = b"x" * (8 * 1024 * 1024 + 1)
        accepted = BoundedCameraProvider(
            Transport(large), Clock(), CaptureLimits(max_encoded_bytes=len(large))
        ).capture(request)
        self.assertEqual(accepted.reason, ReasonCode.NONE)
        rejected = BoundedCameraProvider(
            Transport(large), Clock(), CaptureLimits(max_encoded_bytes=len(large) - 1)
        ).capture(request)
        self.assertEqual(rejected.reason, ReasonCode.OVERSIZED_INPUT)

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

    def test_inventory_is_relative_hashed_and_split_requires_sessions(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = root / "session-a" / "frame.pgm"
            first.parent.mkdir()
            first.write_bytes(b"pixels")
            entries = build_inventory(root, [first])
            self.assertEqual(entries[0].path, Path("session-a/frame.pgm"))
            self.assertNotIn(str(root), inventory_json(entries))
            with self.assertRaises(ValueError):
                verify_inventory(
                    root,
                    [
                        CorpusEntry(
                            entries[0].entry_id,
                            entries[0].path,
                            entries[0].session_id,
                            entries[0].label,
                            "0" * 64,
                            entries[0].provenance,
                            0,
                            None,
                            "UNLABELED",
                            entries[0].byte_size,
                        )
                    ],
                )
        with self.assertRaises(ValueError):
            deterministic_split([CorpusEntry("a", Path("a"), "only", "x", "a" * 64)])

    def test_calibration_fault_before_replace_preserves_current(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            stages: list[str] = []
            armed = False

            def fault(stage: str) -> None:
                nonlocal armed
                stages.append(stage)
                if armed and stage == "before_current_replace":
                    raise RuntimeError(stage)

            store = JsonCalibrationStore(Path(directory), max_backups=3, fault=fault)
            calibration = self.calibration()
            store.put(calibration)
            armed = True
            with self.assertRaises(RuntimeError):
                store.put(calibration)
            self.assertEqual(store.get("cal-1"), calibration)
            self.assertIn("before_current_replace", stages)
            path = Path(directory) / "cal-1.json"
            path.write_text("{", encoding="utf-8")
            with self.assertRaises(ValueError):
                store.get("cal-1")
            path.write_text("{}", encoding="utf-8")
            with self.assertRaises(ValueError):
                store.get("cal-1")

    def test_calibration_backup_rotation_faults_preserve_current(self) -> None:
        stages_to_fault = (
            "backup_rotation_1",
            "backup_rotation_2",
            "backup_rotation_3",
        )
        for fault_stage in stages_to_fault:
            with (
                self.subTest(fault_stage=fault_stage),
                tempfile.TemporaryDirectory() as directory,
            ):
                seen: list[str] = []
                armed = [False]

                def fault(
                    stage: str,
                    target_stage: str = fault_stage,
                    seen_stages: list[str] = seen,
                    armed_flag: list[bool] = armed,
                ) -> None:
                    seen_stages.append(stage)
                    if armed_flag[0] and stage == target_stage:
                        raise RuntimeError(stage)

                store = JsonCalibrationStore(
                    Path(directory), max_backups=3, fault=fault
                )
                original = self.calibration()
                store.put(original)
                store.put(original)
                store.put(original)
                armed[0] = True
                with self.assertRaises(RuntimeError):
                    store.put(original)
                self.assertEqual(store.get("cal-1"), original)
                self.assertIn(fault_stage, seen)

    def test_calibration_and_inventory_bounds_faults(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaises(ValueError):
                JsonCalibrationStore(root, max_file_bytes=0)
            with self.assertRaises(ValueError):
                JsonCalibrationStore(root, max_backups=9)
            frame = root / "s" / "f.pgm"
            frame.parent.mkdir()
            frame.write_bytes(b"abc")
            with self.assertRaises(ValueError):
                build_inventory(root, [root.parent / "outside.pgm"])
            with self.assertRaises(ValueError):
                verify_inventory(
                    root,
                    [
                        CorpusEntry(
                            "x",
                            Path("s/f.pgm"),
                            "s",
                            "x",
                            "a" * 64,
                            "SYNTHETIC",
                            0,
                            None,
                            "x",
                            4,
                        )
                    ],
                )
            entry = build_inventory(root, [frame])[0]
            frame.write_bytes(b"changed")
            with self.assertRaises(ValueError):
                verify_inventory(root, [entry])
        for kwargs in (
            {"provenance": "REAL"},
            {"path": Path("../escape")},
            {"expected_candidate_count": -1},
            {"expected_center_px": (1.0,)},
            {"failure_class": "x" * 129},
            {"byte_size": -1},
        ):
            values: dict[str, Any] = {
                "entry_id": "x",
                "path": Path("f"),
                "session_id": "s",
                "label": "l",
                "sha256": "a" * 64,
            }
            values.update(kwargs)
            with self.assertRaises(ValueError):
                CorpusEntry(**values)

    def test_synthetic_holdout_benchmark_metrics(self) -> None:
        entries = (
            CorpusEntry(
                "one",
                Path("s/one.pgm"),
                "s",
                "target",
                "a" * 64,
                "SYNTHETIC",
                1,
                (1.0, 1.0),
                None,
                1,
            ),
            CorpusEntry(
                "two",
                Path("s/two.pgm"),
                "s",
                "target",
                "b" * 64,
                "SYNTHETIC",
                0,
                None,
                "ZERO_CANDIDATE",
                1,
            ),
        )
        report = evaluate_benchmark(
            entries,
            {
                "blob": lambda entry: (entry.expected_candidate_count, 0.5, ""),
                "circle": lambda entry: (entry.expected_candidate_count, 0.25, ""),
            },
        )
        self.assertEqual(set(report), {"blob", "circle"})
        self.assertEqual(report["blob"]["dataset_label"], "SYNTHETIC")
        self.assertEqual(report["blob"]["samples"], 2)

    @unittest.skipUnless(_jsonschema is not None, "install pinned dev validator")
    def test_phase03_schemas_are_draft202012_contracts(self) -> None:
        root = Path(__file__).parents[1]
        calibration_schema = json.loads(
            (root / "schemas" / "calibration-envelope.v1.schema.json").read_text()
        )
        corpus_schema = json.loads(
            (root / "schemas" / "corpus-manifest.v1.schema.json").read_text()
        )
        benchmark_schema = json.loads(
            (root / "schemas" / "benchmark-report.v1.schema.json").read_text()
        )
        for schema in (calibration_schema, corpus_schema, benchmark_schema):
            _jsonschema.Draft202012Validator.check_schema(schema)
        calibration_data = calibration_payload(self.calibration())
        calibration_instance = {
            "schema_version": 1,
            "calibration": calibration_data,
            "checksum": "a" * 64,
        }
        corpus_instance = {
            "schema_version": 1,
            "entries": [
                {
                    "entry_id": "e",
                    "path": "session/frame.pgm",
                    "session_id": "session",
                    "label": "target",
                    "sha256": "a" * 64,
                    "provenance": "SYNTHETIC",
                    "byte_size": 1,
                }
            ],
        }
        benchmark_instance: dict[str, Any] = {
            "dataset_label": "SYNTHETIC",
            "samples": 1,
            "true_positive": 1,
            "precision": 1.0,
            "recall": 1.0,
            "center_error_px_mean": 0.0,
            "failure_classes": [],
        }
        cases: tuple[tuple[dict[str, Any], dict[str, Any]], ...] = (
            (calibration_schema, calibration_instance),
            (corpus_schema, corpus_instance),
            (benchmark_schema, benchmark_instance),
        )
        for schema, instance in cases:
            validator = _jsonschema.Draft202012Validator(schema)
            self.assertEqual(list(validator.iter_errors(instance)), [])
            invalid = dict(instance)
            invalid["unexpected"] = True
            self.assertTrue(list(validator.iter_errors(invalid)))
        cast(dict[str, Any], calibration_instance["calibration"])["created_at_utc"] = (
            "2026-09-01T00:00:00+07:00"
        )
        self.assertTrue(
            list(
                _jsonschema.Draft202012Validator(calibration_schema).iter_errors(
                    calibration_instance
                )
            )
        )


if __name__ == "__main__":
    unittest.main()

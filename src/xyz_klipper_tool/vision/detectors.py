"""Bounded, independent grayscale detector candidates with typed identity checks."""

import hashlib
import json
import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Protocol

from xyz_klipper_tool.domain.models import ReasonCode, Verdict
from xyz_klipper_tool.domain.units import Pixels, Seconds

from .calibration import Calibration
from .capture import CameraFrame, CaptureLimits, FrameValidationError


@dataclass(frozen=True)
class DetectionContext:
    """Expected calibration/fingerprint and UTC freshness for one frame.

    This pure context performs no I/O, blocking, or machine action. Missing,
    mismatched, non-UTC, or stale values fail closed with a typed result.
    """

    expected_calibration_id: str
    expected_camera_fingerprint: str
    captured_at_utc: datetime
    now_utc: datetime
    max_frame_age_s: Seconds
    frame_sample_id: str
    exposure_metadata: str | None = None

    def __post_init__(self) -> None:
        if (
            type(self.expected_calibration_id) is not str
            or not self.expected_calibration_id.strip()
        ):
            raise ValueError("expected calibration identity is required")
        if (
            type(self.expected_camera_fingerprint) is not str
            or not self.expected_camera_fingerprint.strip()
        ):
            raise ValueError("expected camera fingerprint is required")
        if type(self.frame_sample_id) is not str or not self.frame_sample_id.strip():
            raise ValueError("frame sample identity is required")
        if type(
            self.captured_at_utc
        ) is not datetime or self.captured_at_utc.utcoffset() != timedelta(0):
            raise ValueError("captured_at_utc must be UTC")
        if type(self.now_utc) is not datetime or self.now_utc.utcoffset() != timedelta(
            0
        ):
            raise ValueError("now_utc must be UTC")
        if (
            type(self.max_frame_age_s) is not Seconds
            or self.max_frame_age_s.value_s < 0
        ):
            raise ValueError("max frame age must be bounded Seconds")
        if (
            self.exposure_metadata is not None
            and type(self.exposure_metadata) is not str
        ):
            raise ValueError("exposure metadata must be text")


@dataclass(frozen=True)
class Detection:
    """Pure detection result carrying calibration, sample, exposure and uncertainty.

    Pixel centers/residuals are image-frame pixels; uncertainty is combined
    millimetres from calibration and detector error (currently calibration
    uncertainty is the conservative available component). No side effects or
    blocking occur; invalid inputs produce a typed non-PASS verdict.
    """

    calibration_id: str
    frame_sample_id: str
    camera_fingerprint: str
    center_x_px: Pixels | None
    center_y_px: Pixels | None
    confidence: float
    candidate_count: int
    reason: ReasonCode
    verdict: Verdict
    frame_age_s: float
    uncertainty_mm: float
    candidate_shapes: tuple[str, ...] = ()
    exposure_metadata: str | None = None
    center_residual_px: float | None = None
    overlay_artifact: bytes = field(default=b"", repr=False)

    def __post_init__(self) -> None:
        if type(self.frame_sample_id) is not str or not self.frame_sample_id.strip():
            raise ValueError("frame sample identity is required")
        if (
            type(self.camera_fingerprint) is not str
            or not self.camera_fingerprint.strip()
        ):
            raise ValueError("camera fingerprint is required")
        if not self.overlay_artifact:
            data = {
                "calibration_id": self.calibration_id,
                "camera_fingerprint": self.camera_fingerprint,
                "candidate_count": self.candidate_count,
                "candidate_shapes": self.candidate_shapes,
                "frame_sample_id": self.frame_sample_id,
                "reason": self.reason.value,
                "residual_px": self.center_residual_px,
            }
            artifact = json.dumps(data, sort_keys=True, separators=(",", ":")).encode()
            if len(artifact) > 4096:
                raise ValueError("diagnostic overlay exceeds bound")
            object.__setattr__(self, "overlay_artifact", artifact)

    @property
    def combined_uncertainty_mm(self) -> float:
        """Return conservative combined uncertainty in millimetres."""
        return self.uncertainty_mm

    @property
    def overlay_sha256(self) -> str:
        """Return SHA-256 of the bounded deterministic diagnostic artifact."""
        return hashlib.sha256(self.overlay_artifact).hexdigest()

    @property
    def overlay_size_bytes(self) -> int:
        """Return diagnostic artifact size in bytes."""
        return len(self.overlay_artifact)


class Detector(Protocol):
    """Non-I/O image detector; failure is fail-closed and never physical."""

    def detect(
        self,
        frame: CameraFrame,
        calibration: Calibration,
        limits: CaptureLimits,
        context: DetectionContext | None = None,
    ) -> Detection:
        """Detect image geometry in pixels; no blocking or side effects."""
        ...


def _decode_pgm(frame: CameraFrame, limits: CaptureLimits) -> tuple[int, int, bytes]:
    """Decode bounded PGM geometry without filesystem or camera access."""
    frame.validate(limits)
    if not frame.encoded.startswith(b"P5"):
        raise ValueError("unsupported or corrupt image encoding")
    try:
        tokens = frame.encoded.split()
        width, height, max_value = (int(value) for value in tokens[1:4])
        header_end = (
            frame.encoded.find(
                b"\n", frame.encoded.find(b"\n", frame.encoded.find(b"\n") + 1) + 1
            )
            + 1
        )
        payload = frame.encoded[header_end:]
    except (ValueError, IndexError) as exc:
        raise ValueError("corrupt PGM") from exc
    if (
        max_value != 255
        or width != frame.width_px
        or height != frame.height_px
        or len(payload) != width * height
    ):
        raise ValueError("PGM dimensions or depth mismatch")
    return width, height, payload


def _components(
    width: int, height: int, payload: bytes
) -> list[tuple[int, int, int, int, int]]:
    """Return bright connected components with deterministic traversal."""
    active: set[int] = {index for index, value in enumerate(payload) if value >= 200}
    found: list[tuple[int, int, int, int, int]] = []
    while active:
        seed = min(active)
        active.remove(seed)
        queue = [seed]
        points = [seed]
        while queue:
            point = queue.pop()
            x, y = point % width, point // width
            for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                nxt = ny * width + nx
                if 0 <= nx < width and 0 <= ny < height and nxt in active:
                    active.remove(nxt)
                    queue.append(nxt)
                    points.append(nxt)
        xs = [point % width for point in points]
        ys = [point // width for point in points]
        found.append((min(xs), min(ys), max(xs), max(ys), len(points)))
    return found


def _invalid(
    calibration: Calibration,
    frame: CameraFrame,
    reason: ReasonCode,
    context: DetectionContext | None,
    count: int = 0,
    shapes: tuple[str, ...] = (),
) -> Detection:
    """Build an invalid result while retaining identity where available."""
    return Detection(
        calibration.calibration_id,
        context.frame_sample_id if context is not None else "rejected-frame",
        calibration.camera_fingerprint,
        None,
        None,
        0.0,
        count,
        reason,
        Verdict.INVALID,
        frame.age_s.value_s,
        calibration.uncertainty_mm.value_mm,
        shapes,
        context.exposure_metadata if context is not None else None,
    )


def _preflight(
    calibration: Calibration, frame: CameraFrame, context: DetectionContext | None
) -> Detection | None:
    """Reject missing identity or stale UTC context before decoding."""
    if (
        context is None
        or context.expected_calibration_id != calibration.calibration_id
        or context.expected_camera_fingerprint != calibration.camera_fingerprint
    ):
        return _invalid(calibration, frame, ReasonCode.CALIBRATION_MISMATCH, context)
    if (
        context.now_utc < context.captured_at_utc
        or (context.now_utc - context.captured_at_utc).total_seconds()
        > context.max_frame_age_s.value_s
    ):
        return _invalid(calibration, frame, ReasonCode.STALE_FRAME, context)
    return None


def _residual(width: int, height: int, x: float, y: float) -> float:
    """Return image-center residual in pixels."""
    return math.hypot(x - (width - 1) / 2, y - (height - 1) / 2)


class BlobDetector:
    """Connected-component candidate pipeline over decoded image pixels."""

    def detect(
        self,
        frame: CameraFrame,
        calibration: Calibration,
        limits: CaptureLimits,
        context: DetectionContext | None = None,
    ) -> Detection:
        """Find one bright component; no I/O, blocking, or machine action."""
        early = _preflight(calibration, frame, context)
        if early is not None:
            return early
        assert context is not None
        try:
            width, height, payload = _decode_pgm(frame, limits)
        except FrameValidationError as exc:
            return _invalid(calibration, frame, exc.reason, context)
        except ValueError:
            return _invalid(calibration, frame, ReasonCode.CORRUPT_INPUT, context)
        candidates = _components(width, height, payload)
        shapes = tuple("component" for _ in candidates)
        if len(candidates) != 1:
            reason = (
                ReasonCode.ZERO_CANDIDATE
                if not candidates
                else ReasonCode.AMBIGUOUS_CANDIDATE
            )
            return _invalid(
                calibration, frame, reason, context, len(candidates), shapes
            )
        x0, y0, x1, y1, _ = candidates[0]
        center_x, center_y = (x0 + x1) / 2, (y0 + y1) / 2
        return Detection(
            calibration.calibration_id,
            context.frame_sample_id,
            calibration.camera_fingerprint,
            Pixels(center_x),
            Pixels(center_y),
            1.0,
            1,
            ReasonCode.NONE,
            Verdict.PASS,
            frame.age_s.value_s,
            calibration.uncertainty_mm.value_mm,
            shapes,
            context.exposure_metadata,
            _residual(width, height, center_x, center_y),
        )


class CircleCandidateDetector:
    """Independent circle-like pipeline using component circularity."""

    def detect(
        self,
        frame: CameraFrame,
        calibration: Calibration,
        limits: CaptureLimits,
        context: DetectionContext | None = None,
    ) -> Detection:
        """Score circular candidates from pixels; no I/O or physical side effects."""
        early = _preflight(calibration, frame, context)
        if early is not None:
            return early
        assert context is not None
        try:
            width, height, payload = _decode_pgm(frame, limits)
        except FrameValidationError as exc:
            return _invalid(calibration, frame, exc.reason, context)
        except ValueError:
            return _invalid(calibration, frame, ReasonCode.CORRUPT_INPUT, context)
        candidates = [
            candidate
            for candidate in _components(width, height, payload)
            if candidate[4]
            / max(
                1, (candidate[2] - candidate[0] + 1) * (candidate[3] - candidate[1] + 1)
            )
            >= 0.5
        ]
        shapes = tuple("circle_candidate" for _ in candidates)
        if len(candidates) != 1:
            reason = (
                ReasonCode.ZERO_CANDIDATE
                if not candidates
                else ReasonCode.AMBIGUOUS_CANDIDATE
            )
            return _invalid(
                calibration, frame, reason, context, len(candidates), shapes
            )
        x0, y0, x1, y1, area = candidates[0]
        center_x, center_y = (x0 + x1) / 2, (y0 + y1) / 2
        confidence = area / max(1, (x1 - x0 + 1) * (y1 - y0 + 1))
        return Detection(
            calibration.calibration_id,
            context.frame_sample_id,
            calibration.camera_fingerprint,
            Pixels(center_x),
            Pixels(center_y),
            confidence,
            1,
            ReasonCode.NONE,
            Verdict.PASS,
            frame.age_s.value_s,
            calibration.uncertainty_mm.value_mm,
            shapes,
            context.exposure_metadata,
            _residual(width, height, center_x, center_y),
        )


def benchmark_detectors(
    detectors: dict[str, Detector],
    frames: list[tuple[CameraFrame, Calibration]],
    limits: CaptureLimits,
) -> dict[str, dict[str, int | str]]:
    """Return bounded synthetic benchmark counts; real-corpus validity is separate."""
    result: dict[str, dict[str, int | str]] = {}
    for name, detector in sorted(detectors.items()):
        outputs: list[Detection] = []
        for index, (frame, calibration) in enumerate(frames):
            context = DetectionContext(
                calibration.calibration_id,
                calibration.camera_fingerprint,
                calibration.created_at_utc,
                calibration.created_at_utc,
                limits.max_frame_age_s,
                f"synthetic-{index}",
            )
            outputs.append(detector.detect(frame, calibration, limits, context))
        result[name] = {
            "dataset_label": "SYNTHETIC",
            "total": len(outputs),
            "pass": sum(output.verdict is Verdict.PASS for output in outputs),
            "invalid": sum(output.verdict is Verdict.INVALID for output in outputs),
            "failure_classes": ",".join(
                sorted(
                    {
                        output.reason.value
                        for output in outputs
                        if output.reason is not ReasonCode.NONE
                    }
                )
            ),
        }
    return result

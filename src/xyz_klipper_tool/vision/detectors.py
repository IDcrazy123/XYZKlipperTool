"""Bounded, independent grayscale geometry detector candidates."""

from dataclasses import dataclass
from typing import Protocol

from xyz_klipper_tool.domain.models import ReasonCode, Verdict
from xyz_klipper_tool.domain.units import Pixels

from .calibration import Calibration
from .capture import CameraFrame, CaptureLimits, FrameValidationError


@dataclass(frozen=True)
class Detection:
    """Detection diagnostics with pixel geometry, calibration identity, age, and uncertainty."""

    calibration_id: str
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


class Detector(Protocol):
    """Non-I/O image detector; malformed, stale, and ambiguous frames fail closed."""

    def detect(
        self, frame: CameraFrame, calibration: Calibration, limits: CaptureLimits
    ) -> Detection:
        """Return a geometry-dependent diagnostic without physical side effects."""
        ...


def _decode_pgm(frame: CameraFrame, limits: CaptureLimits) -> tuple[int, int, bytes]:
    frame.validate(limits)
    if not frame.encoded.startswith(b"P5"):
        raise ValueError("unsupported or corrupt image encoding")
    try:
        tokens = frame.encoded.split()
        width, height, max_value = (int(x) for x in tokens[1:4])
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
    active: set[int] = {i for i, value in enumerate(payload) if value >= 200}
    found: list[tuple[int, int, int, int, int]] = []
    while active:
        seed = active.pop()
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
        xs = [p % width for p in points]
        ys = [p // width for p in points]
        found.append((min(xs), min(ys), max(xs), max(ys), len(points)))
    return found


def _invalid(
    calibration: Calibration,
    frame: CameraFrame,
    reason: ReasonCode,
    count: int = 0,
    shapes: tuple[str, ...] = (),
) -> Detection:
    return Detection(
        calibration.calibration_id,
        None,
        None,
        0.0,
        count,
        reason,
        Verdict.INVALID,
        frame.age_s.value_s,
        calibration.uncertainty_mm.value_mm,
        shapes,
    )


class BlobDetector:
    """Connected-component candidate pipeline over decoded grayscale pixel geometry."""

    def detect(
        self, frame: CameraFrame, calibration: Calibration, limits: CaptureLimits
    ) -> Detection:
        """Find one bright connected component; no marker bytes or I/O are used."""
        try:
            width, height, payload = _decode_pgm(frame, limits)
        except FrameValidationError as exc:
            return _invalid(calibration, frame, exc.reason)
        except ValueError:
            return _invalid(calibration, frame, ReasonCode.CORRUPT_INPUT)
        candidates = _components(width, height, payload)
        shapes = tuple("component" for _ in candidates)
        if len(candidates) != 1:
            return _invalid(
                calibration,
                frame,
                ReasonCode.ZERO_CANDIDATE
                if not candidates
                else ReasonCode.AMBIGUOUS_CANDIDATE,
                len(candidates),
                shapes,
            )
        x0, y0, x1, y1, area = candidates[0]
        box = (x1 - x0 + 1) * (y1 - y0 + 1)
        return Detection(
            calibration.calibration_id,
            Pixels((x0 + x1) / 2),
            Pixels((y0 + y1) / 2),
            min(1.0, area / box),
            1,
            ReasonCode.NONE,
            Verdict.PASS,
            frame.age_s.value_s,
            calibration.uncertainty_mm.value_mm,
            shapes,
        )


class CircleCandidateDetector:
    """Independent circle-like pipeline using component geometry and circularity."""

    def detect(
        self, frame: CameraFrame, calibration: Calibration, limits: CaptureLimits
    ) -> Detection:
        """Score circular candidates from pixels; benchmark evidence is still required."""
        try:
            width, height, payload = _decode_pgm(frame, limits)
        except FrameValidationError as exc:
            return _invalid(calibration, frame, exc.reason)
        except ValueError:
            return _invalid(calibration, frame, ReasonCode.CORRUPT_INPUT)
        candidates = [
            c
            for c in _components(width, height, payload)
            if c[4] / max(1, (c[2] - c[0] + 1) * (c[3] - c[1] + 1)) >= 0.5
        ]
        shapes = tuple("circle_candidate" for _ in candidates)
        if len(candidates) != 1:
            return _invalid(
                calibration,
                frame,
                ReasonCode.ZERO_CANDIDATE
                if not candidates
                else ReasonCode.AMBIGUOUS_CANDIDATE,
                len(candidates),
                shapes,
            )
        x0, y0, x1, y1, area = candidates[0]
        box = (x1 - x0 + 1) * (y1 - y0 + 1)
        return Detection(
            calibration.calibration_id,
            Pixels((x0 + x1) / 2),
            Pixels((y0 + y1) / 2),
            area / box,
            1,
            ReasonCode.NONE,
            Verdict.PASS,
            frame.age_s.value_s,
            calibration.uncertainty_mm.value_mm,
            shapes,
        )


def benchmark_detectors(
    detectors: dict[str, Detector],
    frames: list[tuple[CameraFrame, Calibration]],
    limits: CaptureLimits,
) -> dict[str, dict[str, int | str]]:
    """Return per-pipeline SYNTHETIC/evaluation counts and failure classes."""
    result: dict[str, dict[str, int | str]] = {}
    for name, detector in sorted(detectors.items()):
        outputs = [
            detector.detect(frame, calibration, limits) for frame, calibration in frames
        ]
        result[name] = {
            "dataset_label": "SYNTHETIC",
            "total": len(outputs),
            "pass": sum(x.verdict is Verdict.PASS for x in outputs),
            "invalid": sum(x.verdict is Verdict.INVALID for x in outputs),
            "failure_classes": ",".join(
                sorted(
                    {x.reason.value for x in outputs if x.reason is not ReasonCode.NONE}
                )
            ),
        }
    return result

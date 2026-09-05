# pyright: reportUnknownMemberType=false, reportUnknownArgumentType=false, reportUnknownVariableType=false
"""Bounded OpenCV JPEG adapter for host-side exploratory nozzle analysis.

This module is the only Phase 03 module importing OpenCV. It accepts raw JPEG
bytes from an explicitly supplied VoronBed snapshot, never opens a path, and
does not perform camera, network, printer, or filesystem I/O.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol, cast

import cv2
import numpy as np

from xyz_klipper_tool.domain.models import ReasonCode, Verdict
from xyz_klipper_tool.domain.units import Pixels

from .calibration import Calibration
from .detectors import Detection, DetectionContext


@dataclass(frozen=True)
class RoiBounds:
    """Configured pixel ROI; origin and size are image pixels, never machine coordinates."""

    x_px: int
    y_px: int
    width_px: int
    height_px: int
    calibration_id: str
    camera_fingerprint: str

    def __post_init__(self) -> None:
        if type(self.calibration_id) is not str or not self.calibration_id.strip():
            raise ValueError("ROI calibration identity is required")
        if (
            type(self.camera_fingerprint) is not str
            or not self.camera_fingerprint.strip()
        ):
            raise ValueError("ROI camera identity is required")
        if type(self.x_px) is not int or type(self.y_px) is not int:
            raise ValueError("ROI origin must be integer pixels")
        if type(self.width_px) is not int or type(self.height_px) is not int:
            raise ValueError("ROI size must be integer pixels")
        if not 1 <= self.width_px <= 8192 or not 1 <= self.height_px <= 8192:
            raise ValueError("ROI dimensions are bounded")


@dataclass(frozen=True)
class JpegAnalysisLimits:
    """Finite JPEG/ROI/quality bounds; no defaults encode a machine location."""

    max_encoded_bytes: int = 8 * 1024 * 1024
    max_pixels: int = 64_000_000
    glare_ratio_limit: float = 0.35
    blur_score_min: float = 8.0
    contrast_std_min: float = 5.0
    consensus_distance_px: float = 12.0

    def __post_init__(self) -> None:
        import math

        if (
            type(self.max_encoded_bytes) is not int
            or not 1 <= self.max_encoded_bytes <= 64 * 1024 * 1024
        ):
            raise ValueError("encoded bound is invalid")
        if type(self.max_pixels) is not int or not 1 <= self.max_pixels <= 256_000_000:
            raise ValueError("pixel bound is invalid")
        for value in (
            self.glare_ratio_limit,
            self.blur_score_min,
            self.contrast_std_min,
            self.consensus_distance_px,
        ):
            if type(value) is not float or not math.isfinite(value) or value < 0:
                raise ValueError("quality bound must be finite and nonnegative")
        if self.glare_ratio_limit > 1:
            raise ValueError("glare ratio must be within [0,1]")


@dataclass(frozen=True)
class QualityDiagnostics:
    """Bounded ROI diagnostics: ratios are unitless and blur/contrast are image statistics."""

    saturation_ratio: float
    glare_ratio: float
    blur_score: float
    contrast_std: float
    masked_pixel_count: int


@dataclass(frozen=True)
class ShapeDiagnostics:
    """Pixel-only fit evidence retained for one candidate; no millimetre claim."""

    circularity: float
    aspect_ratio: float
    radial_cv: float
    fit_residual_px: float
    has_hole: bool


@dataclass(frozen=True)
class JpegDetection:
    """Detection plus quality diagnostics and pipeline identity; no side effects or blocking."""

    detection: Detection
    quality: QualityDiagnostics
    pipeline: str
    shape: ShapeDiagnostics | None = None
    pipeline_candidate_counts: tuple[int, int] | tuple[()] = ()
    pipeline_reasons: tuple[str, str] | tuple[()] = ()
    pipeline_shape_scores: tuple[float | None, float | None] | tuple[()] = ()
    geometric_disagreement_px: float | None = None


class JpegDetector(Protocol):
    """Host-side pure detector plugin; malformed/stale input returns typed INVALID."""

    def detect_jpeg(
        self,
        encoded_jpeg: bytes,
        calibration: Calibration,
        roi: RoiBounds,
        context: DetectionContext,
        limits: JpegAnalysisLimits = JpegAnalysisLimits(),  # noqa: B008
    ) -> JpegDetection:
        """Analyze JPEG bytes in a configured ROI without I/O or physical side effects."""
        ...


def _invalid(
    calibration: Calibration,
    context: DetectionContext,
    reason: ReasonCode,
    quality: QualityDiagnostics | None = None,
    pipeline: str = "",
    candidate_count: int = 0,
) -> JpegDetection:
    detection = Detection(
        calibration.calibration_id,
        context.frame_sample_id,
        calibration.camera_fingerprint,
        None,
        None,
        0.0,
        candidate_count,
        reason,
        Verdict.INVALID,
        max(0.0, (context.now_utc - context.captured_at_utc).total_seconds()),
        calibration.uncertainty_mm.value_mm,
    )
    return JpegDetection(
        detection, quality or QualityDiagnostics(0.0, 0.0, 0.0, 0.0, 0), pipeline
    )


def _decode_roi(
    encoded_jpeg: bytes,
    calibration: Calibration,
    roi: RoiBounds,
    context: DetectionContext,
    limits: JpegAnalysisLimits,
) -> tuple[np.ndarray, QualityDiagnostics] | JpegDetection:
    if (
        context.expected_calibration_id != calibration.calibration_id
        or context.expected_camera_fingerprint != calibration.camera_fingerprint
        or context.calibration_created_at_utc != calibration.created_at_utc
    ):
        return _invalid(calibration, context, ReasonCode.CALIBRATION_MISMATCH)
    if (
        context.now_utc < context.captured_at_utc
        or (context.now_utc - context.captured_at_utc).total_seconds()
        > context.max_frame_age_s.value_s
        or context.now_utc < context.calibration_created_at_utc
        or (context.now_utc - context.calibration_created_at_utc).total_seconds()
        > context.max_calibration_age_s.value_s
    ):
        return _invalid(calibration, context, ReasonCode.STALE_FRAME)
    if (
        type(encoded_jpeg) is not bytes
        or not encoded_jpeg
        or len(encoded_jpeg) > limits.max_encoded_bytes
    ):
        return _invalid(calibration, context, ReasonCode.OVERSIZED_INPUT)
    encoded_array: Any = np.frombuffer(encoded_jpeg, dtype=np.uint8)
    decoded: Any = cv2.imdecode(encoded_array, cv2.IMREAD_GRAYSCALE)
    if decoded is None or decoded.ndim != 2:
        return _invalid(calibration, context, ReasonCode.CORRUPT_INPUT)
    height, width = cast(tuple[int, int], decoded.shape)
    if (
        width * height > limits.max_pixels
        or roi.x_px < 0
        or roi.y_px < 0
        or roi.x_px + roi.width_px > width
        or roi.y_px + roi.height_px > height
    ):
        return _invalid(calibration, context, ReasonCode.OVERSIZED_INPUT)
    if (
        roi.calibration_id != calibration.calibration_id
        or roi.camera_fingerprint != calibration.camera_fingerprint
    ):
        return _invalid(calibration, context, ReasonCode.CALIBRATION_MISMATCH)
    gray = decoded[
        roi.y_px : roi.y_px + roi.height_px, roi.x_px : roi.x_px + roi.width_px
    ]
    saturated = gray >= 250
    glare = cv2.dilate(saturated.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
    masked = gray.copy()
    if np.any(saturated):
        valid = gray[~saturated]
        masked[saturated] = np.median(valid) if valid.size else 0
    quality = QualityDiagnostics(
        float(np.mean(saturated)),
        float(np.mean(glare)),
        float(cv2.Laplacian(masked, cv2.CV_64F).var()),
        float(masked.std()),
        int(np.count_nonzero(saturated)),
    )
    return masked, quality


def _quality_reason(
    quality: QualityDiagnostics, limits: JpegAnalysisLimits
) -> ReasonCode | None:
    if quality.glare_ratio > limits.glare_ratio_limit:
        return ReasonCode.GLARE
    if quality.blur_score < limits.blur_score_min:
        return ReasonCode.BLUR
    if quality.contrast_std < limits.contrast_std_min:
        return ReasonCode.LOW_CONTRAST
    return None


def _result(
    calibration: Calibration,
    context: DetectionContext,
    quality: QualityDiagnostics,
    pipeline: str,
    point: tuple[float, float] | None,
    count: int,
    reason: ReasonCode = ReasonCode.NONE,
    confidence: float = 0.0,
    residual_px: float | None = None,
    shape: ShapeDiagnostics | None = None,
    pipeline_candidate_counts: tuple[int, int] | tuple[()] = (),
    pipeline_reasons: tuple[str, str] | tuple[()] = (),
    pipeline_shape_scores: tuple[float | None, float | None] | tuple[()] = (),
    geometric_disagreement_px: float | None = None,
) -> JpegDetection:
    if point is None or reason is not ReasonCode.NONE:
        return _invalid(
            calibration,
            context,
            reason if reason is not ReasonCode.NONE else ReasonCode.ZERO_CANDIDATE,
            quality,
            pipeline,
            count,
        )
    detection = Detection(
        calibration.calibration_id,
        context.frame_sample_id,
        calibration.camera_fingerprint,
        Pixels(point[0]),
        Pixels(point[1]),
        confidence,
        count,
        ReasonCode.NONE,
        Verdict.PASS,
        max(0.0, (context.now_utc - context.captured_at_utc).total_seconds()),
        calibration.uncertainty_mm.value_mm,
        (pipeline,),
        None,
        residual_px,
    )
    return JpegDetection(
        detection,
        quality,
        pipeline,
        shape,
        pipeline_candidate_counts,
        pipeline_reasons,
        pipeline_shape_scores,
        geometric_disagreement_px,
    )


def _shape_metrics(contour: Any, has_hole: bool) -> ShapeDiagnostics | None:
    """Compute bounded contour evidence in pixels and reject non-round shapes."""
    perimeter = float(cv2.arcLength(contour, True))
    area = float(cv2.contourArea(contour))
    if perimeter <= 0 or area <= 0 or len(contour) < 8:
        return None
    _, _, width, height = cv2.boundingRect(contour)
    aspect = max(width, height) / max(1, min(width, height))
    if aspect > 1.5:
        return None
    circularity = 4.0 * float(np.pi) * area / (perimeter * perimeter)
    moments = cv2.moments(contour)
    if not moments["m00"]:
        return None
    cx = moments["m10"] / moments["m00"]
    cy = moments["m01"] / moments["m00"]
    points = contour.reshape(-1, 2).astype(np.float64)
    radii = np.hypot(points[:, 0] - cx, points[:, 1] - cy)
    mean_radius = float(radii.mean())
    radial_cv = float(radii.std() / mean_radius) if mean_radius else float("inf")
    fit_residual = float(radii.std())
    if circularity < 0.55 or radial_cv > 0.35:
        return None
    return ShapeDiagnostics(circularity, aspect, radial_cv, fit_residual, has_hole)


class GradientRadialDetector:
    """Pipeline A: Sobel gradient/radial proxy, masking saturated highlights before localization."""

    def detect_jpeg(
        self,
        encoded_jpeg: bytes,
        calibration: Calibration,
        roi: RoiBounds,
        context: DetectionContext,
        limits: JpegAnalysisLimits = JpegAnalysisLimits(),  # noqa: B008
    ) -> JpegDetection:
        """Analyze bounded JPEG ROI in pixels; no I/O, blocking, motion, or safety assertion."""
        decoded = _decode_roi(encoded_jpeg, calibration, roi, context, limits)
        if isinstance(decoded, JpegDetection):
            return decoded
        gray, quality = decoded
        quality_reason = _quality_reason(quality, limits)
        if quality_reason is not None:
            return _result(
                calibration,
                context,
                quality,
                "gradient_radial",
                None,
                0,
                quality_reason,
            )
        edges = cv2.Canny(gray, 40, 120)
        contours, _ = cv2.findContours(
            edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        candidates: list[tuple[tuple[float, float], ShapeDiagnostics]] = []
        for contour in contours:
            if cv2.contourArea(contour) >= 12:
                approximation = cv2.approxPolyDP(
                    contour, 0.04 * cv2.arcLength(contour, True), True
                )
                shape = _shape_metrics(contour, False)
                if shape is not None and len(approximation) > 6:
                    moments = cv2.moments(contour)
                    candidates.append(
                        (
                            (
                                moments["m10"] / moments["m00"] + roi.x_px,
                                moments["m01"] / moments["m00"] + roi.y_px,
                            ),
                            shape,
                        )
                    )
        if len(candidates) != 1:
            return _result(
                calibration,
                context,
                quality,
                "gradient_radial",
                None,
                len(candidates),
                ReasonCode.ZERO_CANDIDATE
                if not candidates
                else ReasonCode.AMBIGUOUS_CANDIDATE,
            )
        point, shape = candidates[0]
        confidence = max(0.0, min(1.0, shape.circularity * (1.0 - shape.radial_cv)))
        return _result(
            calibration,
            context,
            quality,
            "gradient_radial",
            point,
            1,
            confidence=confidence,
            residual_px=shape.fit_residual_px,
            shape=shape,
        )


class ContourEllipseDetector:
    """Pipeline B: dark annular contour with bounded ellipse/circle fit."""

    def detect_jpeg(
        self,
        encoded_jpeg: bytes,
        calibration: Calibration,
        roi: RoiBounds,
        context: DetectionContext,
        limits: JpegAnalysisLimits = JpegAnalysisLimits(),  # noqa: B008
    ) -> JpegDetection:
        """Fit one bounded dark contour in ROI; no I/O, blocking, or physical side effect."""
        decoded = _decode_roi(encoded_jpeg, calibration, roi, context, limits)
        if isinstance(decoded, JpegDetection):
            return decoded
        gray, quality = decoded
        quality_reason = _quality_reason(quality, limits)
        if quality_reason is not None:
            return _result(
                calibration,
                context,
                quality,
                "contour_ellipse",
                None,
                0,
                quality_reason,
            )
        _, threshold = cv2.threshold(gray, 90, 255, cv2.THRESH_BINARY_INV)
        contours, hierarchy = cv2.findContours(
            threshold, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE
        )
        candidates: list[tuple[tuple[float, float], ShapeDiagnostics]] = []
        for index, contour in enumerate(contours):
            if hierarchy is not None and hierarchy[0][index][3] != -1:
                continue
            area = cv2.contourArea(contour)
            if area >= 20 and len(contour) >= 5:
                child = hierarchy is not None and hierarchy[0][index][2] != -1
                if not child:
                    continue
                shape = _shape_metrics(contour, True)
                if shape is None:
                    continue
                (x, y), axes, _ = cv2.fitEllipse(contour)
                aspect = max(float(axes[0]), float(axes[1])) / max(
                    1.0, min(float(axes[0]), float(axes[1]))
                )
                if aspect > 1.5:
                    continue
                shape = ShapeDiagnostics(
                    shape.circularity,
                    aspect,
                    shape.radial_cv,
                    shape.fit_residual_px,
                    True,
                )
                candidates.append(((x + roi.x_px, y + roi.y_px), shape))
        if len(candidates) != 1:
            return _result(
                calibration,
                context,
                quality,
                "contour_ellipse",
                None,
                len(candidates),
                ReasonCode.ZERO_CANDIDATE
                if not candidates
                else ReasonCode.AMBIGUOUS_CANDIDATE,
            )
        point, shape = candidates[0]
        confidence = max(0.0, min(1.0, shape.circularity * (1.0 - shape.radial_cv)))
        return _result(
            calibration,
            context,
            quality,
            "contour_ellipse",
            point,
            1,
            confidence=confidence,
            residual_px=shape.fit_residual_px,
            shape=shape,
        )


class ConsensusJpegDetector:
    """Run both independent pipelines and emit PASS only on fresh, unique consensus."""

    def __init__(
        self, gradient: JpegDetector | None = None, contour: JpegDetector | None = None
    ) -> None:
        self.gradient = gradient or GradientRadialDetector()
        self.contour = contour or ContourEllipseDetector()

    def detect_jpeg(
        self,
        encoded_jpeg: bytes,
        calibration: Calibration,
        roi: RoiBounds,
        context: DetectionContext,
        limits: JpegAnalysisLimits = JpegAnalysisLimits(),  # noqa: B008
    ) -> JpegDetection:
        """Return consensus in image pixels; no I/O/blocking/physical action, fail closed on disagreement."""
        first = self.gradient.detect_jpeg(
            encoded_jpeg, calibration, roi, context, limits
        )
        second = self.contour.detect_jpeg(
            encoded_jpeg, calibration, roi, context, limits
        )
        quality = QualityDiagnostics(
            max(first.quality.saturation_ratio, second.quality.saturation_ratio),
            max(first.quality.glare_ratio, second.quality.glare_ratio),
            min(first.quality.blur_score, second.quality.blur_score),
            min(first.quality.contrast_std, second.quality.contrast_std),
            max(first.quality.masked_pixel_count, second.quality.masked_pixel_count),
        )
        if (
            first.detection.verdict is not Verdict.PASS
            or second.detection.verdict is not Verdict.PASS
        ):
            reason = (
                first.detection.reason
                if first.detection.verdict is not Verdict.PASS
                else second.detection.reason
            )
            return _invalid(calibration, context, reason, quality, "consensus")
        assert (
            first.detection.center_x_px is not None
            and first.detection.center_y_px is not None
        )
        assert (
            second.detection.center_x_px is not None
            and second.detection.center_y_px is not None
        )
        distance = float(
            np.hypot(
                first.detection.center_x_px.value_px
                - second.detection.center_x_px.value_px,
                first.detection.center_y_px.value_px
                - second.detection.center_y_px.value_px,
            )
        )
        if distance > limits.consensus_distance_px:
            return _invalid(
                calibration,
                context,
                ReasonCode.PIPELINE_DISAGREEMENT,
                quality,
                "consensus",
            )
        return _result(
            calibration,
            context,
            quality,
            "consensus",
            (
                (
                    first.detection.center_x_px.value_px
                    + second.detection.center_x_px.value_px
                )
                / 2,
                (
                    first.detection.center_y_px.value_px
                    + second.detection.center_y_px.value_px
                )
                / 2,
            ),
            2,
            confidence=min(first.detection.confidence, second.detection.confidence),
            residual_px=max(
                value
                for value in (
                    first.detection.center_residual_px,
                    second.detection.center_residual_px,
                )
                if value is not None
            ),
            pipeline_candidate_counts=(
                first.detection.candidate_count,
                second.detection.candidate_count,
            ),
            pipeline_reasons=(
                first.detection.reason.value,
                second.detection.reason.value,
            ),
            pipeline_shape_scores=(
                first.shape.circularity if first.shape is not None else None,
                second.shape.circularity if second.shape is not None else None,
            ),
            geometric_disagreement_px=distance,
        )

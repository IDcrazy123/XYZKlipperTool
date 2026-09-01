"""Bounded host-side camera, calibration, detector, and corpus contracts."""

from .calibration import (
    Calibration,
    CalibrationStore,
    JsonCalibrationStore,
    Transform2D,
)
from .capture import (
    CameraFrame,
    CaptureLimits,
    CaptureRequest,
    FrameValidationError,
    validate_camera_url,
)
from .corpus import CorpusEntry, CorpusSplit, deterministic_split
from .detectors import (
    BlobDetector,
    CircleCandidateDetector,
    Detection,
    Detector,
    benchmark_detectors,
)

__all__ = [
    "BlobDetector",
    "Calibration",
    "CalibrationStore",
    "CameraFrame",
    "CaptureLimits",
    "CaptureRequest",
    "CircleCandidateDetector",
    "CorpusEntry",
    "CorpusSplit",
    "Detection",
    "Detector",
    "FrameValidationError",
    "JsonCalibrationStore",
    "Transform2D",
    "benchmark_detectors",
    "deterministic_split",
    "validate_camera_url",
]

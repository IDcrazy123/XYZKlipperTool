"""Bounded host-side camera, calibration, detector, and corpus contracts."""

from .calibration import (
    Calibration,
    CalibrationStore,
    JsonCalibrationStore,
    Transform2D,
)
from .capture import (
    BoundedCameraProvider,
    CameraClock,
    CameraFrame,
    CameraTransport,
    CaptureLimits,
    CaptureRequest,
    CaptureResult,
    FrameValidationError,
    validate_camera_url,
)
from .corpus import CorpusEntry, CorpusSplit, deterministic_split
from .detectors import (
    BlobDetector,
    CircleCandidateDetector,
    Detection,
    DetectionContext,
    Detector,
    benchmark_detectors,
)

__all__ = [
    "BlobDetector",
    "BoundedCameraProvider",
    "Calibration",
    "CalibrationStore",
    "CameraClock",
    "CameraFrame",
    "CameraTransport",
    "CaptureLimits",
    "CaptureRequest",
    "CaptureResult",
    "CircleCandidateDetector",
    "CorpusEntry",
    "CorpusSplit",
    "Detection",
    "DetectionContext",
    "Detector",
    "FrameValidationError",
    "JsonCalibrationStore",
    "Transform2D",
    "benchmark_detectors",
    "deterministic_split",
    "validate_camera_url",
]

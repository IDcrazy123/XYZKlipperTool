"""Read explicit user-provided images and print unlabeled exploratory diagnostics only."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from xyz_klipper_tool.domain.units import CoordinateFrame, Millimetres, Seconds
from xyz_klipper_tool.vision.calibration import Calibration, Transform2D
from xyz_klipper_tool.vision.detectors import DetectionContext
from xyz_klipper_tool.vision.jpeg_adapter import (
    ContourEllipseDetector,
    GradientRadialDetector,
    JpegAnalysisLimits,
    RoiBounds,
)


def main() -> int:
    """Analyze an explicit directory without writing files or claiming accuracy."""
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    parser.add_argument("--calibration-id", required=True)
    parser.add_argument("--camera-fingerprint", required=True)
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument(
        "--roi", nargs=4, type=int, metavar=("X", "Y", "WIDTH", "HEIGHT"), required=True
    )
    parser.add_argument("--mm-per-pixel-x", type=float, required=True)
    parser.add_argument("--mm-per-pixel-y", type=float, required=True)
    args = parser.parse_args()
    root = args.path.resolve()
    if not root.exists() or not root.is_file() and not root.is_dir():
        raise SystemExit("path must be an image file or directory")
    now = datetime.now(timezone.utc)
    calibration = Calibration(
        args.calibration_id,
        1,
        "explicit-user-camera",
        args.camera_fingerprint,
        Transform2D(
            args.mm_per_pixel_x,
            args.mm_per_pixel_y,
            Millimetres(0.0),
            Millimetres(0.0),
            CoordinateFrame.CAMERA_IMAGE,
            CoordinateFrame.TOOL,
        ),
        0.0,
        Millimetres(0.0),
        args.source_sha256,
        now,
    )
    roi = RoiBounds(*args.roi, args.calibration_id, args.camera_fingerprint)
    context = DetectionContext(
        args.calibration_id,
        args.camera_fingerprint,
        now,
        now,
        Seconds(300.0),
        "exploratory-sample",
        now,
        Seconds(300.0),
        1.0,
    )
    print(
        json.dumps(
            {
                "provenance": "USER_PROVIDED_UNLABELED",
                "metric_claim": False,
                "path": str(root),
                "files": [],
            },
            sort_keys=True,
        )
    )
    paths = (
        [root] if root.is_file() else sorted(root.iterdir(), key=lambda item: item.name)
    )
    for path in paths:
        if path.suffix.lower() not in {".jpg", ".jpeg"}:
            continue
        encoded = path.read_bytes()
        first = GradientRadialDetector().detect_jpeg(
            encoded, calibration, roi, context, JpegAnalysisLimits()
        )
        second = ContourEllipseDetector().detect_jpeg(
            encoded, calibration, roi, context, JpegAnalysisLimits()
        )
        print(
            json.dumps(
                {
                    "name": path.name,
                    "byte_size": len(encoded),
                    "sha256": hashlib.sha256(encoded).hexdigest(),
                    "status": "EXCLUDED_PENDING_LABELS",
                    "reason": "MISSING_INPUT",
                    "pipeline_a": first.detection.reason.value,
                    "pipeline_b": second.detection.reason.value,
                    "quality": first.quality.__dict__,
                },
                sort_keys=True,
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

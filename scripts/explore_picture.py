# pyright: reportUnknownMemberType=false, reportUnknownArgumentType=false, reportUnknownVariableType=false
"""Read explicit user-provided images and print unlabeled exploratory diagnostics only."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, cast

import cv2
import numpy as np

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
    parser.add_argument("--calibration-id")
    parser.add_argument("--camera-fingerprint")
    parser.add_argument("--source-sha256")
    parser.add_argument(
        "--roi", nargs=4, type=int, metavar=("X", "Y", "WIDTH", "HEIGHT"), required=True
    )
    parser.add_argument("--mm-per-pixel-x", type=float)
    parser.add_argument("--mm-per-pixel-y", type=float)
    args = parser.parse_args()
    root = args.path.resolve()
    if not root.exists() or not root.is_file() and not root.is_dir():
        raise SystemExit("path must be an image file or directory")
    now = datetime.now(timezone.utc)
    supplied_calibration = all(
        value is not None
        for value in (
            args.calibration_id,
            args.camera_fingerprint,
            args.source_sha256,
            args.mm_per_pixel_x,
            args.mm_per_pixel_y,
        )
    )
    calibration = None
    roi = None
    context = None
    if supplied_calibration:
        calibration_id = cast(str, args.calibration_id)
        camera_fingerprint = cast(str, args.camera_fingerprint)
        source_sha256 = cast(str, args.source_sha256)
        mm_per_pixel_x = cast(float, args.mm_per_pixel_x)
        mm_per_pixel_y = cast(float, args.mm_per_pixel_y)
        calibration = Calibration(
            calibration_id,
            1,
            "explicit-user-camera",
            camera_fingerprint,
            Transform2D(
                mm_per_pixel_x,
                mm_per_pixel_y,
                Millimetres(0.0),
                Millimetres(0.0),
                CoordinateFrame.CAMERA_IMAGE,
                CoordinateFrame.TOOL,
            ),
            0.0,
            Millimetres(0.0),
            source_sha256,
            now,
        )
        roi = RoiBounds(
            args.roi[0],
            args.roi[1],
            args.roi[2],
            args.roi[3],
            calibration_id,
            camera_fingerprint,
        )
        context = DetectionContext(
            calibration_id,
            camera_fingerprint,
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
        if not supplied_calibration:
            decoded: Any = cv2.imdecode(
                np.frombuffer(encoded, dtype=np.uint8), cv2.IMREAD_GRAYSCALE
            )
            if decoded is None or decoded.ndim != 2:
                quality = {
                    "saturation_ratio": 0.0,
                    "glare_ratio": 0.0,
                    "blur_score": 0.0,
                    "contrast_std": 0.0,
                    "masked_pixel_count": 0,
                }
                reason = "CORRUPT_INPUT"
            else:
                x, y, width, height = args.roi
                crop = decoded[y : y + height, x : x + width]
                saturated = crop >= 250
                quality = {
                    "saturation_ratio": float(np.mean(saturated)),
                    "glare_ratio": float(
                        np.mean(
                            cv2.dilate(
                                saturated.astype(np.uint8), np.ones((3, 3), np.uint8)
                            )
                            > 0
                        )
                    ),
                    "blur_score": float(cv2.Laplacian(crop, cv2.CV_64F).var()),
                    "contrast_std": float(crop.std()),
                    "masked_pixel_count": int(np.count_nonzero(saturated)),
                }
                reason = "CALIBRATION_UNAVAILABLE"
            record = {
                "name": path.name,
                "byte_size": len(encoded),
                "sha256": hashlib.sha256(encoded).hexdigest(),
                "status": "EXCLUDED_PENDING_LABELS",
                "reason": reason,
                "pipeline_a": "CALIBRATION_UNAVAILABLE",
                "pipeline_b": "CALIBRATION_UNAVAILABLE",
                "quality": quality,
            }
            print(json.dumps(record, sort_keys=True))
            continue
        assert calibration is not None and roi is not None and context is not None
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

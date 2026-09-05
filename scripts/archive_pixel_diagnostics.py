# pyright: reportUnknownMemberType=false, reportUnknownArgumentType=false, reportUnknownVariableType=false
"""Read-only archived JPEG candidate inspection; never produces calibrated measurements."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import cv2
import numpy as np

from xyz_klipper_tool.vision.jpeg_bounds import (
    JpegBoundaryError,
    read_bounded,
    validate_jpeg_header,
)

MAX_BYTES = 8 * 1024 * 1024
MAX_PIXELS = 64_000_000


def numeric(values: list[float]) -> dict[str, object]:
    if not values:
        return {
            "count": 0,
            "mean": None,
            "median": None,
            "sample_sd": None,
            "mad": None,
            "min": None,
            "max": None,
            "range": None,
        }
    med = statistics.median(values)
    return {
        "count": len(values),
        "mean": statistics.fmean(values),
        "median": med,
        "sample_sd": statistics.stdev(values) if len(values) > 1 else None,
        "mad": statistics.median(abs(v - med) for v in values),
        "min": min(values),
        "max": max(values),
        "range": max(values) - min(values),
    }


def candidates(gray: Any, x0: int, y0: int) -> tuple[list[dict[str, object]], Any]:
    edges = cv2.Canny(gray, 40, 120)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    found: list[dict[str, object]] = []
    for contour in contours:
        area = float(cv2.contourArea(contour))
        perimeter = float(cv2.arcLength(contour, True))
        if area < 20 or perimeter <= 0:
            continue
        moments = cv2.moments(contour)
        if not moments["m00"]:
            continue
        cx = moments["m10"] / moments["m00"]
        cy = moments["m01"] / moments["m00"]
        points = contour.reshape(-1, 2).astype(np.float64)
        radius = np.hypot(points[:, 0] - cx, points[:, 1] - cy)
        residual = float(radius.std())
        shape_score = max(0.0, min(1.0, 4.0 * np.pi * area / (perimeter * perimeter)))
        found.append(
            {
                "center_px": [cx + x0, cy + y0],
                "area_px2": area,
                "bbox_px": list(map(int, cv2.boundingRect(contour))),
                "shape_score": shape_score,
                "fit_residual_px": residual,
                "accepted_as_nozzle": False,
                "rejection_reasons": ["UNCALIBRATED_CANDIDATE_ONLY"],
            }
        )
    return found, contours


def measure(
    image: Any, bounds: tuple[int, int, int, int], full_w: int, full_h: int
) -> dict[str, object]:
    x, y, w, h = bounds
    if x < 0 or y < 0 or w < 1 or h < 1 or x + w > full_w or y + h > full_h:
        return {"status": "INVALID", "reason": "ROI_OUT_OF_BOUNDS"}
    crop = image[y : y + h, x : x + w]
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY).astype(np.float64)
    values = [float(v) for v in gray.ravel().tolist()]
    all_channels = crop.astype(np.uint16)
    found, _contours = candidates(gray.astype(np.uint8), x, y)
    result = numeric(values)
    result.update(
        {
            "status": "VALID_PIXELS",
            "candidate_count": len(found),
            "candidates": found,
            "shape_score_is_not_confidence": True,
            "uncertainty_mm": None,
            "clipped_all_channels_ge_250_count": int(
                np.count_nonzero(np.all(all_channels >= 250, axis=2))
            ),
            "clipped_all_channels_ge_250_ratio": float(
                np.mean(np.all(all_channels >= 250, axis=2))
            ),
            "grayscale_saturation_ge_250_count": int(np.count_nonzero(gray >= 250)),
            "grayscale_saturation_ge_250_ratio": float(np.mean(gray >= 250)),
            "underexposed_all_channels_le_1_count": int(
                np.count_nonzero(np.all(all_channels <= 1, axis=2))
            ),
            "underexposed_all_channels_le_1_ratio": float(
                np.mean(np.all(all_channels <= 1, axis=2))
            ),
            "blur_score": float(cv2.Laplacian(gray, cv2.CV_64F).var()),
            "contrast_std": float(gray.std()),
            "bounds_px": [x, y, w, h],
        }
    )
    return result


def load_metadata(
    root: Path, path: Path, item: dict[str, Any], digest: str
) -> tuple[dict[str, Any], Path | None]:
    """Load the supported canary/HIL metadata contract or fail with context."""
    metadata_rel = item.get("metadata")
    candidates: list[Path] = []
    if isinstance(metadata_rel, str):
        candidates.append((root / metadata_rel.replace("/", "\\")).resolve())
    if not candidates:
        relative = path.relative_to(root)
        run_root = root / relative.parts[0] if relative.parts else root
        candidates.extend((run_root / "metadata").glob("**/*.json"))
    for candidate in candidates:
        if root not in candidate.parents or not candidate.is_file():
            continue
        try:
            metadata = json.loads(candidate.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise SystemExit(f"metadata malformed: {candidate}: {error}") from error
        if not isinstance(metadata, dict):
            raise SystemExit(f"metadata must be an object: {candidate}")
        if metadata_rel is not None:
            return metadata, candidate
        metadata_digest = metadata.get(
            "sha256", metadata.get("camera", {}).get("sha256")
        )
        if metadata_digest == digest or metadata.get("raw_path") == str(
            path.relative_to(candidate.parents[1])
        ).replace("\\", "/"):
            return metadata, candidate
    if "capture_status" in item or "corpus_inclusion" in item:
        return item, None
    raise SystemExit(f"metadata missing or unsupported for source: {path}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", action="append", type=Path, required=True)
    parser.add_argument("--source-manifest", action="append", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--roi", nargs=4, type=int, required=True)
    args = parser.parse_args()
    if len(args.source_root) != len(args.source_manifest):
        raise SystemExit("each source root requires one manifest")
    output = args.output.resolve()
    if output.exists() or output.is_symlink():
        raise SystemExit("output already exists; refusing overwrite")
    output.mkdir(parents=True)
    roi = tuple(args.roi)
    records: list[dict[str, object]] = []
    source_manifest_sha256: dict[str, str] = {}
    seen_source_entries: set[tuple[str, str, str]] = set()
    for root_arg, manifest_arg in zip(args.source_root, args.source_manifest):
        root = root_arg.resolve()
        manifest = manifest_arg.resolve()
        if not manifest.is_file() or root not in manifest.parents:
            raise SystemExit("manifest must resolve under its source root")
        source_manifest_sha256[str(manifest)] = hashlib.sha256(
            manifest.read_bytes()
        ).hexdigest()
        data = json.loads(manifest.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise SystemExit(f"manifest must be an object: {manifest}")
        entries = data.get("frames", data.get("items"))
        if not isinstance(entries, list):
            raise SystemExit(f"manifest missing frames/items: {manifest}")
        for item in entries:
            if not isinstance(item, dict):
                raise SystemExit(f"malformed manifest entry: {manifest}")
            rel = str(item.get("file", item.get("raw", item.get("path", "")))).replace(
                "/", "\\"
            )
            if not rel:
                raise SystemExit(f"manifest entry missing path: {manifest}")
            path = (root / rel).resolve()
            if root not in path.parents or path.suffix.lower() not in {".jpg", ".jpeg"}:
                raise SystemExit("manifest source path escapes root or is not JPEG")
            raw = read_bounded(path, MAX_BYTES)
            digest = str(item["sha256"])
            source_key = (str(root), digest, rel)
            if source_key in seen_source_entries:
                raise SystemExit(f"duplicate manifest source entry: {digest}")
            seen_source_entries.add(source_key)
            if (
                len(raw) == 0
                or len(raw) > MAX_BYTES
                or hashlib.sha256(raw).hexdigest() != digest
            ):
                raise SystemExit(f"source byte/hash validation failed: {path}")
            base: dict[str, object] = {
                "source_manifest": str(manifest),
                "source": root.name,
                "name": path.name,
                "source_sha256": digest,
                "bytes": len(raw),
                "level_uint8": item.get(
                    "brightness_uint8", item.get("level", "UNKNOWN")
                ),
                "frame": item.get("frame", item.get("frame_id", "UNKNOWN")),
                "frame_time": "UNKNOWN",
                "calibration": "UNAVAILABLE",
                "machine_eligibility": False,
                "accepted_nozzle": False,
            }
            metadata, metadata_path = load_metadata(root, path, item, digest)
            if metadata_path is not None:
                base["metadata_sha256"] = hashlib.sha256(
                    metadata_path.read_bytes()
                ).hexdigest()
            reasons = metadata.get("reason_codes")
            if isinstance(reasons, list) and all(
                isinstance(value, str) for value in reasons
            ):
                base["source_reason_codes"] = reasons
                normalized_reason = reasons[0] if reasons else "UNKNOWN_METADATA"
                base["raw_http_evidence"] = (
                    "MISSING"
                    if "HTTP_EVIDENCE_PERSISTENCE_FAILED" in reasons
                    else "PRESENT_OR_NOT_CLAIMED"
                )
            else:
                normalized_reason = metadata.get(
                    "invalid_reason", metadata.get("capture_status", "UNKNOWN_METADATA")
                )
                base["raw_http_evidence"] = "UNKNOWN"
            base["claim_status"] = metadata.get("claim_status", "UNKNOWN")
            base["homed_axes"] = metadata.get(
                "homed_axes", metadata.get("homed_axes_before", "UNKNOWN")
            )
            base["frame_time"] = metadata.get("captured_at_utc", "UNKNOWN")
            capture_status = metadata.get("capture_status", "UNKNOWN")
            source_status = capture_status
            if source_status == "UNKNOWN":
                source_status = metadata.get("claim_status", "UNKNOWN")
            base["source_capture_status"] = capture_status
            base["source_invalid_reason"] = metadata.get("invalid_reason", "UNKNOWN")
            base["source_corpus_inclusion"] = metadata.get(
                "corpus_inclusion", "UNKNOWN"
            )
            base["source_verdict"] = metadata.get("verdict", "UNKNOWN")
            base["source_status"] = source_status
            base["reason"] = normalized_reason
            try:
                validate_jpeg_header(raw, MAX_BYTES, MAX_PIXELS)
            except JpegBoundaryError as error:
                base.update(
                    {
                        "status": "INVALID",
                        "reason": error.reason.value,
                        "full_frame": None,
                        "development_roi": None,
                    }
                )
                records.append(base)
                continue
            try:
                image = cv2.imdecode(
                    np.frombuffer(raw, dtype=np.uint8), cv2.IMREAD_COLOR
                )
            except cv2.error:
                image = None
            if (
                image is None
                or image.ndim != 3
                or image.shape[0] * image.shape[1] > MAX_PIXELS
            ):
                base.update(
                    {
                        "status": "INVALID",
                        "reason": "CORRUPT_OR_OVERSIZED",
                        "full_frame": None,
                        "development_roi": None,
                    }
                )
                records.append(base)
                continue
            h, w = image.shape[:2]
            base.update(
                {
                    "status": source_status,
                    "reason": normalized_reason,
                    "dimensions_px": [int(w), int(h)],
                    "full_frame": measure(image, (0, 0, w, h), w, h),
                    "development_roi": measure(image, roi, w, h),
                }
            )
            full_bounds = (0, 0, w, h)
            for name, bounds in (("full_frame", full_bounds), ("development_roi", roi)):
                overlay = image.copy()
                bx, by, bw, bh = bounds
                cv2.rectangle(
                    overlay, (bx, by), (bx + bw - 1, by + bh - 1), (0, 255, 255), 2
                )
                section = base[name]
                if isinstance(section, dict):
                    for candidate in section.get("candidates", []):
                        center = candidate["center_px"]
                        cv2.drawMarker(
                            overlay,
                            (round(float(center[0])), round(float(center[1]))),
                            (0, 0, 255),
                            cv2.MARKER_CROSS,
                            18,
                            2,
                        )
                cv2.putText(
                    overlay,
                    "CANDIDATE ONLY / UNCALIBRATED",
                    (20, 35),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 0, 255),
                    2,
                )
                overlay_dir = output / "overlays" / name
                overlay_dir.mkdir(parents=True, exist_ok=True)
                source_namespace = hashlib.sha256(str(root).encode()).hexdigest()[:16]
                overlay_name = f"{source_namespace}__{source_manifest_sha256[str(manifest)][:16]}__{hashlib.sha256(str(path.relative_to(root)).encode()).hexdigest()[:16]}__{path.name}"
                overlay_path = overlay_dir / overlay_name
                if overlay_path.exists() or not cv2.imwrite(str(overlay_path), overlay):
                    raise SystemExit(
                        f"overlay write failed or would overwrite: {overlay_path}"
                    )
            records.append(base)
    report = {
        "schema": "xyz-klipper-tool.archived-pixel-candidate-inspection.v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "argv": sys.argv,
        "python": sys.version,
        "platform": platform.platform(),
        "opencv": cv2.__version__,
        "parameters": {
            "full_frame": "decoded image bounds",
            "development_roi_px": roi,
            "max_encoded_bytes": MAX_BYTES,
            "max_pixels": MAX_PIXELS,
            "calibration": "UNAVAILABLE",
            "machine_eligibility": False,
            "shape_score": "bounded geometric score, not confidence probability",
            "candidate_acceptance": "never accepted as nozzle",
        },
        "source_manifest_sha256": source_manifest_sha256,
        "records": records,
    }
    (output / "reports.json").write_text(
        json.dumps(report, indent=2, sort_keys=True, allow_nan=False), encoding="utf-8"
    )
    missing_http = sum(
        1 for record in records if record.get("raw_http_evidence") == "MISSING"
    )
    text = f"# Archived pixel candidate inspection\n\nDevelopment-only, calibration-free candidate geometry. Red markers show every detected candidate; no marker is an accepted nozzle. No millimetres, freshness, accuracy, holdout, or machine eligibility claim. Full-frame and explicit ROI are both retained. {missing_http} records carry RAW_HTTP_EVIDENCE_MISSING.\n"
    (output / "SUMMARY.md").write_text(text, encoding="utf-8")
    (output / "SUMMARY.vi.md").write_text(
        f"# Kiểm tra candidate pixel từ archive\n\nChỉ dành cho phát triển, hình học candidate không calibration. Marker đỏ hiển thị mọi candidate; không marker nào là nozzle được chấp nhận. Không có millimet, freshness, accuracy, holdout hay điều kiện máy. Giữ cả full-frame và ROI explicit. {missing_http} record mang nhãn RAW_HTTP_EVIDENCE_MISSING.\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

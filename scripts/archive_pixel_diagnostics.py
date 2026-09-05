# pyright: reportUnknownMemberType=false, reportUnknownArgumentType=false, reportUnknownVariableType=false, reportUnknownLambdaType=false
"""Create calibration-free, read-only diagnostics for sealed JPEG manifests."""

from __future__ import annotations

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

FULL = (0, 0, 1280, 720)
ROI = (620, 230, 220, 240)


def stats(values: list[float]) -> dict[str, object]:
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
    median = statistics.median(values)
    return {
        "count": len(values),
        "mean": statistics.fmean(values),
        "median": median,
        "sample_sd": statistics.stdev(values) if len(values) > 1 else None,
        "mad": statistics.median([abs(v - median) for v in values]),
        "min": min(values),
        "max": max(values),
        "range": max(values) - min(values),
    }


def one(
    path: Path,
    source: str,
    level: int,
    frame: int,
    missing_http: bool,
    digest: str,
    out: Path,
) -> dict[str, object]:
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != digest:
        raise RuntimeError(f"source hash mismatch: {path}")
    image = cv2.imread(str(path), cv2.IMREAD_COLOR)
    record: dict[str, object] = {
        "source": source,
        "level_uint8": level,
        "frame": frame,
        "name": path.name,
        "source_sha256": digest,
        "bytes": len(raw),
        "uncertainty_mm": None,
        "detector_candidates": "UNSUPPORTED_WITHOUT_CALIBRATION",
        "machine_eligibility": False,
        "raw_http_evidence": "MISSING" if missing_http else "PRESENT_OR_NOT_CLAIMED",
    }
    if image is None or image.ndim != 3:
        record.update(
            {
                "status": "INVALID",
                "reason": "CORRUPT_INPUT",
                "full_frame": None,
                "development_roi": None,
            }
        )
        return record
    h, w = image.shape[:2]
    record["dimensions_px"] = [int(w), int(h)]

    def measure(x: int, y: int, rw: int, rh: int) -> dict[str, object]:
        if x < 0 or y < 0 or x + rw > w or y + rh > h:
            return {"status": "INVALID", "reason": "ROI_OUT_OF_BOUNDS"}
        crop: Any = image[y : y + rh, x : x + rw]
        g = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY).astype(np.float64)
        pixels = g.ravel().tolist()
        all_channels = crop.astype(np.uint16)
        clipped = int(np.count_nonzero(np.all(all_channels >= 250, axis=2)))
        underexposed = int(np.count_nonzero(np.all(all_channels <= 1, axis=2)))
        result = stats([float(v) for v in pixels])
        result.update(
            {
                "status": "VALID_PIXELS",
                "shape_score": None,
                "uncertainty_mm": None,
                "clipped_all_channels_ge_250_count": clipped,
                "clipped_all_channels_ge_250_ratio": clipped / (rw * rh),
                "underexposed_all_channels_le_1_count": underexposed,
                "underexposed_all_channels_le_1_ratio": underexposed / (rw * rh),
                "grayscale_saturation_ge_250_count": int(np.count_nonzero(g >= 250)),
                "grayscale_saturation_ge_250_ratio": float(np.mean(g >= 250)),
                "blur_score": float(cv2.Laplacian(g, cv2.CV_64F).var()),
                "contrast_std": float(g.std()),
                "width_px": rw,
                "height_px": rh,
            }
        )
        return result

    record.update(
        {
            "status": "WARNING",
            "reason": "UNHOMED_POSE_UNVERIFIED",
            "full_frame": measure(*FULL),
            "development_roi": measure(*ROI),
        }
    )
    return record


def main() -> int:
    roots = [
        Path(
            r"D:\Desktop\XYZKlipperTool-Captures\20260905T133241Z_VoronBed_camera-ring_T0-canary"
        ),
        Path(
            r"D:\Desktop\XYZKlipperTool-Captures\20260905T133902Z_VoronBed_camera-ring_T0-lowlight"
        ),
    ]
    output = Path(
        r"D:\Desktop\XYZKlipperTool-Captures\analysis_20260905T135000Z_T0_lighting"
    )
    output.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, object]] = []
    manifest_hashes: dict[str, str] = {}
    for root in roots:
        manifest_path = root / "reports" / "canary-manifest.json"
        manifest_hashes[str(root)] = hashlib.sha256(
            manifest_path.read_bytes()
        ).hexdigest()
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        missing = "lowlight" in root.name
        for item in data["frames"]:
            rel = item.get("file", item.get("raw"))
            path = root / Path(str(rel).replace("/", "\\"))
            records.append(
                one(
                    path,
                    root.name,
                    int(item.get("brightness_uint8", item.get("level", 0))),
                    int(item["frame"]),
                    missing,
                    str(item["sha256"]),
                    output,
                )
            )
    report = {
        "schema": "xyz-klipper-tool.archived-pixel-diagnostics.v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "python": sys.version,
        "platform": platform.platform(),
        "opencv": cv2.__version__,
        "parameters": {
            "full_frame_requested_px": FULL,
            "development_roi_requested_px": ROI,
            "color_clipping_definition": "all BGR channels >= 250",
            "grayscale_saturation_definition": "grayscale >= 250",
            "underexposure_definition": "all BGR channels <= 1",
            "calibration": "none",
            "machine_eligibility": False,
            "detector_candidates": "UNSUPPORTED_WITHOUT_CALIBRATION",
        },
        "source_manifest_sha256": manifest_hashes,
        "records": records,
    }
    (output / "reports.json").write_text(
        json.dumps(report, indent=2, sort_keys=True, allow_nan=False), encoding="utf-8"
    )
    summary = (
        "# Archived pixel diagnostics\n\nCalibration-free diagnostic only; no millimetre transform, nozzle-center claim, machine eligibility, or product brightness default. All 21 source frames are retained, including clipped and underexposed frames. Full-frame requested size is 1280x720; development ROI is x=620,y=230,width=220,height=240. Clipping metrics are named separately: all-channel >=250 versus grayscale >=250. Low-light frames are additionally marked RAW_HTTP_EVIDENCE_MISSING. Provisional visual observation only: L001 appears preferable for further review; this is not a firmware/product default.\n\nSource manifest hashes:\n"
        + "\n".join(f"- `{k}`: `{v}`" for k, v in manifest_hashes.items())
        + f"\n\nRecords: {len(records)}; no source files modified.\n"
    )
    (output / "SUMMARY.md").write_text(summary, encoding="utf-8")
    (output / "SUMMARY.vi.md").write_text(
        "# Diagnostic pixel archive\n\nChỉ là diagnostic không calibration; không có biến đổi millimet, claim tâm nozzle, điều kiện máy hoặc default độ sáng sản phẩm. Giữ đủ 21 frame, kể cả frame clipped và underexposed. Kích thước full-frame yêu cầu 1280x720; ROI phát triển là x=620,y=230,width=220,height=240. Metric clipping được đặt tên riêng: toàn bộ channel >=250 so với grayscale >=250. Các frame low-light được đánh dấu thêm RAW_HTTP_EVIDENCE_MISSING. Quan sát thị giác tạm thời: L001 có vẻ phù hợp hơn để xem tiếp; không phải firmware/product default.\n\nHash manifest nguồn:\n"
        + "\n".join(f"- `{k}`: `{v}`" for k, v in manifest_hashes.items())
        + f"\n\nSố record: {len(records)}; không sửa file nguồn.\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

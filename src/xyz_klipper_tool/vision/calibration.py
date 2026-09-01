"""Versioned camera calibration values and checksummed store contracts."""

import hashlib
import json
import math
import os
import shutil
import tempfile
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Protocol

from xyz_klipper_tool.domain.units import CoordinateFrame, Millimetres


@dataclass(frozen=True)
class Transform2D:
    """Finite image-to-relative-millimetre transform; never a machine origin.

    Scale is millimetres per pixel. Translation is relative to the explicitly
    supplied camera reference, not a historical station or machine coordinate.
    This value object has no I/O, blocking, or physical side effects.
    """

    mm_per_px_x: float
    mm_per_px_y: float
    relative_x_mm: Millimetres
    relative_y_mm: Millimetres
    input_frame: CoordinateFrame
    output_frame: CoordinateFrame

    def __post_init__(self) -> None:
        if (
            type(self.input_frame) is not CoordinateFrame
            or type(self.output_frame) is not CoordinateFrame
        ):
            raise ValueError("transform frames must be typed CoordinateFrame values")
        if (
            self.input_frame is not CoordinateFrame.CAMERA_IMAGE
            or self.output_frame is not CoordinateFrame.TOOL
        ):
            raise ValueError("transform must be CAMERA_IMAGE to TOOL relative frame")
        if not all(
            math.isfinite(float(x)) and float(x) > 0
            for x in (self.mm_per_px_x, self.mm_per_px_y)
        ):
            raise ValueError("transform must be finite and positive")


@dataclass(frozen=True)
class Calibration:
    """Immutable calibration identity, provenance, residual, and uncertainty."""

    calibration_id: str
    version: int
    camera_identity: str
    camera_fingerprint: str
    transform: Transform2D
    residual_px: float
    uncertainty_mm: Millimetres
    source_sha256: str
    created_at_utc: datetime

    def __post_init__(self) -> None:
        for value in (
            self.calibration_id,
            self.camera_identity,
            self.camera_fingerprint,
            self.source_sha256,
        ):
            if (
                type(value) is not str
                or not value.strip()
                or len(value) > 128
                or any(ord(c) < 32 for c in value)
            ):
                raise ValueError("calibration identity is required")
        if (
            "/" in self.calibration_id
            or "\\" in self.calibration_id
            or self.calibration_id in (".", "..")
            or len(self.source_sha256) != 64
            or any(c not in "0123456789abcdef" for c in self.source_sha256)
        ):
            raise ValueError("invalid calibration id or source hash")
        if self.uncertainty_mm.value_mm < 0:
            raise ValueError("uncertainty must not be negative")
        if type(self.version) is not int or self.version != 1:
            raise ValueError("unsupported calibration version")
        if not math.isfinite(self.residual_px) or self.residual_px < 0:
            raise ValueError("invalid residual")
        if type(
            self.created_at_utc
        ) is not datetime or self.created_at_utc.utcoffset() != timedelta(0):
            raise ValueError("created_at_utc must be UTC")


class CalibrationStore(Protocol):
    """Persistence boundary; implementations must be atomic and checksum validating."""

    def put(self, calibration: Calibration) -> None:
        """Persist one calibration without physical side effects."""
        ...

    def get(self, calibration_id: str) -> Calibration | None:
        """Read one calibration or return absent; malformed state fails closed."""
        ...


class JsonCalibrationStore:
    """Checksummed versioned calibration store confined to a caller directory."""

    def __init__(
        self,
        root: Path,
        max_file_bytes: int = 1_048_576,
        max_backups: int = 3,
        fault: Callable[[str], None] | None = None,
    ) -> None:
        if (
            type(max_file_bytes) is not int
            or not 1 <= max_file_bytes <= 16 * 1024 * 1024
        ):
            raise ValueError("invalid calibration file bound")
        if type(max_backups) is not int or not 0 <= max_backups <= 8:
            raise ValueError("invalid calibration backup bound")
        self.root = root
        self.max_file_bytes = max_file_bytes
        self.max_backups = max_backups
        self.fault = fault
        self.root.mkdir(parents=True, exist_ok=True)

    def _stage(self, name: str) -> None:
        if self.fault is not None:
            self.fault(name)

    def put(self, calibration: Calibration) -> None:
        """Atomically persist calibration metadata; no camera or printer I/O occurs."""
        payload = calibration_payload(calibration)
        envelope = {
            "schema_version": 1,
            "calibration": payload,
            "checksum": hashlib.sha256(
                json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
            ).hexdigest(),
        }
        root = self.root.resolve()
        path = (root / f"{calibration.calibration_id}.json").resolve()
        if path.parent != root:
            raise ValueError("calibration path escapes store root")
        fd, temp_name = tempfile.mkstemp(
            dir=self.root, prefix=".calibration-", suffix=".tmp"
        )
        try:
            self._stage("before_temp")
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(envelope, handle, sort_keys=True, separators=(",", ":"))
                if handle.tell() > self.max_file_bytes:
                    raise ValueError("calibration state exceeds bound")
                self._stage("after_temp_write")
                handle.flush()
                self._stage("after_flush")
                os.fsync(handle.fileno())
                self._stage("after_fsync")
            if path.exists() and self.max_backups:
                for index in range(self.max_backups, 0, -1):
                    old = root / f"{calibration.calibration_id}.json.bak{index}"
                    previous = (
                        root / f"{calibration.calibration_id}.json.bak{index - 1}"
                        if index > 1
                        else path
                    )
                    if previous.exists():
                        shutil.copy2(previous, old)
                        self._stage(f"backup_rotation_{index}")
            self._stage("before_current_replace")
            os.replace(temp_name, path)
            self._stage("after_current_replace")
        finally:
            Path(temp_name).unlink(missing_ok=True)

    def get(self, calibration_id: str) -> Calibration | None:
        """Read one checksummed calibration or fail closed on corruption."""
        if type(calibration_id) is not str or not calibration_id.strip():
            raise ValueError("calibration_id required")
        root = self.root.resolve()
        path = (root / f"{calibration_id}.json").resolve()
        if path.parent != root:
            raise ValueError("calibration path escapes store root")
        if not path.exists():
            return None
        return self._read_path(path, calibration_id)

    def _read_path(self, path: Path, calibration_id: str) -> Calibration:
        if path.stat().st_size > self.max_file_bytes:
            raise ValueError("calibration state exceeds bound")
        try:
            envelope = json.loads(path.read_text(encoding="utf-8"))
            if (
                envelope.get("schema_version") != 1
                or envelope.get("calibration", {}).get("calibration_id")
                != calibration_id
            ):
                raise ValueError("unsupported or mismatched calibration")
            payload = envelope["calibration"]
            expected = hashlib.sha256(
                json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
            ).hexdigest()
            if envelope.get("checksum") != expected:
                raise ValueError("calibration checksum mismatch")
            transform = payload["transform"]
            return Calibration(
                payload["calibration_id"],
                payload["version"],
                payload["camera_identity"],
                payload["camera_fingerprint"],
                Transform2D(
                    transform["mm_per_px_x"],
                    transform["mm_per_px_y"],
                    Millimetres(transform["relative_x_mm"]),
                    Millimetres(transform["relative_y_mm"]),
                    CoordinateFrame(transform["input_frame"]),
                    CoordinateFrame(transform["output_frame"]),
                ),
                payload["residual_px"],
                Millimetres(payload["uncertainty_mm"]),
                payload["source_sha256"],
                datetime.fromisoformat(payload["created_at_utc"]),
            )
        except (
            OSError,
            json.JSONDecodeError,
            KeyError,
            TypeError,
            ValueError,
            OverflowError,
        ) as exc:
            raise ValueError("corrupt calibration state") from exc

    def recover(self, calibration_id: str, backup_index: int = 1) -> Calibration:
        """Validate a named backup before atomic replacement; preserve backup on failure."""
        if type(calibration_id) is not str or not calibration_id.strip():
            raise ValueError("calibration_id required")
        if type(backup_index) is not int or not 1 <= backup_index <= self.max_backups:
            raise ValueError("invalid backup index")
        root = self.root.resolve()
        path = (root / f"{calibration_id}.json.bak{backup_index}").resolve()
        current = (root / f"{calibration_id}.json").resolve()
        if path.parent != root or current.parent != root:
            raise ValueError("calibration path escapes store root")
        if not path.exists() or path.stat().st_size > self.max_file_bytes:
            raise ValueError("requested calibration backup is absent")
        recovered = self._read_path(path, calibration_id)
        fd, temp_name = tempfile.mkstemp(
            dir=self.root, prefix=".recovery-", suffix=".tmp"
        )
        try:
            with os.fdopen(fd, "wb") as handle:
                handle.write(path.read_bytes())
                handle.flush()
                os.fsync(handle.fileno())
            self._stage("before_recovery_replace")
            os.replace(temp_name, current)
            self._stage("after_recovery_replace")
        finally:
            Path(temp_name).unlink(missing_ok=True)
        return recovered


def calibration_payload(calibration: Calibration) -> dict[str, Any]:
    """Return deterministic JSON-safe metadata without side effects or secrets."""
    return {
        "version": calibration.version,
        "calibration_id": calibration.calibration_id,
        "camera_identity": calibration.camera_identity,
        "camera_fingerprint": calibration.camera_fingerprint,
        "transform": {
            "mm_per_px_x": calibration.transform.mm_per_px_x,
            "mm_per_px_y": calibration.transform.mm_per_px_y,
            "relative_x_mm": calibration.transform.relative_x_mm.value_mm,
            "relative_y_mm": calibration.transform.relative_y_mm.value_mm,
            "input_frame": calibration.transform.input_frame.value,
            "output_frame": calibration.transform.output_frame.value,
        },
        "residual_px": calibration.residual_px,
        "uncertainty_mm": calibration.uncertainty_mm.value_mm,
        "source_sha256": calibration.source_sha256,
        "created_at_utc": calibration.created_at_utc.isoformat(),
    }


def calibration_digest(calibration: Calibration) -> str:
    """Compute a stable provenance digest over canonical calibration JSON."""
    return hashlib.sha256(
        json.dumps(
            calibration_payload(calibration), sort_keys=True, separators=(",", ":")
        ).encode()
    ).hexdigest()

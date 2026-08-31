"""Versioned atomic JSON station store with checksum and bounded backups."""

import hashlib
import json
import os
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, cast

from xyz_klipper_tool.domain.models import ProviderKind
from xyz_klipper_tool.domain.units import CoordinateFrame, Millimetres
from xyz_klipper_tool.stations.models import CurrentPose, StationRecord, StationType


class PersistenceError(ValueError):
    """Stable fail-closed persistence error for malformed, stale, or partial state."""


def _safe(value: str, name: str) -> str:
    if (
        type(value) is not str
        or not value.strip()
        or Path(value).name != value
        or value in (".", "..")
    ):
        raise PersistenceError(f"invalid {name}")
    return value


def _encode(record: StationRecord) -> dict[str, Any]:
    return {
        "name": record.name,
        "station_type": record.station_type.value,
        "provider": record.provider.value,
        "pose": {
            "x_mm": record.pose.x_mm.value_mm,
            "y_mm": record.pose.y_mm.value_mm,
            "z_mm": record.pose.z_mm.value_mm,
            "frame": record.pose.frame.value,
        },
        "safe_z_mm": record.safe_z_mm.value_mm,
        "revision": record.revision,
        "taught_at_utc": record.taught_at_utc.isoformat(),
        "configuration_fingerprint": record.configuration_fingerprint,
        "provenance": record.provenance,
    }


def _strict_text(value: object, name: str) -> str:
    if type(value) is not str or not value.strip():
        raise PersistenceError(f"invalid {name}")
    return value


def _strict_number(value: object, name: str) -> float:
    if type(value) not in (int, float):
        raise PersistenceError(f"invalid {name}")
    return float(cast(int | float, value))


def _decode(data: object, namespace: str, name: str) -> StationRecord:
    if not isinstance(data, dict):
        raise PersistenceError("unsupported or malformed station envelope")
    envelope = cast(dict[str, Any], data)
    if envelope.get("schema_version") != 1 or not isinstance(
        envelope.get("record"), dict
    ):
        raise PersistenceError("unsupported or malformed station envelope")
    raw = cast(dict[str, Any], envelope["record"])
    try:
        pose = cast(dict[str, Any], raw["pose"])
        record_name = _strict_text(raw["name"], "name")
        if record_name != name:
            raise PersistenceError("station path and record identity mismatch")
        timestamp = datetime.fromisoformat(
            _strict_text(raw["taught_at_utc"], "taught_at_utc")
        )
        if timestamp.tzinfo is None or timestamp.astimezone(timezone.utc) != timestamp:
            raise PersistenceError("taught_at_utc must be UTC")
        return StationRecord(
            record_name,
            StationType(raw["station_type"]),
            ProviderKind(raw["provider"]),
            CurrentPose(
                Millimetres(_strict_number(pose["x_mm"], "x_mm")),
                Millimetres(_strict_number(pose["y_mm"], "y_mm")),
                Millimetres(_strict_number(pose["z_mm"], "z_mm")),
                CoordinateFrame(pose["frame"]),
            ),
            Millimetres(_strict_number(raw["safe_z_mm"], "safe_z_mm")),
            _strict_text(raw["revision"], "revision"),
            timestamp,
            _strict_text(raw["configuration_fingerprint"], "configuration_fingerprint"),
            _strict_text(raw["provenance"], "provenance"),
        )
    except (KeyError, TypeError, ValueError, OverflowError) as exc:
        raise PersistenceError("malformed station record") from exc


class JsonStationStore:
    """Atomic bounded JSON store; only a caller-provided directory is touched and no network occurs."""

    def __init__(
        self, root: Path, max_backups: int = 3, fault_stage: str | None = None
    ) -> None:
        if max_backups < 0 or max_backups > 16:
            raise ValueError("max_backups out of bounds")
        self.root = root
        self.max_backups = max_backups
        self.fault_stage = fault_stage
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, namespace: str, name: str) -> Path:
        return self.root / _safe(namespace, "namespace") / f"{_safe(name, 'name')}.json"

    def get(self, namespace: str, name: str) -> StationRecord | None:
        """Read and validate current station state; malformed state raises without fallback silence."""
        path = self._path(namespace, name)
        if not path.exists():
            return None
        return self._read_path(path, namespace, name)

    def _read_path(self, path: Path, namespace: str, name: str) -> StationRecord:
        try:
            envelope = json.loads(path.read_text(encoding="utf-8"))
            payload = envelope["record"]
            expected = envelope["checksum"]
            actual = hashlib.sha256(
                json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
            ).hexdigest()
            if expected != actual:
                raise PersistenceError("checksum mismatch")
            return _decode(envelope, namespace, name)
        except PersistenceError:
            raise
        except (OSError, json.JSONDecodeError, KeyError, TypeError) as exc:
            raise PersistenceError("corrupt or truncated station state") from exc

    def recover(
        self, namespace: str, name: str, backup_index: int = 1
    ) -> StationRecord:
        """Explicitly validate and restore a selected backup; corrupt current is never silently swallowed."""
        if (
            type(backup_index) is not int
            or backup_index < 1
            or backup_index > self.max_backups
        ):
            raise PersistenceError("backup index out of bounds")
        backup = self._path(namespace, name).with_name(
            f"{_safe(name, 'name')}.json.bak{backup_index}"
        )
        record = self._read_path(backup, namespace, name)
        self.put(namespace, name, record)
        return record

    def put(self, namespace: str, name: str, value: object) -> None:
        """Atomically persist a validated station, retaining bounded backups and rejecting fault stages."""
        if not isinstance(value, StationRecord):
            raise PersistenceError("station record required")
        path = self._path(namespace, name)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = _encode(value)
        envelope = {
            "schema_version": 1,
            "record": payload,
            "checksum": hashlib.sha256(
                json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
            ).hexdigest(),
        }
        if self.fault_stage == "before_temp":
            raise OSError("injected before_temp")
        fd, temp_name = tempfile.mkstemp(
            prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
        )
        temp_path = Path(temp_name)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                handle.write(
                    json.dumps(envelope, sort_keys=True, separators=(",", ":"))
                )
                handle.flush()
                if self.fault_stage in ("after_flush", "before_replace"):
                    raise OSError(f"injected {self.fault_stage}")
                os.fsync(handle.fileno())
            if path.exists() and self.max_backups:
                if self.fault_stage == "backup":
                    raise OSError("injected backup")
                for index in range(self.max_backups - 1, 0, -1):
                    older = path.with_name(f"{path.name}.bak{index}")
                    newer = path.with_name(f"{path.name}.bak{index + 1}")
                    if older.exists():
                        os.replace(older, newer)
                shutil.copy2(path, path.with_name(f"{path.name}.bak1"))
            if self.fault_stage == "after_replace":
                os.replace(temp_path, path)
                raise OSError("injected after_replace")
            os.replace(temp_path, path)
        except OSError as exc:
            raise PersistenceError(str(exc)) from exc
        finally:
            temp_path.unlink(missing_ok=True)

    def remove(self, namespace: str, name: str) -> None:
        """Remove one station file; caller controls destructive confirmation."""
        self._path(namespace, name).unlink(missing_ok=True)

    def list(self, namespace: str) -> tuple[str, ...]:
        """List valid-looking station names in deterministic order without reading records."""
        directory = self.root / _safe(namespace, "namespace")
        if not directory.exists():
            return ()
        return tuple(
            sorted(
                path.stem
                for path in directory.glob("*.json")
                if not path.name.endswith(".bak1.json")
            )
        )

"""Versioned atomic JSON station store with checksum and bounded backups."""

import hashlib
import json
import os
import tempfile
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


def _decode(data: object) -> StationRecord:
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
        return StationRecord(
            str(raw["name"]),
            StationType(raw["station_type"]),
            ProviderKind(raw["provider"]),
            CurrentPose(
                Millimetres(pose["x_mm"]),
                Millimetres(pose["y_mm"]),
                Millimetres(pose["z_mm"]),
                CoordinateFrame(pose["frame"]),
            ),
            Millimetres(raw["safe_z_mm"]),
            str(raw["revision"]),
            __import__("datetime").datetime.fromisoformat(raw["taught_at_utc"]),
            str(raw["configuration_fingerprint"]),
            str(raw["provenance"]),
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
        try:
            envelope = json.loads(path.read_text(encoding="utf-8"))
            payload = envelope["record"]
            expected = envelope["checksum"]
            actual = hashlib.sha256(
                json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
            ).hexdigest()
            if expected != actual:
                raise PersistenceError("checksum mismatch")
            return _decode(envelope)
        except (OSError, json.JSONDecodeError, KeyError, TypeError) as exc:
            raise PersistenceError("corrupt or truncated station state") from exc

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
                backup = path.with_suffix(".json.bak1")
                if self.fault_stage == "backup":
                    raise OSError("injected backup")
                os.replace(path, backup)
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

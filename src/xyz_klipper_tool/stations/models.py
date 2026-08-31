"""Typed station data; coordinates are accepted only as explicit current-pose input."""

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

from xyz_klipper_tool.domain.models import ProviderKind
from xyz_klipper_tool.domain.units import Millimetres
from xyz_klipper_tool.ports import CurrentPose


def validate_text(value: str, name: str) -> str:
    """Validate non-empty textual station metadata without side effects."""
    if type(value) is not str or not value.strip():
        raise ValueError(f"{name} must be non-empty")
    return value


class StationType(str, Enum):
    """Provider namespace for station identity."""

    CAMERA = "camera"
    SWITCH_Z = "switch_z"
    CARTOGRAPHER_TOUCH_Z = "cartographer_touch_z"


@dataclass(frozen=True)
class StationRecord:
    """Immutable taught station with provenance; it does not prove travel safety."""

    name: str
    station_type: StationType
    provider: ProviderKind
    pose: CurrentPose
    safe_z_mm: Millimetres
    revision: str
    taught_at_utc: datetime
    configuration_fingerprint: str
    provenance: str

    def __post_init__(self) -> None:
        validate_text(self.name, "name")
        validate_text(self.revision, "revision")
        validate_text(self.configuration_fingerprint, "configuration_fingerprint")
        validate_text(self.provenance, "provenance")
        if (
            type(self.station_type) is not StationType
            or type(self.provider) is not ProviderKind
        ):
            raise ValueError("station type and provider must be typed enums")
        expected = {
            StationType.CAMERA: ProviderKind.CAMERA,
            StationType.SWITCH_Z: ProviderKind.SWITCH,
            StationType.CARTOGRAPHER_TOUCH_Z: ProviderKind.CARTOGRAPHER_TOUCH,
        }[self.station_type]
        if self.provider is not expected:
            raise ValueError("station namespace and provider mismatch")
        if (
            self.taught_at_utc.tzinfo is None
            or self.taught_at_utc.utcoffset() != timedelta(0)
        ):
            raise ValueError("taught_at_utc must be timezone-aware")

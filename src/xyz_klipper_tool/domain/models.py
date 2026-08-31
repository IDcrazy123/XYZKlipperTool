"""Validated identities, hierarchy, provider-specific results, and plans."""

from dataclasses import dataclass
from enum import Enum

from .units import CoordinateFrame, Millimetres, SignConvention, Vector2Mm


def _id(value: str, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be non-empty")
    return value


@dataclass(frozen=True)
class RunId:
    value: str

    def __post_init__(self):
        object.__setattr__(self, "value", _id(self.value, "run_id"))


@dataclass(frozen=True)
class OuterCycleId:
    value: str

    def __post_init__(self):
        object.__setattr__(self, "value", _id(self.value, "outer_cycle_id"))


@dataclass(frozen=True)
class ToolVisitId:
    value: str

    def __post_init__(self):
        object.__setattr__(self, "value", _id(self.value, "tool_visit_id"))


@dataclass(frozen=True)
class FrameSampleId:
    value: str

    def __post_init__(self):
        object.__setattr__(self, "value", _id(self.value, "sample_id"))


class Axis(str, Enum):
    X = "X"
    Y = "Y"
    Z = "Z"


class ProviderKind(str, Enum):
    SWITCH = "switch"
    CARTOGRAPHER_TOUCH = "cartographer_touch"


class ClaimState(str, Enum):
    OBSERVED = "OBSERVED"
    IMPLEMENTED = "IMPLEMENTED"
    PLANNED = "PLANNED"
    REQUIRES_HIL = "REQUIRES_HIL"


class Verdict(str, Enum):
    PASS = "PASS"
    WARNING = "WARNING"
    INVALID = "INVALID"


class ReasonCode(str, Enum):
    NONE = "NONE"
    INVALID_SAMPLE = "INVALID_SAMPLE"
    INSUFFICIENT_SAMPLES = "INSUFFICIENT_SAMPLES"
    STALE_FINGERPRINT = "STALE_FINGERPRINT"
    ROLLBACK_REQUIRED = "ROLLBACK_REQUIRED"
    PROVIDER_CONTRACT_UNVERIFIED = "PROVIDER_CONTRACT_UNVERIFIED"
    LIMIT_EXCEEDED = "LIMIT_EXCEEDED"


class Hierarchy(str, Enum):
    RUN = "run"
    OUTER_CYCLE = "outer_cycle"
    TOOL_VISIT = "tool_visit"
    FRAME_SAMPLE = "frame_sample"


@dataclass(frozen=True)
class MeasurementContext:
    run_id: RunId
    outer_cycle_id: OuterCycleId
    tool_visit_id: ToolVisitId
    sample_id: FrameSampleId
    station_revision: str
    configuration_fingerprint: str
    calibration_identity: str
    provider: ProviderKind
    axis: Axis
    hierarchy: Hierarchy = Hierarchy.FRAME_SAMPLE

    def __post_init__(self):
        for name in (
            "station_revision",
            "configuration_fingerprint",
            "calibration_identity",
        ):
            _id(getattr(self, name), name)


@dataclass(frozen=True)
class SwitchZMeasurementResult:
    context: MeasurementContext
    z_offset_mm: Millimetres
    frame: CoordinateFrame
    sign: SignConvention
    verdict: Verdict
    reason_code: ReasonCode
    claim_state: ClaimState = ClaimState.REQUIRES_HIL

    def __post_init__(self):
        if (
            self.context.provider is not ProviderKind.SWITCH
            or self.context.axis is not Axis.Z
        ):
            raise ValueError("switch result must be Z/switch")


@dataclass(frozen=True)
class CartographerTouchMeasurementResult:
    context: MeasurementContext
    z_offset_mm: Millimetres
    frame: CoordinateFrame
    sign: SignConvention
    verdict: Verdict
    reason_code: ReasonCode
    claim_state: ClaimState = ClaimState.REQUIRES_HIL

    def __post_init__(self):
        if (
            self.context.provider is not ProviderKind.CARTOGRAPHER_TOUCH
            or self.context.axis is not Axis.Z
        ):
            raise ValueError("Cartographer result must be Z/Cartographer")


@dataclass(frozen=True)
class CameraXYMeasurementResult:
    context: MeasurementContext
    offset_xy_mm: Vector2Mm
    frame: CoordinateFrame
    sign: SignConvention

    def __post_init__(self):
        if self.context.axis not in (Axis.X, Axis.Y):
            raise ValueError("camera result must be X or Y")


@dataclass(frozen=True)
class FreshnessExpectation:
    configuration_fingerprint: str
    station_revision: str


@dataclass(frozen=True)
class FreshnessResult:
    fresh: bool
    reason_code: ReasonCode


@dataclass(frozen=True)
class ApplyPlan:
    run_id: RunId
    configuration_fingerprint: str
    preview_only: bool = True

    def __post_init__(self):
        if not self.preview_only:
            raise ValueError("apply plan is preview-only in pure domain")


@dataclass(frozen=True)
class RollbackEntry:
    tool_id: str
    previous_offset_xy_mm: Vector2Mm


@dataclass(frozen=True)
class RollbackPlan:
    entries: tuple[RollbackEntry, ...]
    source_run_id: RunId

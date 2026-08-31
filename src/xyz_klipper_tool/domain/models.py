"""Validated identities, hierarchy, provider-specific results, and plans."""

from dataclasses import dataclass
from enum import Enum

from .units import CoordinateFrame, Millimetres, SignConvention, Vector2Mm


def _id(value: str, name: str) -> str:
    value_object: object = value
    if type(value_object) is not str or not value_object.strip():
        raise ValueError(f"{name} must be non-empty")
    return value


@dataclass(frozen=True)
class RunId:
    """Non-empty run identity; no I/O or machine action is performed."""

    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _id(self.value, "run_id"))


@dataclass(frozen=True)
class OuterCycleId:
    """Non-empty independent outer pickup-cycle identity."""

    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _id(self.value, "outer_cycle_id"))


@dataclass(frozen=True)
class ToolVisitId:
    """Non-empty tool visit identity within a run and cycle."""

    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _id(self.value, "tool_visit_id"))


@dataclass(frozen=True)
class FrameSampleId:
    """Non-empty frame/sample identity for one observation."""

    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _id(self.value, "sample_id"))


@dataclass(frozen=True)
class ToolId:
    """Non-empty stable tool identity; it is not a numeric slot default."""

    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _id(self.value, "tool_id"))


class Axis(str, Enum):
    """Measured axis; X/Y are camera and Z is a declared Z provider."""

    X = "X"
    Y = "Y"
    Z = "Z"


class ProviderKind(str, Enum):
    """Typed provider family separating camera from the two Z providers."""

    CAMERA = "camera"
    SWITCH = "switch"
    CARTOGRAPHER_TOUCH = "cartographer_touch"


class ClaimState(str, Enum):
    """Evidence claim maturity; REQUIRES_HIL is not a safety assertion."""

    OBSERVED = "OBSERVED"
    IMPLEMENTED = "IMPLEMENTED"
    PLANNED = "PLANNED"
    REQUIRES_HIL = "REQUIRES_HIL"


class Verdict(str, Enum):
    """Domain result verdict for downstream report/apply gating."""

    PASS = "PASS"
    WARNING = "WARNING"
    INVALID = "INVALID"


class ReasonCode(str, Enum):
    """Stable fail-closed reason code; values carry no side effects."""

    NONE = "NONE"
    INVALID_SAMPLE = "INVALID_SAMPLE"
    WARNING_SAMPLE = "WARNING_SAMPLE"
    OUTLIER_REJECTED = "OUTLIER_REJECTED"
    INSUFFICIENT_SAMPLES = "INSUFFICIENT_SAMPLES"
    STALE_FINGERPRINT = "STALE_FINGERPRINT"
    ROLLBACK_REQUIRED = "ROLLBACK_REQUIRED"
    PROVIDER_CONTRACT_UNVERIFIED = "PROVIDER_CONTRACT_UNVERIFIED"
    LIMIT_EXCEEDED = "LIMIT_EXCEEDED"


class Hierarchy(str, Enum):
    """Aggregation hierarchy level retained with every observation."""

    RUN = "run"
    OUTER_CYCLE = "outer_cycle"
    TOOL_VISIT = "tool_visit"
    FRAME_SAMPLE = "frame_sample"


@dataclass(frozen=True)
class MeasurementContext:
    """Complete identity/provider/axis context; validation is pure and non-blocking."""

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

    def __post_init__(self) -> None:
        for name in (
            "station_revision",
            "configuration_fingerprint",
            "calibration_identity",
        ):
            _id(getattr(self, name), name)
        provider_object: object = self.provider
        axis_object: object = self.axis
        if type(provider_object) is not ProviderKind or type(axis_object) is not Axis:
            raise ValueError("provider and axis must be typed enums")
        if self.provider is ProviderKind.CAMERA and self.axis not in (Axis.X, Axis.Y):
            raise ValueError("camera context must use X or Y")
        if (
            self.provider in (ProviderKind.SWITCH, ProviderKind.CARTOGRAPHER_TOUCH)
            and self.axis is not Axis.Z
        ):
            raise ValueError("Z provider context must use Z")


@dataclass(frozen=True)
class SwitchZMeasurementResult:
    """Pure switch Z result; mm/frame/sign are data only and never block or write."""

    context: MeasurementContext
    z_offset_mm: Millimetres
    frame: CoordinateFrame
    sign: SignConvention
    verdict: Verdict
    reason_code: ReasonCode
    claim_state: ClaimState = ClaimState.REQUIRES_HIL

    def __post_init__(self) -> None:
        if (
            self.context.provider is not ProviderKind.SWITCH
            or self.context.axis is not Axis.Z
        ):
            raise ValueError("switch result must be Z/switch")


@dataclass(frozen=True)
class CartographerTouchMeasurementResult:
    """Pure Cartographer Touch Z result; physical compatibility remains REQUIRES_HIL."""

    context: MeasurementContext
    z_offset_mm: Millimetres
    frame: CoordinateFrame
    sign: SignConvention
    verdict: Verdict
    reason_code: ReasonCode
    claim_state: ClaimState = ClaimState.REQUIRES_HIL

    def __post_init__(self) -> None:
        if (
            self.context.provider is not ProviderKind.CARTOGRAPHER_TOUCH
            or self.context.axis is not Axis.Z
        ):
            raise ValueError("Cartographer result must be Z/Cartographer")


@dataclass(frozen=True)
class CameraXYMeasurementResult:
    """Pure camera X/Y result requiring a camera provider and coherent metadata."""

    context: MeasurementContext
    offset_xy_mm: Vector2Mm
    frame: CoordinateFrame
    sign: SignConvention

    def __post_init__(self) -> None:
        if (
            self.context.provider is not ProviderKind.CAMERA
            or self.context.axis not in (Axis.X, Axis.Y)
        ):
            raise ValueError("camera result must be CAMERA provider and X or Y")
        if (
            self.offset_xy_mm.frame is not self.frame
            or self.offset_xy_mm.sign is not self.sign
        ):
            raise ValueError("camera result frame/sign must match offset vector")


@dataclass(frozen=True)
class FreshnessExpectation:
    """Expected non-empty configuration/station identities for a later non-I/O check."""

    configuration_fingerprint: str
    station_revision: str

    def __post_init__(self) -> None:
        _id(self.configuration_fingerprint, "configuration_fingerprint")
        _id(self.station_revision, "station_revision")


@dataclass(frozen=True)
class FreshnessResult:
    """Typed freshness decision with no I/O or blocking behavior."""

    fresh: bool
    reason_code: ReasonCode

    def __post_init__(self) -> None:
        if (self.fresh and self.reason_code is not ReasonCode.NONE) or (
            not self.fresh and self.reason_code is ReasonCode.NONE
        ):
            raise ValueError("freshness and reason_code are incoherent")


@dataclass(frozen=True)
class ApplyPlan:
    """Preview-only immutable transaction data; it has no writer side effect."""

    run_id: RunId
    configuration_fingerprint: str
    preview_only: bool = True

    def __post_init__(self) -> None:
        _id(self.configuration_fingerprint, "configuration_fingerprint")
        if not self.preview_only:
            raise ValueError("apply plan is preview-only in pure domain")


@dataclass(frozen=True)
class RollbackEntry:
    """Immutable tool correction snapshot; no I/O, blocking, or writer side effect."""

    tool_id: str
    previous_offset_xy_mm: Vector2Mm

    def __post_init__(self) -> None:
        _id(self.tool_id, "tool_id")


@dataclass(frozen=True)
class RollbackPlan:
    """Immutable rollback data whose execution belongs outside the pure domain."""

    entries: tuple[RollbackEntry, ...]
    source_run_id: RunId

"""Identity, provider, verdict, and side-effect-free transaction models."""

from dataclasses import dataclass
from enum import Enum

from .units import Millimetres, Vector2Mm


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


@dataclass(frozen=True)
class RunId:
    value: str


@dataclass(frozen=True)
class OuterCycleId:
    value: str


@dataclass(frozen=True)
class ToolVisitId:
    value: str


@dataclass(frozen=True)
class FrameSampleId:
    value: str


@dataclass(frozen=True)
class SwitchMeasurementResult:
    run_id: RunId
    tool_visit_id: ToolVisitId
    offset_xy_mm: Vector2Mm
    verdict: Verdict
    reason_code: ReasonCode
    claim_state: ClaimState = ClaimState.REQUIRES_HIL


@dataclass(frozen=True)
class CartographerTouchMeasurementResult:
    run_id: RunId
    tool_visit_id: ToolVisitId
    z_offset_mm: Millimetres
    verdict: Verdict
    reason_code: ReasonCode
    claim_state: ClaimState = ClaimState.REQUIRES_HIL


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


@dataclass(frozen=True)
class RollbackEntry:
    tool_id: str
    previous_offset_xy_mm: Vector2Mm


@dataclass(frozen=True)
class RollbackPlan:
    entries: tuple[RollbackEntry, ...]
    source_run_id: RunId

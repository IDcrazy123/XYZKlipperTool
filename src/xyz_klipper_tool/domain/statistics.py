"""Raw-preserving deterministic statistics with explicit rejection reasons."""

import math
from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum
from statistics import fmean, median, stdev

from .models import (
    Axis,
    FrameSampleId,
    Hierarchy,
    OuterCycleId,
    ProviderKind,
    ReasonCode,
    RunId,
    ToolId,
    ToolVisitId,
    Verdict,
)
from .units import Millimetres


class SampleStatus(str, Enum):
    """Raw sample quality state; INVALID values never enter estimators."""

    VALID = "VALID"
    INVALID = "INVALID"
    WARNING = "WARNING"


class AcceptanceStatus(str, Enum):
    """Explicit accepted/rejected status for a derived rejection record."""

    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


class SampleSufficiency(str, Enum):
    """Typed estimator sufficiency result for n=0/1 versus n>=2."""

    INSUFFICIENT_SAMPLES = "INSUFFICIENT_SAMPLES"
    SUFFICIENT = "SUFFICIENT"


@dataclass(frozen=True)
class Observation:
    """One finite sample with complete run→cycle→visit→sample provenance."""

    run_id: RunId
    tool_id: ToolId
    outer_cycle_id: OuterCycleId
    tool_visit_id: ToolVisitId
    sample_id: FrameSampleId
    station_revision: str
    configuration_fingerprint: str
    calibration_identity: str
    provider: ProviderKind
    axis: Axis
    hierarchy: Hierarchy
    value_mm: Millimetres
    status: SampleStatus = SampleStatus.VALID

    def __post_init__(self) -> None:
        for name in (
            "station_revision",
            "configuration_fingerprint",
            "calibration_identity",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be non-empty")
        for name, expected in (
            ("run_id", RunId),
            ("tool_id", ToolId),
            ("outer_cycle_id", OuterCycleId),
            ("tool_visit_id", ToolVisitId),
            ("sample_id", FrameSampleId),
            ("value_mm", Millimetres),
        ):
            if not isinstance(getattr(self, name), expected):
                raise ValueError(f"{name} must be typed")  # noqa: TRY004
        provider_object: object = self.provider
        axis_object: object = self.axis
        hierarchy_object: object = self.hierarchy
        status_object: object = self.status
        if type(provider_object) is not ProviderKind or type(axis_object) is not Axis:
            raise ValueError("provider and axis must be typed enums")
        if type(hierarchy_object) is not Hierarchy:
            raise ValueError("hierarchy must be a typed enum")
        if type(status_object) is not SampleStatus:
            raise ValueError("status must be a typed enum")


@dataclass(frozen=True)
class StatisticSeriesKey:
    """Typed aggregation key; outer-cycle observations aggregate only within this key."""

    run_id: RunId
    tool_id: ToolId
    provider: ProviderKind
    axis: Axis
    hierarchy: Hierarchy
    station_revision: str
    configuration_fingerprint: str
    calibration_identity: str

    def __post_init__(self) -> None:
        for value, name in (
            (self.station_revision, "station_revision"),
            (self.configuration_fingerprint, "configuration_fingerprint"),
            (self.calibration_identity, "calibration_identity"),
        ):
            value_object: object = value
            if type(value_object) is not str or not value_object.strip():
                raise ValueError(f"{name} must be non-empty")
        if (
            type(self.run_id) is not RunId
            or type(self.tool_id) is not ToolId
            or type(self.provider) is not ProviderKind
            or type(self.axis) is not Axis
            or type(self.hierarchy) is not Hierarchy
        ):
            raise ValueError("series key fields must be typed")


@dataclass(frozen=True)
class ReferencePair:
    """Typed reference-start and reference-return values used for drift."""

    start_mm: Millimetres
    return_mm: Millimetres


@dataclass(frozen=True)
class OutlierPolicy:
    """Declared estimator policy; automatic threshold rejection requires a positive finite threshold."""

    name: str = "report_only_no_automatic_rejection"
    threshold_mm: float | None = None
    automatic_rejection: bool = False

    def __post_init__(self) -> None:
        if self.automatic_rejection and (
            self.threshold_mm is None
            or not math.isfinite(self.threshold_mm)
            or self.threshold_mm <= 0
        ):
            raise ValueError("automatic outlier threshold must be positive and finite")


DEFAULT_OUTLIER_POLICY = OutlierPolicy()


@dataclass(frozen=True)
class Rejection:
    """Immutable derived rejection with accepted/rejected state and reason."""

    sample_id: FrameSampleId
    status: AcceptanceStatus
    reason_code: ReasonCode


@dataclass(frozen=True)
class Summary:
    """Complete estimator summary in millimetres; uncertainty uses documented MAD scale."""

    values_mm: tuple[float, ...]
    mean_mm: float | None
    median_mm: float | None
    sample_sd_mm: float | None
    mad_mm: float | None
    minimum_mm: float | None
    maximum_mm: float | None
    range_mm: float | None
    uncertainty_mm: float | None
    sufficiency: SampleSufficiency


@dataclass(frozen=True)
class StatisticResult:
    """Raw-preserving result with separate unfiltered/filtered summaries and verdict."""

    raw_observations: tuple[Observation, ...]
    unfiltered: Summary
    filtered: Summary
    total_count: int
    valid_count: int
    invalid_count: int
    warning_count: int
    rejected_count: int
    rejections: tuple[Rejection, ...]
    reference_drift_mm: Millimetres | None
    verdict: Verdict
    reason_code: ReasonCode
    outlier_policy: OutlierPolicy


def _summary(values: tuple[float, ...]) -> Summary:
    n = len(values)
    mean = fmean(values) if n else None
    med = median(values) if n else None
    mad = (
        median(tuple(abs(value - med) for value in values))
        if n and med is not None
        else None
    )
    return Summary(
        values,
        mean,
        med,
        stdev(values) if n >= 2 else None,
        mad,
        min(values) if n else None,
        max(values) if n else None,
        max(values) - min(values) if n else None,
        (1.4826 * mad / math.sqrt(n)) if mad is not None else None,
        SampleSufficiency.SUFFICIENT
        if n >= 2
        else SampleSufficiency.INSUFFICIENT_SAMPLES,
    )


def summarize(
    observations: Iterable[Observation],
    policy: OutlierPolicy = DEFAULT_OUTLIER_POLICY,
    reference: ReferencePair | None = None,
    limit_mm: float | None = None,
) -> StatisticResult:
    """Summarize one homogeneous series; mixed provider/axis fails closed."""
    raw = tuple(observations)
    if raw:
        first = raw[0]
        series_key = StatisticSeriesKey(
            first.run_id,
            first.tool_id,
            first.provider,
            first.axis,
            first.hierarchy,
            first.station_revision,
            first.configuration_fingerprint,
            first.calibration_identity,
        )
        for item in raw[1:]:
            item_key = StatisticSeriesKey(
                item.run_id,
                item.tool_id,
                item.provider,
                item.axis,
                item.hierarchy,
                item.station_revision,
                item.configuration_fingerprint,
                item.calibration_identity,
            )
            if item_key != series_key:
                raise ValueError(
                    "series cannot mix run, tool, provider, axis, hierarchy, or identity"
                )
    valid = tuple(item for item in raw if item.status is not SampleStatus.INVALID)
    unfiltered_values = tuple(sorted(item.value_mm.value_mm for item in valid))
    rejections: list[Rejection] = []
    filtered: list[float] = []
    centre = median(unfiltered_values) if unfiltered_values else None
    for item in valid:
        reject = (
            policy.automatic_rejection
            and centre is not None
            and policy.threshold_mm is not None
            and abs(item.value_mm.value_mm - centre) > policy.threshold_mm
        )
        if reject:
            rejections.append(
                Rejection(
                    item.sample_id,
                    AcceptanceStatus.REJECTED,
                    ReasonCode.OUTLIER_REJECTED,
                )
            )
        else:
            filtered.append(item.value_mm.value_mm)
    filtered_values = tuple(sorted(filtered))
    if len(filtered_values) < 2:
        reason, verdict = ReasonCode.INSUFFICIENT_SAMPLES, Verdict.WARNING
    elif any(item.status is SampleStatus.INVALID for item in raw):
        reason, verdict = ReasonCode.INVALID_SAMPLE, Verdict.INVALID
    elif any(item.status is SampleStatus.WARNING for item in raw):
        reason, verdict = ReasonCode.WARNING_SAMPLE, Verdict.WARNING
    else:
        reason, verdict = ReasonCode.NONE, Verdict.PASS
    if limit_mm is not None and (not math.isfinite(limit_mm) or limit_mm < 0):
        raise ValueError("limit_mm must be finite and non-negative")
    if (
        limit_mm is not None
        and filtered_values
        and max(abs(value) for value in filtered_values) > limit_mm
    ):
        verdict, reason = Verdict.INVALID, ReasonCode.LIMIT_EXCEEDED
    drift = (
        Millimetres(reference.return_mm.value_mm - reference.start_mm.value_mm)
        if reference
        else None
    )
    return StatisticResult(
        raw,
        _summary(unfiltered_values),
        _summary(filtered_values),
        len(raw),
        len(valid),
        sum(item.status is SampleStatus.INVALID for item in raw),
        sum(item.status is SampleStatus.WARNING for item in raw),
        len(rejections),
        tuple(rejections),
        drift,
        verdict,
        reason,
        policy,
    )

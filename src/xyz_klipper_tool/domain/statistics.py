"""Raw-preserving deterministic statistics with explicit rejection reasons."""

import math
from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum
from statistics import fmean, median, stdev

from .models import Axis, ProviderKind, ReasonCode, Verdict
from .units import Millimetres


class SampleStatus(str, Enum):
    VALID = "VALID"
    INVALID = "INVALID"
    WARNING = "WARNING"


class AcceptanceStatus(str, Enum):
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


class SampleSufficiency(str, Enum):
    INSUFFICIENT_SAMPLES = "INSUFFICIENT_SAMPLES"
    SUFFICIENT = "SUFFICIENT"


@dataclass(frozen=True)
class Observation:
    """One finite sample with complete run→cycle→visit→sample provenance."""

    run_id: str
    outer_cycle_id: str
    tool_visit_id: str
    sample_id: str
    station_revision: str
    configuration_fingerprint: str
    calibration_identity: str
    provider: ProviderKind
    axis: Axis
    value_mm: Millimetres
    status: SampleStatus = SampleStatus.VALID

    def __post_init__(self) -> None:
        for name in (
            "run_id",
            "outer_cycle_id",
            "tool_visit_id",
            "sample_id",
            "station_revision",
            "configuration_fingerprint",
            "calibration_identity",
        ):
            if (
                not isinstance(getattr(self, name), str)
                or not getattr(self, name).strip()
            ):
                raise ValueError(f"{name} must be non-empty")


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
    sample_id: str
    status: AcceptanceStatus
    reason_code: ReasonCode


@dataclass(frozen=True)
class Summary:
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
    if raw and len({(item.provider, item.axis) for item in raw}) != 1:
        raise ValueError("series cannot mix provider or axis")
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
                    item.sample_id, AcceptanceStatus.REJECTED, ReasonCode.LIMIT_EXCEEDED
                )
            )
        else:
            filtered.append(item.value_mm.value_mm)
    filtered_values = tuple(sorted(filtered))
    reason = (
        ReasonCode.INSUFFICIENT_SAMPLES if len(filtered_values) < 2 else ReasonCode.NONE
    )
    verdict = (
        Verdict.WARNING if reason is ReasonCode.INSUFFICIENT_SAMPLES else Verdict.PASS
    )
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

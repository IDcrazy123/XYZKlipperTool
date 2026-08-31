"""Deterministic, raw-preserving robust statistics."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum
from statistics import fmean, median, stdev


class SampleStatus(str, Enum):
    VALID = "VALID"
    INVALID = "INVALID"
    WARNING = "WARNING"


class AcceptanceStatus(str, Enum):
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


@dataclass(frozen=True)
class Observation:
    sample_id: str
    value_mm: float
    status: SampleStatus = SampleStatus.VALID
    reason_code: str | None = None
    acceptance: AcceptanceStatus = AcceptanceStatus.ACCEPTED


@dataclass(frozen=True)
class OutlierPolicy:
    """Policy is declared data; invalid samples are always excluded from estimators."""

    name: str = "report_only_no_automatic_rejection"
    threshold_mm: float | None = None
    automatic_rejection: bool = False


DEFAULT_OUTLIER_POLICY = OutlierPolicy()


@dataclass(frozen=True)
class StatisticSummary:
    raw_observations: tuple[Observation, ...]
    ordered_valid_values_mm: tuple[float, ...]
    filtered_values_mm: tuple[float, ...]
    total_count: int
    valid_count: int
    invalid_count: int
    warning_count: int
    rejected_count: int
    mean_mm: float | None
    median_mm: float | None
    sample_sd_mm: float | None
    mad_mm: float | None
    minimum_mm: float | None
    maximum_mm: float | None
    range_mm: float | None
    uncertainty_mm: float | None
    drift_mm: float | None
    insufficient_samples: bool
    outlier_policy: OutlierPolicy


def summarize(
    observations: Iterable[Observation], policy: OutlierPolicy = DEFAULT_OUTLIER_POLICY
) -> StatisticSummary:
    raw = tuple(observations)
    valid = tuple(
        o.value_mm
        for o in raw
        if o.status is not SampleStatus.INVALID
        and o.acceptance is AcceptanceStatus.ACCEPTED
    )
    ordered = tuple(sorted(valid))
    filtered = ordered
    if policy.automatic_rejection and policy.threshold_mm is not None and ordered:
        centre = median(ordered)
        filtered = tuple(v for v in ordered if abs(v - centre) <= policy.threshold_mm)
    n = len(filtered)
    mean = fmean(filtered) if n else None
    med = median(filtered) if n else None
    sd = stdev(filtered) if n >= 2 else None
    mad = (
        median(tuple(abs(v - med) for v in filtered)) if n and med is not None else None
    )
    uncertainty = (1.4826 * mad / (n**0.5)) if mad is not None and n else None
    warning = sum(o.status is SampleStatus.WARNING for o in raw)
    rejected = sum(o.acceptance is AcceptanceStatus.REJECTED for o in raw)
    drift = (
        (raw[-1].value_mm - raw[0].value_mm)
        if len(raw) >= 2
        and all(o.status is not SampleStatus.INVALID for o in (raw[0], raw[-1]))
        else None
    )
    return StatisticSummary(
        raw,
        ordered,
        filtered,
        len(raw),
        len(valid),
        sum(o.status is SampleStatus.INVALID for o in raw),
        warning,
        rejected,
        mean,
        med,
        sd,
        mad,
        min(filtered) if n else None,
        max(filtered) if n else None,
        (max(filtered) - min(filtered)) if n else None,
        uncertainty,
        drift,
        n < 2,
        policy,
    )

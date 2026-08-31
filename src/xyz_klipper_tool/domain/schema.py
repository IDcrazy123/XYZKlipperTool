"""Strict in-memory v1 codecs; no filesystem or network side effects."""

import json
from typing import Any, cast

from .models import (
    Axis,
    CartographerTouchMeasurementResult,
    ClaimState,
    FrameSampleId,
    MeasurementContext,
    OuterCycleId,
    ProviderKind,
    ReasonCode,
    RunId,
    SwitchZMeasurementResult,
    ToolVisitId,
    Verdict,
)
from .units import CoordinateFrame, Millimetres, SignConvention

SCHEMA_VERSION = 1


class SchemaVersionError(ValueError):
    pass


class SchemaPayloadError(ValueError):
    pass


def _read(payload: str) -> dict[str, Any]:
    try:
        raw: Any = json.loads(payload)
    except (TypeError, json.JSONDecodeError) as exc:
        raise SchemaPayloadError("malformed JSON") from exc
    if not isinstance(raw, dict):
        raise SchemaPayloadError("payload must be an object")
    data = cast(dict[str, Any], raw)
    if data.get("schema_version") != SCHEMA_VERSION:
        raise SchemaVersionError("unsupported or missing schema_version")
    return data


def _context(data: dict[str, Any], provider: ProviderKind) -> MeasurementContext:
    required = (
        "run_id",
        "outer_cycle_id",
        "tool_visit_id",
        "sample_id",
        "station_revision",
        "configuration_fingerprint",
        "calibration_identity",
        "axis",
    )
    if any(key not in data for key in required):
        raise SchemaPayloadError("missing context field")
    if data["provider"] != provider.value:
        raise SchemaPayloadError("provider mismatch")
    return MeasurementContext(
        RunId(data["run_id"]),
        OuterCycleId(data["outer_cycle_id"]),
        ToolVisitId(data["tool_visit_id"]),
        FrameSampleId(data["sample_id"]),
        data["station_revision"],
        data["configuration_fingerprint"],
        data["calibration_identity"],
        provider,
        Axis(data["axis"]),
    )


def _base(result: Any) -> dict[str, Any]:
    c = result.context
    return {
        "schema_version": SCHEMA_VERSION,
        "run_id": c.run_id.value,
        "outer_cycle_id": c.outer_cycle_id.value,
        "tool_visit_id": c.tool_visit_id.value,
        "sample_id": c.sample_id.value,
        "station_revision": c.station_revision,
        "configuration_fingerprint": c.configuration_fingerprint,
        "calibration_identity": c.calibration_identity,
        "provider": c.provider.value,
        "axis": c.axis.value,
        "frame": result.frame.value,
        "sign": result.sign.value,
        "verdict": result.verdict.value,
        "reason_code": result.reason_code.value,
        "claim_state": result.claim_state.value,
    }


def encode_switch_z_result(result: SwitchZMeasurementResult) -> str:
    data = _base(result)
    data["z_offset_mm"] = result.z_offset_mm.value_mm
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


def encode_cartographer_result(result: CartographerTouchMeasurementResult) -> str:
    data = _base(result)
    data["z_offset_mm"] = result.z_offset_mm.value_mm
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


def _decode(
    data: dict[str, Any], provider: ProviderKind
) -> tuple[
    MeasurementContext,
    Millimetres,
    CoordinateFrame,
    SignConvention,
    Verdict,
    ReasonCode,
    ClaimState,
]:
    context = _context(data, provider)
    for key in (
        "z_offset_mm",
        "frame",
        "sign",
        "verdict",
        "reason_code",
        "claim_state",
    ):
        if key not in data:
            raise SchemaPayloadError("missing result field")
    return (
        context,
        Millimetres(data["z_offset_mm"]),
        CoordinateFrame(data["frame"]),
        SignConvention(data["sign"]),
        Verdict(data["verdict"]),
        ReasonCode(data["reason_code"]),
        ClaimState(data["claim_state"]),
    )


def decode_switch_z_result(payload: str) -> SwitchZMeasurementResult:
    return SwitchZMeasurementResult(*_decode(_read(payload), ProviderKind.SWITCH))


def decode_cartographer_result(payload: str) -> CartographerTouchMeasurementResult:
    return CartographerTouchMeasurementResult(
        *_decode(_read(payload), ProviderKind.CARTOGRAPHER_TOUCH)
    )

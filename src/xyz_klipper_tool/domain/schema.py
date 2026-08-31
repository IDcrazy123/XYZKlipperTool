"""In-memory versioned schema codec; it performs no filesystem or network I/O."""

import json
from typing import Any

from .models import (
    ClaimState,
    ReasonCode,
    RunId,
    SwitchMeasurementResult,
    ToolVisitId,
    Verdict,
)
from .units import Vector2Mm

SCHEMA_VERSION = 1


class SchemaVersionError(ValueError):
    pass


def encode_switch_result(result: SwitchMeasurementResult) -> str:
    return json.dumps(
        {
            "schema_version": SCHEMA_VERSION,
            "run_id": result.run_id.value,
            "tool_visit_id": result.tool_visit_id.value,
            "x_mm": result.offset_xy_mm.x_mm,
            "y_mm": result.offset_xy_mm.y_mm,
            "verdict": result.verdict.value,
            "reason_code": result.reason_code.value,
            "claim_state": result.claim_state.value,
        },
        sort_keys=True,
        separators=(",", ":"),
    )


def decode_switch_result(payload: str) -> SwitchMeasurementResult:
    data: dict[str, Any] = json.loads(payload)
    version = data.get("schema_version", 1)
    if version != SCHEMA_VERSION:
        raise SchemaVersionError(f"unsupported schema_version: {version}")
    return SwitchMeasurementResult(
        RunId(str(data["run_id"])),
        ToolVisitId(str(data["tool_visit_id"])),
        Vector2Mm(float(data["x_mm"]), float(data["y_mm"])),
        Verdict(data["verdict"]),
        ReasonCode(data["reason_code"]),
        ClaimState(data.get("claim_state", ClaimState.REQUIRES_HIL.value)),
    )

"""Pure domain contracts for XYZ Klipper Tool."""

from .models import (
    Axis,
    CameraXYMeasurementResult,
    CartographerTouchMeasurementResult,
    ClaimState,
    MeasurementContext,
    ProviderKind,
    ReasonCode,
    SwitchZMeasurementResult,
)
from .state_machine import RunState, RunStateMachine, TransitionResult
from .statistics import (
    Observation,
    OutlierPolicy,
    ReferencePair,
    SampleSufficiency,
    StatisticResult,
    summarize,
)
from .units import (
    Celsius,
    CoordinateFrame,
    Millimetres,
    PixelScale,
    PixelVector2,
    Seconds,
    SignConvention,
    Vector2Mm,
)

__all__ = [
    "Axis",
    "CameraXYMeasurementResult",
    "CartographerTouchMeasurementResult",
    "Celsius",
    "ClaimState",
    "CoordinateFrame",
    "MeasurementContext",
    "Millimetres",
    "Observation",
    "OutlierPolicy",
    "PixelScale",
    "PixelVector2",
    "ProviderKind",
    "ReasonCode",
    "ReferencePair",
    "RunState",
    "RunStateMachine",
    "SampleSufficiency",
    "Seconds",
    "SignConvention",
    "StatisticResult",
    "SwitchZMeasurementResult",
    "TransitionResult",
    "Vector2Mm",
    "summarize",
]

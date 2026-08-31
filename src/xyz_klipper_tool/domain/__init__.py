"""Pure domain contracts for XYZ Klipper Tool."""

from .state_machine import RunState, RunStateMachine, TransitionResult
from .statistics import Observation, OutlierPolicy, StatisticSummary, summarize
from .units import CoordinateFrame, PixelScale, PixelVector2, Vector2Mm

__all__ = [
    "CoordinateFrame",
    "Observation",
    "OutlierPolicy",
    "PixelScale",
    "PixelVector2",
    "RunState",
    "RunStateMachine",
    "StatisticSummary",
    "TransitionResult",
    "Vector2Mm",
    "summarize",
]

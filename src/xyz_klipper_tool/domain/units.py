"""Typed units and explicit coordinate/sign contracts.

All conversions are pure. Pixel-to-millimetre scale is supplied by a taught
camera calibration; no historical machine coordinate is a default.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum


def _finite(value: float, name: str) -> float:
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    return float(value)


@dataclass(frozen=True)
class Millimetres:
    value_mm: float

    def __post_init__(self) -> None:
        object.__setattr__(self, "value_mm", _finite(self.value_mm, "value_mm"))


@dataclass(frozen=True)
class Pixels:
    value_px: float

    def __post_init__(self) -> None:
        object.__setattr__(self, "value_px", _finite(self.value_px, "value_px"))


@dataclass(frozen=True)
class Vector2Mm:
    x_mm: float
    y_mm: float

    def __post_init__(self) -> None:
        object.__setattr__(self, "x_mm", _finite(self.x_mm, "x_mm"))
        object.__setattr__(self, "y_mm", _finite(self.y_mm, "y_mm"))


@dataclass(frozen=True)
class PixelVector2:
    x_px: float
    y_px: float

    def __post_init__(self) -> None:
        object.__setattr__(self, "x_px", _finite(self.x_px, "x_px"))
        object.__setattr__(self, "y_px", _finite(self.y_px, "y_px"))


class CoordinateFrame(str, Enum):
    """Named frame; frame conversion is never implicit."""

    CAMERA_IMAGE = "camera_image"
    MACHINE = "machine"
    TOOL = "tool"
    PROVIDER = "provider"


class SignConvention(str, Enum):
    """Explicit sign meaning for an X/Y residual."""

    RESIDUAL_REFERENCE_MINUS_MEASURED = "reference_minus_measured"
    CORRECTION_TO_APPLY = "correction_to_apply"
    PROVIDER_REPORTED = "provider_reported"


@dataclass(frozen=True)
class PixelScale:
    """Taught scale in mm/px for a camera image; both directions are exact inverses."""

    x_mm_per_px: float
    y_mm_per_px: float

    def __post_init__(self) -> None:
        for name in ("x_mm_per_px", "y_mm_per_px"):
            value = _finite(getattr(self, name), name)
            if value <= 0:
                raise ValueError(f"{name} must be positive")
            object.__setattr__(self, name, value)

    def to_mm(self, pixels: PixelVector2) -> Vector2Mm:
        return Vector2Mm(pixels.x_px * self.x_mm_per_px, pixels.y_px * self.y_mm_per_px)

    def to_pixels(self, millimetres: Vector2Mm) -> PixelVector2:
        return PixelVector2(
            millimetres.x_mm / self.x_mm_per_px, millimetres.y_mm / self.y_mm_per_px
        )

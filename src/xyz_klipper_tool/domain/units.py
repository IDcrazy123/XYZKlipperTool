"""Finite typed quantities and explicit coordinate/sign contracts."""

import math
from dataclasses import dataclass
from enum import Enum


def _finite(value: float, name: str) -> float:
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    return float(value)


@dataclass(frozen=True)
class Millimetres:
    """A finite millimetre value; no frame or sign is implied."""

    value_mm: float

    def __post_init__(self) -> None:
        object.__setattr__(self, "value_mm", _finite(self.value_mm, "value_mm"))


@dataclass(frozen=True)
class Pixels:
    """A finite camera-image pixel value."""

    value_px: float

    def __post_init__(self) -> None:
        object.__setattr__(self, "value_px", _finite(self.value_px, "value_px"))


@dataclass(frozen=True)
class Seconds:
    """A finite duration in seconds."""

    value_s: float

    def __post_init__(self) -> None:
        object.__setattr__(self, "value_s", _finite(self.value_s, "value_s"))


@dataclass(frozen=True)
class Celsius:
    """A finite temperature in degrees Celsius."""

    value_c: float

    def __post_init__(self) -> None:
        object.__setattr__(self, "value_c", _finite(self.value_c, "value_c"))


class CoordinateFrame(str, Enum):
    CAMERA_IMAGE = "camera_image"
    MACHINE = "machine"
    TOOL = "tool"
    PROVIDER = "provider"


class SignConvention(str, Enum):
    REFERENCE_MINUS_MEASURED = "reference_minus_measured"
    CORRECTION_TO_APPLY = "correction_to_apply"
    PROVIDER_REPORTED = "provider_reported"


@dataclass(frozen=True)
class Vector2Mm:
    """Finite X/Y millimetres carrying frame and sign; neither is implicit."""

    x_mm: float
    y_mm: float
    frame: CoordinateFrame
    sign: SignConvention

    def __post_init__(self) -> None:
        object.__setattr__(self, "x_mm", _finite(self.x_mm, "x_mm"))
        object.__setattr__(self, "y_mm", _finite(self.y_mm, "y_mm"))


@dataclass(frozen=True)
class PixelVector2:
    """Finite camera pixels carrying frame and sign."""

    x_px: float
    y_px: float
    frame: CoordinateFrame
    sign: SignConvention

    def __post_init__(self) -> None:
        object.__setattr__(self, "x_px", _finite(self.x_px, "x_px"))
        object.__setattr__(self, "y_px", _finite(self.y_px, "y_px"))


@dataclass(frozen=True)
class PixelScale:
    """Positive, taught mm/px scale; conversion preserves sign explicitly."""

    x_mm_per_px: float
    y_mm_per_px: float

    def __post_init__(self) -> None:
        for name in ("x_mm_per_px", "y_mm_per_px"):
            value = _finite(getattr(self, name), name)
            if value <= 0:
                raise ValueError(f"{name} must be positive")
            object.__setattr__(self, name, value)

    def to_mm(self, pixels: PixelVector2) -> Vector2Mm:
        return Vector2Mm(
            pixels.x_px * self.x_mm_per_px,
            pixels.y_px * self.y_mm_per_px,
            CoordinateFrame.MACHINE,
            pixels.sign,
        )

    def to_pixels(self, millimetres: Vector2Mm) -> PixelVector2:
        return PixelVector2(
            millimetres.x_mm / self.x_mm_per_px,
            millimetres.y_mm / self.y_mm_per_px,
            CoordinateFrame.CAMERA_IMAGE,
            millimetres.sign,
        )


def convert_sign(
    value_mm: Millimetres, source: SignConvention, target: SignConvention
) -> Millimetres:
    """Convert between residual and correction signs; the surrounding result supplies frame."""
    return value_mm if source is target else Millimetres(-value_mm.value_mm)

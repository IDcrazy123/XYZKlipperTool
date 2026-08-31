"""Finite typed quantities and explicit coordinate/sign contracts."""

import math
from dataclasses import dataclass
from enum import Enum


def _finite(value: object, name: str) -> float:
    value_object: object = value
    if not isinstance(value_object, (int, float)) or isinstance(value_object, bool):
        raise ValueError(f"{name} must be finite")  # noqa: TRY004
    numeric_value = float(value_object)
    if not math.isfinite(numeric_value):
        raise ValueError(f"{name} must be finite")
    return numeric_value


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
        frame_object: object = self.frame
        sign_object: object = self.sign
        if (
            type(frame_object) is not CoordinateFrame
            or type(sign_object) is not SignConvention
        ):
            raise ValueError("frame and sign must be typed enums")


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
        frame_object: object = self.frame
        sign_object: object = self.sign
        if (
            type(frame_object) is not CoordinateFrame
            or type(sign_object) is not SignConvention
        ):
            raise ValueError("frame and sign must be typed enums")


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
        if pixels.frame is not CoordinateFrame.CAMERA_IMAGE:
            raise ValueError("PixelScale requires CAMERA_IMAGE source frame")
        return Vector2Mm(
            pixels.x_px * self.x_mm_per_px,
            pixels.y_px * self.y_mm_per_px,
            CoordinateFrame.MACHINE,
            pixels.sign,
        )

    def to_pixels(self, millimetres: Vector2Mm) -> PixelVector2:
        if millimetres.frame is not CoordinateFrame.MACHINE:
            raise ValueError("PixelScale requires MACHINE source frame")
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
    if source is target:
        return value_mm
    if {source, target} != {
        SignConvention.REFERENCE_MINUS_MEASURED,
        SignConvention.CORRECTION_TO_APPLY,
    }:
        raise ValueError("BLOCKED_BY_SOURCE: provider sign mapping is not established")
    return Millimetres(-value_mm.value_mm)

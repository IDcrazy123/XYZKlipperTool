"""Bounded, local-only camera input contracts; no camera I/O is performed."""

from dataclasses import dataclass, field
from urllib.parse import urlparse

from xyz_klipper_tool.domain.models import ReasonCode
from xyz_klipper_tool.domain.units import Seconds


@dataclass(frozen=True)
class CaptureLimits:
    """Finite capture limits for encoded bytes, dimensions, pixels, retries, and age."""

    max_encoded_bytes: int = 8 * 1024 * 1024
    max_width_px: int = 8192
    max_height_px: int = 8192
    max_retries: int = 3
    max_frame_age_s: Seconds = field(default_factory=lambda: Seconds(2.0))

    def __post_init__(self) -> None:
        if (
            type(self.max_encoded_bytes) is not int
            or not 1 <= self.max_encoded_bytes <= 64 * 1024 * 1024
        ):
            raise ValueError(f"{ReasonCode.OVERSIZED_INPUT.value}: encoded-byte limit")
        if type(self.max_width_px) is not int or not 1 <= self.max_width_px <= 16384:
            raise ValueError("invalid width limit")
        if type(self.max_height_px) is not int or not 1 <= self.max_height_px <= 16384:
            raise ValueError("invalid height limit")
        if type(self.max_retries) is not int or not 0 <= self.max_retries <= 8:
            raise ValueError("invalid retry limit")


@dataclass(frozen=True)
class CaptureRequest:
    """Allowlisted local camera target and bounded timeout; no network is opened."""

    target: str
    timeout_s: Seconds

    def __post_init__(self) -> None:
        validate_camera_url(self.target)
        if type(self.timeout_s) is not Seconds or not 0 < self.timeout_s.value_s <= 30:
            raise ValueError("timeout must be bounded Seconds")


@dataclass(frozen=True)
class CameraFrame:
    """Immutable encoded frame metadata with explicit dimensions and capture age."""

    encoded: bytes
    width_px: int
    height_px: int
    age_s: Seconds

    def validate(self, limits: CaptureLimits) -> None:
        """Validate encoded bytes, dimensions, pixels, and age against finite limits."""
        if (
            type(self.encoded) is not bytes
            or len(self.encoded) > limits.max_encoded_bytes
        ):
            raise ValueError(f"{ReasonCode.OVERSIZED_INPUT.value}: encoded frame")
        if (
            type(self.width_px) is not int
            or type(self.height_px) is not int
            or self.width_px < 1
            or self.height_px < 1
        ):
            raise ValueError("invalid frame dimensions")
        if (
            self.width_px > limits.max_width_px
            or self.height_px > limits.max_height_px
            or self.width_px * self.height_px > 64_000_000
        ):
            raise ValueError(f"{ReasonCode.OVERSIZED_INPUT.value}: frame dimensions")
        if (
            type(self.age_s) is not Seconds
            or not 0 <= self.age_s.value_s <= limits.max_frame_age_s.value_s
        ):
            raise ValueError("stale or invalid frame age")


def validate_camera_url(target: str) -> str:
    """Accept only local device paths or loopback HTTP(S); reject credentials and traversal."""
    if type(target) is not str or not target or ".." in target or "@" in target:
        raise ValueError(f"{ReasonCode.CORRUPT_INPUT.value}: camera target")
    parsed = urlparse(target)
    if parsed.scheme in ("", "device") and target.startswith(("/", "device:")):
        return target
    if (
        parsed.scheme in ("http", "https")
        and parsed.hostname in ("127.0.0.1", "localhost", "::1")
        and parsed.username is None
    ):
        return target
    raise ValueError("camera target is not local/allowlisted")

"""Bounded, local-only camera input contracts; no camera I/O is performed."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Protocol
from urllib.parse import urlparse

from xyz_klipper_tool.domain.models import ReasonCode
from xyz_klipper_tool.domain.units import Seconds


class FrameValidationError(ValueError):
    """Typed frame rejection carrying a stable reason code."""

    def __init__(self, reason: ReasonCode, message: str) -> None:
        super().__init__(message)
        self.reason = reason


@dataclass(frozen=True)
class CaptureLimits:
    """Finite capture limits for encoded bytes, dimensions, pixels, retries, and age."""

    max_encoded_bytes: int = 8 * 1024 * 1024
    max_width_px: int = 8192
    max_height_px: int = 8192
    max_retries: int = 3
    max_pixels: int = 64_000_000
    max_decode_time_s: Seconds = field(default_factory=lambda: Seconds(2.0))
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
        if type(self.max_pixels) is not int or not 1 <= self.max_pixels <= 256_000_000:
            raise ValueError("invalid pixel limit")
        if (
            type(self.max_decode_time_s) is not Seconds
            or not 0 < self.max_decode_time_s.value_s <= 30
        ):
            raise ValueError("invalid decode-time limit")


class CameraTransport(Protocol):
    """Injected transport boundary; no live camera or network is implied."""

    def capture(self, timeout_s: Seconds) -> bytes:
        """Return encoded bytes or raise a typed transport fault."""
        ...


class CameraClock(Protocol):
    """Injected clock for deterministic elapsed-time checks."""

    def now_utc(self) -> datetime:
        """Return a timezone-aware UTC timestamp without sleeping."""
        ...


@dataclass(frozen=True)
class CaptureResult:
    """Bounded capture outcome with attempts and total bytes."""

    encoded: bytes | None
    reason: ReasonCode
    attempts: int
    total_bytes: int


class BoundedCameraProvider:
    """Retrying, clock-injected camera adapter for offline tests only."""

    def __init__(
        self, transport: CameraTransport, clock: CameraClock, limits: CaptureLimits
    ) -> None:
        self.transport, self.clock, self.limits = transport, clock, limits

    def capture(self, request: "CaptureRequest") -> CaptureResult:
        """Pass a finite timeout per attempt and classify bounded transport faults."""
        total = 0
        for attempt in range(1, self.limits.max_retries + 2):
            started = self.clock.now_utc()
            try:
                encoded = self.transport.capture(request.timeout_s)
            except TimeoutError:
                if attempt > self.limits.max_retries:
                    return CaptureResult(
                        None, ReasonCode.DECODE_TIMEOUT, attempt, total
                    )
                continue
            except (ValueError, TypeError):
                return CaptureResult(None, ReasonCode.CORRUPT_INPUT, attempt, total)
            total += len(encoded)
            if (
                self.clock.now_utc() - started
            ).total_seconds() > self.limits.max_decode_time_s.value_s:
                return CaptureResult(None, ReasonCode.DECODE_TIMEOUT, attempt, total)
            if not encoded:
                return CaptureResult(None, ReasonCode.MISSING_INPUT, attempt, total)
            if total > self.limits.max_encoded_bytes:
                return CaptureResult(None, ReasonCode.OVERSIZED_INPUT, attempt, total)
            return CaptureResult(encoded, ReasonCode.NONE, attempt, total)
        return CaptureResult(
            None, ReasonCode.DECODE_TIMEOUT, self.limits.max_retries + 1, total
        )


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
        if type(self.encoded) is not bytes or not self.encoded:
            raise FrameValidationError(
                ReasonCode.MISSING_INPUT, "encoded frame missing"
            )
        if len(self.encoded) > limits.max_encoded_bytes:
            raise FrameValidationError(
                ReasonCode.OVERSIZED_INPUT, "encoded frame rejected"
            )
        if (
            type(self.width_px) is not int
            or type(self.height_px) is not int
            or self.width_px < 1
            or self.height_px < 1
        ):
            raise FrameValidationError(
                ReasonCode.CORRUPT_INPUT, "invalid frame dimensions"
            )
        if (
            self.width_px > limits.max_width_px
            or self.height_px > limits.max_height_px
            or self.width_px * self.height_px > limits.max_pixels
        ):
            raise FrameValidationError(
                ReasonCode.OVERSIZED_INPUT, "frame dimensions exceed bounds"
            )
        if (
            type(self.age_s) is not Seconds
            or not 0 <= self.age_s.value_s <= limits.max_frame_age_s.value_s
        ):
            raise FrameValidationError(ReasonCode.STALE_FRAME, "stale frame age")


def validate_camera_url(target: str) -> str:
    """Accept only local device paths or loopback HTTP(S); reject credentials and traversal."""
    from urllib.parse import unquote

    if type(target) is not str or not target:
        raise ValueError(f"{ReasonCode.CORRUPT_INPUT.value}: camera target")
    normalized = target
    for _ in range(3):
        decoded = unquote(normalized)
        if decoded == normalized:
            break
        normalized = decoded
    if ".." in normalized or "@" in normalized or "#" in normalized:
        raise ValueError(f"{ReasonCode.CORRUPT_INPUT.value}: camera target")
    parsed = urlparse(normalized)
    if parsed.scheme in ("", "device") and normalized.startswith(("/", "device:")):
        return normalized
    if (
        parsed.scheme in ("http", "https")
        and parsed.hostname in ("127.0.0.1", "localhost", "::1")
        and parsed.username is None
    ):
        return normalized
    raise ValueError("camera target is not local/allowlisted")

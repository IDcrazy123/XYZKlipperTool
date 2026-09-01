"""Bounded, local-only camera input contracts; no camera I/O is performed."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
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
        if (
            type(self.max_frame_age_s) is not Seconds
            or not 0 <= self.max_frame_age_s.value_s <= 300
        ):
            raise ValueError("invalid frame-age limit")


class CameraTransport(Protocol):  # pragma: no cover - protocol declaration
    """Injected transport boundary; no live camera or network is implied."""

    def capture(self, target: str, timeout_s: Seconds) -> bytes:
        """Capture normalized target with finite timeout or raise transport fault."""
        ...


class CameraClock(Protocol):  # pragma: no cover - protocol declaration
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
    frame_sample_id: str
    camera_fingerprint: str
    captured_at_utc: datetime
    exposure_metadata: str | None = None

    def __post_init__(self) -> None:
        if type(self.reason) is not ReasonCode:
            raise ValueError("capture reason must be typed")
        if self.encoded is not None and type(self.encoded) is not bytes:
            raise ValueError("encoded capture must be bytes")
        if type(self.attempts) is not int or self.attempts < 1:
            raise ValueError("attempts must be positive")
        if type(self.total_bytes) is not int or self.total_bytes < 0:
            raise ValueError("total_bytes must be nonnegative")
        if (
            type(self.frame_sample_id) is not str
            or not self.frame_sample_id.strip()
            or type(self.camera_fingerprint) is not str
            or not self.camera_fingerprint.strip()
        ):
            raise ValueError("capture identities must be text")
        if type(
            self.captured_at_utc
        ) is not datetime or self.captured_at_utc.utcoffset() != timedelta(0):
            raise ValueError("captured_at_utc must be UTC")
        if (self.reason is ReasonCode.NONE) != (
            self.encoded is not None and bool(self.encoded)
        ):
            raise ValueError("capture success/result coherence failure")
        if self.encoded is not None and len(self.encoded) > 8 * 1024 * 1024:
            raise ValueError("capture bytes exceed bound")
        if self.exposure_metadata is not None and (
            type(self.exposure_metadata) is not str
            or len(self.exposure_metadata) > 1024
        ):
            raise ValueError("exposure metadata exceeds bound")


class BoundedCameraProvider:
    """Retrying, clock-injected camera adapter for offline tests only."""

    def __init__(
        self, transport: CameraTransport, clock: CameraClock, limits: CaptureLimits
    ) -> None:
        self.transport, self.clock, self.limits = transport, clock, limits

    def capture(self, request: CaptureRequest) -> CaptureResult:
        """Pass a finite timeout per attempt and classify bounded transport faults."""
        total = 0
        started = datetime.min.replace(tzinfo=timezone.utc)
        for attempt in range(1, self.limits.max_retries + 2):
            started = self.clock.now_utc()
            try:
                encoded = self.transport.capture(request.target, request.timeout_s)
            except TimeoutError:
                if attempt > self.limits.max_retries:
                    return CaptureResult(
                        None,
                        ReasonCode.CAPTURE_TIMEOUT,
                        attempt,
                        total,
                        request.frame_sample_id,
                        request.camera_fingerprint,
                        started,
                        request.exposure_metadata,
                    )
                continue
            except (ValueError, TypeError):
                return CaptureResult(
                    None,
                    ReasonCode.CORRUPT_INPUT,
                    attempt,
                    total,
                    request.frame_sample_id,
                    request.camera_fingerprint,
                    started,
                    request.exposure_metadata,
                )
            total += len(encoded)
            finished = self.clock.now_utc()
            if (finished - started).total_seconds() > request.timeout_s.value_s:
                return CaptureResult(
                    None,
                    ReasonCode.CAPTURE_TIMEOUT,
                    attempt,
                    total,
                    request.frame_sample_id,
                    request.camera_fingerprint,
                    started,
                    request.exposure_metadata,
                )
            if not encoded:
                return CaptureResult(
                    None,
                    ReasonCode.MISSING_INPUT,
                    attempt,
                    total,
                    request.frame_sample_id,
                    request.camera_fingerprint,
                    started,
                    request.exposure_metadata,
                )
            if total > self.limits.max_encoded_bytes:
                return CaptureResult(
                    None,
                    ReasonCode.OVERSIZED_INPUT,
                    attempt,
                    total,
                    request.frame_sample_id,
                    request.camera_fingerprint,
                    started,
                    request.exposure_metadata,
                )
            return CaptureResult(
                encoded,
                ReasonCode.NONE,
                attempt,
                total,
                request.frame_sample_id,
                request.camera_fingerprint,
                started,
                request.exposure_metadata,
            )
        return CaptureResult(
            None,
            ReasonCode.CAPTURE_TIMEOUT,
            self.limits.max_retries + 1,
            total,
            request.frame_sample_id,
            request.camera_fingerprint,
            started,
            request.exposure_metadata,
        )


@dataclass(frozen=True)
class CaptureRequest:
    """Allowlisted local camera target and bounded timeout; no network is opened."""

    target: str
    timeout_s: Seconds
    frame_sample_id: str
    camera_fingerprint: str
    exposure_metadata: str | None = None

    def __post_init__(self) -> None:
        normalized = validate_camera_url(self.target)
        object.__setattr__(self, "target", normalized)
        if type(self.timeout_s) is not Seconds or not 0 < self.timeout_s.value_s <= 30:
            raise ValueError("timeout must be bounded Seconds")
        if type(self.frame_sample_id) is not str or not self.frame_sample_id.strip():
            raise ValueError("frame sample identity is required")
        if (
            type(self.camera_fingerprint) is not str
            or not self.camera_fingerprint.strip()
        ):
            raise ValueError("camera fingerprint is required")
        if self.exposure_metadata is not None and (
            type(self.exposure_metadata) is not str
            or len(self.exposure_metadata) > 1024
        ):
            raise ValueError("exposure metadata exceeds bound")


@dataclass(frozen=True)
class CameraFrame:
    """Immutable encoded frame metadata with explicit dimensions and capture age."""

    encoded: bytes
    width_px: int
    height_px: int
    age_s: Seconds
    frame_sample_id: str
    camera_fingerprint: str
    captured_at_utc: datetime
    exposure_metadata: str | None = None

    def __post_init__(self) -> None:
        if type(self.frame_sample_id) is not str or not self.frame_sample_id.strip():
            raise ValueError("frame sample identity is required")
        if (
            type(self.camera_fingerprint) is not str
            or not self.camera_fingerprint.strip()
        ):
            raise ValueError("camera fingerprint is required")
        if type(
            self.captured_at_utc
        ) is not datetime or self.captured_at_utc.utcoffset() != timedelta(0):
            raise ValueError("captured_at_utc must be UTC")
        if self.exposure_metadata is not None and (
            type(self.exposure_metadata) is not str
            or len(self.exposure_metadata) > 1024
        ):
            raise ValueError("exposure metadata exceeds bound")

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

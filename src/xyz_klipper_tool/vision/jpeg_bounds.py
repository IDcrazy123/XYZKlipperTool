"""Pre-decode JPEG byte and header bounds for host-side image inspection."""

from __future__ import annotations

from enum import Enum
from pathlib import Path


class JpegBoundaryReason(Enum):
    """Typed fail-closed reason returned by pre-decode JPEG validation."""

    CORRUPT_INPUT = "CORRUPT_INPUT"
    OVERSIZED_INPUT = "OVERSIZED_INPUT"


class JpegBoundaryError(ValueError):
    """A JPEG fails bounded byte/header validation before decoder allocation."""

    def __init__(self, reason: JpegBoundaryReason) -> None:
        super().__init__(reason.value)
        self.reason = reason


def validate_jpeg_header(encoded: bytes, max_bytes: int, max_pixels: int) -> None:
    """Validate JPEG SOI/SOF, encoded bytes, dimensions, and pixel bound without OpenCV."""
    if type(encoded) is not bytes or not encoded or len(encoded) > max_bytes:
        raise JpegBoundaryError(JpegBoundaryReason.OVERSIZED_INPUT)
    if len(encoded) < 4 or encoded[:2] != b"\xff\xd8":
        raise JpegBoundaryError(JpegBoundaryReason.CORRUPT_INPUT)
    index = 2
    sof_markers = (
        set(range(0xC0, 0xC4))
        | set(range(0xC5, 0xC8))
        | set(range(0xC9, 0xCC))
        | set(range(0xCD, 0xD0))
    )
    while index < len(encoded):
        if encoded[index] != 0xFF:
            raise JpegBoundaryError(JpegBoundaryReason.CORRUPT_INPUT)
        while index < len(encoded) and encoded[index] == 0xFF:
            index += 1
        if index >= len(encoded):
            raise JpegBoundaryError(JpegBoundaryReason.CORRUPT_INPUT)
        marker = encoded[index]
        index += 1
        if marker in (0xD8, 0xD9):
            continue
        if marker == 0xDA:
            raise JpegBoundaryError(JpegBoundaryReason.CORRUPT_INPUT)
        if index + 2 > len(encoded):
            raise JpegBoundaryError(JpegBoundaryReason.CORRUPT_INPUT)
        segment_length = int.from_bytes(encoded[index : index + 2], "big")
        if segment_length < 2 or index + segment_length > len(encoded):
            raise JpegBoundaryError(JpegBoundaryReason.CORRUPT_INPUT)
        if marker in sof_markers:
            if segment_length < 7:
                raise JpegBoundaryError(JpegBoundaryReason.CORRUPT_INPUT)
            height = int.from_bytes(encoded[index + 3 : index + 5], "big")
            width = int.from_bytes(encoded[index + 5 : index + 7], "big")
            if width < 1 or height < 1:
                raise JpegBoundaryError(JpegBoundaryReason.CORRUPT_INPUT)
            if width * height > max_pixels:
                raise JpegBoundaryError(JpegBoundaryReason.OVERSIZED_INPUT)
            return
        index += segment_length
    raise JpegBoundaryError(JpegBoundaryReason.CORRUPT_INPUT)


def read_bounded(path: Path, max_bytes: int) -> bytes:
    """Read at most max_bytes+1 so oversized files are rejected before decode."""
    with path.open("rb") as handle:
        return handle.read(max_bytes + 1)

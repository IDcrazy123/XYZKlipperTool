"""Typed, side-effect-explicit ports; implementations live in adapters."""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Protocol, runtime_checkable

from xyz_klipper_tool.domain.models import ProviderKind, ToolId
from xyz_klipper_tool.domain.units import CoordinateFrame, Millimetres, PixelVector2

from .ownership import RunOperation, RunToken

if TYPE_CHECKING:
    from xyz_klipper_tool.stations.models import StationRecord


class PrinterState(str, Enum):
    """Typed read-only simulator state; no state value authorizes physical action."""

    READY = "ready"
    PRINTING = "printing"
    PAUSED = "paused"
    SHUTDOWN = "shutdown"


@dataclass(frozen=True)
class CurrentPose:
    """Explicit machine pose with millimetre units; it is input data, not movement."""

    x_mm: Millimetres
    y_mm: Millimetres
    z_mm: Millimetres
    frame: CoordinateFrame = CoordinateFrame.MACHINE

    def __post_init__(self) -> None:
        if (
            type(self.frame) is not CoordinateFrame
            or self.frame is not CoordinateFrame.MACHINE
        ):
            raise ValueError("current pose must use MACHINE frame")


@runtime_checkable
class CameraProvider(Protocol):
    """Capture one bounded frame; no port contract authorizes machine motion."""

    def capture(self) -> bytes:
        """Return one bounded frame; implementations document blocking/failure behavior."""
        ...


@runtime_checkable
class VisionDetector(Protocol):
    """Detect a finite camera measurement without blocking or persistence."""

    def detect(self, frame: bytes) -> PixelVector2:
        """Return a finite camera-image detection without physical side effects."""
        ...


@runtime_checkable
class ToolchangerAdapter(Protocol):
    """Read dynamic tool identity/state; it does not authorize tool changes."""

    def discover_tools(self) -> Sequence[ToolId]:
        """Return dynamic tool identities without changing tool state."""
        ...

    def active_tool(self) -> ToolId | None:
        """Return the known active tool or unknown."""
        ...

    def detected_tool(self) -> ToolId | None:
        """Return the independently detected tool or unknown."""
        ...


@runtime_checkable
class ZProvider(Protocol):
    """Read a provider-specific Z value; physical compatibility remains HIL."""

    @property
    def provider_kind(self) -> ProviderKind:
        """Identify the Z provider represented by this adapter."""
        ...

    def measure_z_mm(self) -> Millimetres:
        """Return provider-specific Z data; physical compatibility remains HIL."""
        ...


@runtime_checkable
class StationStore(Protocol):
    """Store station records; adapters must define atomic/failure behavior."""

    def get(self, namespace: str, name: str) -> "StationRecord | None":
        """Read one provider namespace record."""
        ...

    def put(self, namespace: str, name: str, value: "StationRecord") -> None:
        """Persist one record according to adapter atomicity guarantees."""
        ...

    def remove(self, namespace: str, name: str) -> None:
        """Remove one explicitly confirmed record."""
        ...

    def list(self, namespace: str) -> Sequence[str]:
        """List records deterministically."""
        ...


@runtime_checkable
class EvidenceStore(Protocol):
    """Persist evidence metadata without mutating completed raw evidence."""

    def append(self, record: Mapping[str, object]) -> None:
        """Append metadata without modifying completed raw evidence."""
        ...


@runtime_checkable
class OffsetReader(Protocol):
    """Read offsets only; no apply or printer side effect is implied."""

    def read(self) -> Mapping[ToolId, Millimetres]:
        """Read typed offsets without applying them."""
        ...


@runtime_checkable
class OffsetWriter(Protocol):
    """Apply is outside Phase 02; fakes must record calls and never write hardware."""

    def write(self, offsets: Mapping[ToolId, Millimetres]) -> None:
        """Write offsets only in a later explicitly authorized phase."""
        ...


@runtime_checkable
class Clock(Protocol):
    """Supply deterministic timestamps without sleeping or blocking."""

    def now_utc(self) -> datetime:
        """Return a timezone-aware UTC timestamp without sleeping."""
        ...


@runtime_checkable
class RunLock(Protocol):
    """Acquire/release typed ownership; conflicting operations fail closed."""

    def acquire(self, operation: RunOperation) -> RunToken:
        """Acquire ownership or reject deterministic conflict."""
        ...

    def release(self, token: RunToken) -> None:
        """Release exact ownership or fail closed."""
        ...


@runtime_checkable
class PrinterStateProvider(Protocol):
    """Read-only simulator boundary for readiness and safe state assertions."""

    def state(self) -> PrinterState:
        """Return read-only printer state."""
        ...


@runtime_checkable
class CurrentPoseProvider(Protocol):
    """Return explicit current pose input; no movement or inferred coordinate occurs."""

    def current_pose(self) -> CurrentPose:
        """Return explicit pose input without motion or inference."""
        ...

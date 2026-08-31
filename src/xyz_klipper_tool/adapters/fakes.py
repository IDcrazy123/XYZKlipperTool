"""Scripted, no-sleep/no-thread/no-network fake adapters."""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, ClassVar, cast

from xyz_klipper_tool.domain.models import ProviderKind, ToolId
from xyz_klipper_tool.domain.units import Millimetres, PixelVector2
from xyz_klipper_tool.ports import MAX_CAMERA_FRAME_BYTES, CurrentPose, PrinterState
from xyz_klipper_tool.ports.ownership import RunOperation, RunToken
from xyz_klipper_tool.stations.models import StationRecord


def _next(script: list[object], calls: list[str], operation: str) -> object:
    calls.append(operation)
    if not script:
        raise RuntimeError(f"unscripted fake operation: {operation}")
    value = script.pop(0)
    if isinstance(value, BaseException):
        raise value
    return value


@dataclass
class FakeCamera:
    """Scripted camera fake with recorded bounded capture calls."""

    frames: list[object] = field(default_factory=list)
    calls: list[str] = field(default_factory=list)

    def capture(self) -> bytes:
        """Return the next scripted frame without sleeping or I/O."""
        value = _next(self.frames, self.calls, "capture")
        if not isinstance(value, bytes):
            raise TypeError("fake frame must be bytes")
        if len(value) > MAX_CAMERA_FRAME_BYTES:
            raise ValueError("fake frame exceeds bounded camera contract")
        return value


@dataclass
class FakeVisionDetector:
    """Scripted detector fake with deterministic call recording."""

    detections: list[object] = field(default_factory=list)
    calls: list[str] = field(default_factory=list)

    def detect(self, frame: bytes) -> PixelVector2:
        """Return the next scripted detection and reject malformed values."""
        value = _next(self.detections, self.calls, "detect")
        if not isinstance(value, PixelVector2):
            raise TypeError("fake detection must be PixelVector2")
        return value


@dataclass
class FakeZProvider:
    """Scripted provider-specific Z fake; it never probes hardware."""

    provider_kind: ProviderKind
    measurements: list[object] = field(default_factory=list)
    calls: list[str] = field(default_factory=list)

    def measure_z_mm(self) -> Millimetres:
        """Return the next scripted millimetre result."""
        value = _next(self.measurements, self.calls, "measure_z_mm")
        if not isinstance(value, Millimetres):
            raise TypeError("fake Z result must be Millimetres")
        return value


@dataclass
class FakeToolchanger:
    """Read-only dynamic tool/state fake with no tool-change operation."""

    tools: Sequence[ToolId]
    active: ToolId | None = None
    detected: ToolId | None = None
    calls: list[str] = field(default_factory=list)

    def discover_tools(self) -> Sequence[ToolId]:
        """Return scripted tool identities in their supplied order."""
        self.calls.append("discover_tools")
        return tuple(self.tools)

    def active_tool(self) -> ToolId | None:
        """Return the scripted active tool without changing it."""
        self.calls.append("active_tool")
        return self.active

    def detected_tool(self) -> ToolId | None:
        """Return the scripted detected tool without hardware access."""
        self.calls.append("detected_tool")
        return self.detected


@dataclass
class FakePrinter:
    """Read-only printer state and explicit current-pose fake."""

    pose: CurrentPose
    printer_state: PrinterState = PrinterState.READY
    calls: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Reject untyped pose or printer state at fake construction time."""
        if (
            type(self.pose) is not CurrentPose
            or type(self.printer_state) is not PrinterState
        ):
            raise TypeError("pose and printer_state must use typed contracts")

    def current_pose(self) -> CurrentPose:
        """Return the scripted current pose without moving the printer."""
        self.calls.append("current_pose")
        return self.pose

    def state(self) -> PrinterState:
        """Return the scripted printer state."""
        self.calls.append("state")
        return self.printer_state


@dataclass
class FakeClock:
    """Deterministic clock with no sleeping or wall-clock dependency."""

    current: datetime

    def now_utc(self) -> datetime:
        """Return the configured UTC timestamp."""
        if self.current.tzinfo is None:
            raise ValueError("fake clock must be timezone-aware")
        return self.current.astimezone(timezone.utc)


@dataclass
class FakeStationStore:
    """In-memory station store with deterministic calls and no filesystem."""

    records: dict[tuple[str, str], StationRecord | object] = field(default_factory=dict)
    calls: list[str] = field(default_factory=list)

    def get(self, namespace: str, name: str) -> StationRecord | None:
        """Read one namespaced record."""
        self.calls.append(f"get:{namespace}:{name}")
        value: object = self.records.get((namespace, name))
        if value is not None and not isinstance(value, StationRecord):
            raise TypeError("corrupt station value")
        return value

    def put(self, namespace: str, name: str, value: StationRecord) -> None:
        """Write one namespaced record in memory."""
        candidate: object = cast(Any, value)
        if (
            type(namespace) is not str
            or type(name) is not str
            or not isinstance(candidate, StationRecord)
            or namespace != candidate.station_type.value
            or name != candidate.name
        ):
            raise ValueError("station namespace, name, and record identity mismatch")
        self.calls.append(f"put:{namespace}:{name}")
        self.records[(namespace, name)] = value

    def remove(self, namespace: str, name: str) -> None:
        """Remove one namespaced record in memory."""
        self.calls.append(f"remove:{namespace}:{name}")
        self.records.pop((namespace, name), None)

    def list(self, namespace: str) -> Sequence[str]:
        """List names in deterministic insertion order."""
        self.calls.append(f"list:{namespace}")
        return tuple(name for ns, name in self.records if ns == namespace)


@dataclass
class FakeEvidenceStore:
    """In-memory append-only evidence fake."""

    records: list[Mapping[str, object]] = field(default_factory=list)

    def append(self, record: Mapping[str, object]) -> None:
        """Append a copied metadata record without raw-file mutation."""
        self.records.append(dict(record))


@dataclass
class FakeOffsetReader:
    """Read-only offset fake for proving apply separation."""

    offsets: Mapping[ToolId, Millimetres]

    def read(self) -> Mapping[ToolId, Millimetres]:
        """Return a copied offset mapping."""
        return dict(self.offsets)


@dataclass
class FakeOffsetWriter:
    """Writer sentinel that fails if Phase 02 attempts apply."""

    calls: list[Mapping[ToolId, Millimetres]] = field(default_factory=list)

    def write(self, offsets: Mapping[ToolId, Millimetres]) -> None:
        """Record and reject an attempted offset write."""
        self.calls.append(dict(offsets))
        raise AssertionError("Phase 02 must not apply offsets")


@dataclass
class FakeRunLock:
    """Single-owner deterministic lock fake with typed release validation."""

    held: RunToken | None = None
    next_nonce: int = 1
    _issuer_sequence: ClassVar[int] = 1
    _issuer: int = field(init=False)

    def __post_init__(self) -> None:
        """Assign a monotonic explicit issuer identity, never an object address."""
        self._issuer = FakeRunLock._issuer_sequence
        FakeRunLock._issuer_sequence += 1

    @property
    def issuer_id(self) -> int:
        """Return this lock instance identity used to reject foreign tokens."""
        return self._issuer

    def acquire(self, operation: RunOperation) -> RunToken:
        """Acquire once or reject a conflicting owner."""
        if type(operation) is not RunOperation:
            raise TypeError("operation must be RunOperation")
        if self.held is not None:
            raise RuntimeError("CONFLICT: run lock held")
        token = RunToken(operation, self.issuer_id, self.next_nonce)
        self.next_nonce += 1
        self.held = token
        return token

    def release(self, token: object) -> None:
        """Release only the currently held exact token."""
        if (
            type(token) is not RunToken
            or self.held is None
            or token.issuer != self.issuer_id
            or token != self.held
        ):
            raise ValueError("lock token does not own lock")
        self.held = None

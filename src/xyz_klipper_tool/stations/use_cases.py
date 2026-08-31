"""Side-effect-controlled station workflows over ports."""

from xyz_klipper_tool.domain.models import ReasonCode
from xyz_klipper_tool.ports import (
    Clock,
    CurrentPoseProvider,
    RunLock,
    RunOperation,
    StationStore,
)

from .models import CurrentPose, StationRecord, StationType, validate_text


def _station_type(provider: object) -> StationType:
    from xyz_klipper_tool.domain.models import ProviderKind

    if provider is ProviderKind.CAMERA:
        return StationType.CAMERA
    if provider is ProviderKind.SWITCH:
        return StationType.SWITCH_Z
    if provider is ProviderKind.CARTOGRAPHER_TOUCH:
        return StationType.CARTOGRAPHER_TOUCH_Z
    raise ValueError(f"{ReasonCode.PROVIDER_CONTRACT_UNVERIFIED.value}: provider")


def teach_station(
    store: StationStore,
    pose_provider: CurrentPoseProvider,
    clock: Clock,
    name: str,
    provider: object,
    configuration_fingerprint: str,
    revision: str,
    provenance: str,
    safe_z_mm: object | None,
    lock: RunLock,
) -> StationRecord:
    """Teach from explicit current pose; omitted SAFE_Z fails closed and no movement occurs."""
    validate_text(name, "name")
    if safe_z_mm is None:
        raise ValueError(f"{ReasonCode.UNSAFE_APPROACH.value}: SAFE_Z is required")
    if not hasattr(pose_provider, "current_pose"):
        raise ValueError("current pose provider is required")
    pose = pose_provider.current_pose()
    if not isinstance(pose, CurrentPose):
        raise TypeError("current pose input must be CurrentPose")
    from xyz_klipper_tool.domain.models import ProviderKind
    from xyz_klipper_tool.domain.units import Millimetres

    if type(provider) is not ProviderKind or type(safe_z_mm) is not Millimetres:
        raise ValueError("provider and SAFE_Z must be typed")
    token = lock.acquire(RunOperation.TEACH)
    try:
        record = StationRecord(
            name,
            _station_type(provider),
            provider,
            pose,
            safe_z_mm,
            revision,
            clock.now_utc(),
            configuration_fingerprint,
            provenance,
        )
        store.put(record.station_type.value, record.name, record)
        return record
    finally:
        lock.release(token)


def show_stations(store: StationStore, name: str | None = None) -> tuple[object, ...]:
    """Read station records without mutation, I/O blocking policy, or writer access."""
    if name is not None:
        validate_text(name, "name")
        result: list[object] = []
        for namespace in StationType:
            value = store.get(namespace.value, name)
            if value is not None:
                if not isinstance(value, StationRecord):
                    raise TypeError("corrupt station value")
                result.append(value)
        return tuple(result)
    result = []
    for namespace in StationType:
        for station_name in sorted(store.list(namespace.value)):
            value = store.get(namespace.value, station_name)
            if value is not None:
                if not isinstance(value, StationRecord):
                    raise ValueError("corrupt station value")
                result.append(value)
    return tuple(result)


def clear_station(
    store: StationStore,
    station_type: StationType,
    name: str,
    confirm: str | None = None,
    lock: RunLock | None = None,
) -> tuple[object, ...]:
    """Return a preview or perform exact-confirmed removal; no offset writer is called."""
    if type(station_type) is not StationType:
        raise ValueError("station_type must be typed")
    validate_text(name, "name")
    if lock is None:
        raise ValueError("teach/clear operation requires a run lock")
    token = lock.acquire(RunOperation.TEACH)
    try:
        existing = store.get(station_type.value, name)
        if existing is None:
            return ()
        if not isinstance(existing, StationRecord):
            raise TypeError("corrupt station value")
        preview = (existing,)
        if confirm is None:
            return preview
        if confirm != f"CLEAR:{station_type.value}:{name}":
            raise ValueError(
                f"{ReasonCode.CONFIRMATION_REQUIRED.value}: exact token required"
            )
        store.remove(station_type.value, name)
        return preview
    finally:
        lock.release(token)

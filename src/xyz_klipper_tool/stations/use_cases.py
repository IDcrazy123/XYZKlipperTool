"""Side-effect-controlled station workflows over ports."""

from typing import cast

from xyz_klipper_tool.domain.models import ReasonCode
from xyz_klipper_tool.ports import (
    Clock,
    CurrentPoseProvider,
    RunLock,
    RunOperation,
    StationStore,
)
from xyz_klipper_tool.ports import (
    CurrentPose as PortCurrentPose,
)

from .models import StationRecord, StationType, validate_text


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
    token = lock.acquire(RunOperation.TEACH)
    try:
        validate_text(name, "name")
        if safe_z_mm is None:
            raise ValueError(f"{ReasonCode.UNSAFE_APPROACH.value}: SAFE_Z is required")
        raw_pose: object = cast(object, pose_provider.current_pose())
        if not isinstance(raw_pose, PortCurrentPose):
            raise TypeError("current pose input must be CurrentPose")
        pose = raw_pose
        from xyz_klipper_tool.domain.models import ProviderKind
        from xyz_klipper_tool.domain.units import Millimetres

        if type(provider) is not ProviderKind or type(safe_z_mm) is not Millimetres:
            raise ValueError("provider and SAFE_Z must be typed")
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
    except BaseException:
        try:
            lock.release(token)
        except Exception:  # noqa: BLE001,S110 - cleanup must not mask the primary error
            pass
        raise
    else:
        lock.release(token)
    return record


def _check_fingerprint(expected: str | None, current: str | None) -> None:
    if expected is not None and (type(expected) is not str or not expected.strip()):
        raise ValueError("expected configuration fingerprint must be non-empty")
    if current is not None and (type(current) is not str or not current.strip()):
        raise ValueError("current configuration fingerprint must be non-empty")
    if (expected is None) != (current is None) or (
        expected is not None and expected != current
    ):
        raise ValueError(
            f"{ReasonCode.STALE_STATE.value}: configuration fingerprint mismatch"
        )


def show_stations(
    store: StationStore,
    name: str | None = None,
    expected_configuration_fingerprint: str | None = None,
    current_configuration_fingerprint: str | None = None,
) -> tuple[object, ...]:
    """Read station records without mutation, I/O blocking policy, or writer access."""
    _check_fingerprint(
        expected_configuration_fingerprint, current_configuration_fingerprint
    )
    if name is not None:
        validate_text(name, "name")
        result: list[object] = []
        for namespace in StationType:
            item: object = cast(object, store.get(namespace.value, name))
            if item is not None:
                if not isinstance(item, StationRecord):
                    raise TypeError("corrupt station value")
                result.append(item)
        return tuple(result)
    result = []
    for namespace in StationType:
        for station_name in sorted(store.list(namespace.value)):
            item2: object = cast(object, store.get(namespace.value, station_name))
            if item2 is not None:
                if not isinstance(item2, StationRecord):
                    raise ValueError("corrupt station value")
                result.append(item2)
    return tuple(result)


def clear_station(
    store: StationStore,
    station_type: StationType,
    name: str,
    confirm: str | None = None,
    lock: RunLock | None = None,
    expected_configuration_fingerprint: str | None = None,
    current_configuration_fingerprint: str | None = None,
) -> tuple[object, ...]:
    """Return a preview or perform exact-confirmed removal; no offset writer is called."""
    if lock is None:
        raise ValueError("teach/clear operation requires a run lock")
    token = lock.acquire(RunOperation.TEACH)
    try:
        _check_fingerprint(
            expected_configuration_fingerprint, current_configuration_fingerprint
        )
        if type(station_type) is not StationType:
            raise ValueError("station_type must be typed")
        validate_text(name, "name")
        existing: object = cast(object, store.get(station_type.value, name))
        if existing is None:
            result: tuple[object, ...] = ()
        elif not isinstance(existing, StationRecord):
            raise TypeError("corrupt station value")
        elif confirm is None:
            result = (existing,)
        elif confirm != f"CLEAR:{station_type.value}:{name}":
            raise ValueError(
                f"{ReasonCode.CONFIRMATION_REQUIRED.value}: exact token required"
            )
        else:
            store.remove(station_type.value, name)
            result = (existing,)
    except BaseException:
        try:
            lock.release(token)
        except Exception:  # noqa: BLE001,S110 - cleanup must not mask the primary error
            pass
        raise
    else:
        lock.release(token)
    return result

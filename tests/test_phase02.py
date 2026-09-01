import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, cast

from xyz_klipper_tool.adapters import (
    FakeCamera,
    FakeClock,
    FakeOffsetWriter,
    FakePrinter,
    FakeRunLock,
    FakeStationStore,
    FakeToolchanger,
)
from xyz_klipper_tool.configuration import fingerprint
from xyz_klipper_tool.domain.models import ProviderKind, ToolId
from xyz_klipper_tool.domain.units import CoordinateFrame, Millimetres, Seconds
from xyz_klipper_tool.persistence import JsonStationStore, PersistenceError
from xyz_klipper_tool.ports import RunOperation
from xyz_klipper_tool.stations import (
    CurrentPose,
    StationType,
    clear_station,
    show_stations,
    teach_station,
)
from xyz_klipper_tool.tool_selection import discover_tools
from xyz_klipper_tool.vision import CaptureRequest

try:
    import jsonschema
except ImportError:  # pragma: no cover - exercised by the pinned venv
    jsonschema = None


class Phase02Tests(unittest.TestCase):
    def pose(self) -> CurrentPose:
        return CurrentPose(Millimetres(1), Millimetres(2), Millimetres(3))

    def test_dynamic_tools_are_bounded_and_deterministic(self) -> None:
        adapter = FakeToolchanger([ToolId("T2"), ToolId("T1"), ToolId("T3")])
        self.assertEqual(
            tuple(t.value for t in discover_tools(adapter, ToolId("T3"))),
            ("T3", "T1", "T2"),
        )
        with self.assertRaises(ValueError):
            discover_tools(FakeToolchanger([ToolId("T1"), ToolId("T1")]))
        with self.assertRaises(ValueError):
            discover_tools(FakeToolchanger([ToolId("T1")], ToolId("T1"), ToolId("T2")))
        with self.assertRaises(ValueError):
            discover_tools(FakeToolchanger([ToolId("T1")]))
        with self.assertRaises(ValueError):
            discover_tools(
                FakeToolchanger([ToolId("T1")], ToolId("unknown"), ToolId("unknown")),
                ToolId("T1"),
            )
        with self.assertRaises(ValueError):
            discover_tools(FakeToolchanger([ToolId("T1")]), ToolId("T1"), 0)
        with self.assertRaises(ValueError):
            discover_tools(FakeToolchanger([ToolId("T1")]), ToolId("T1"), 10**100)

    def test_fake_boundaries_reject_untyped_and_oversize_values(self) -> None:
        with self.assertRaises(TypeError):
            CurrentPose(cast(Any, 1), cast(Any, 2), cast(Any, 3))
        with self.assertRaises(TypeError):
            FakePrinter(cast(Any, object()), cast(Any, "ready"))
        with self.assertRaises(ValueError):
            FakeCamera([b"x" * (8 * 1024 * 1024 + 1)]).capture(
                CaptureRequest("device:/dev/video0", Seconds(1), "sample", "camera")
            )

    def test_station_record_rejects_untyped_fields_before_attribute_access(
        self,
    ) -> None:
        values: dict[str, Any] = {
            "pose": cast(Any, object()),
            "safe_z_mm": cast(Any, 5),
            "taught_at_utc": cast(Any, "2026-08-31T00:00:00Z"),
        }
        for field, value in values.items():
            kwargs: dict[str, Any] = {
                "name": "cam",
                "station_type": StationType.CAMERA,
                "provider": ProviderKind.CAMERA,
                "pose": self.pose(),
                "safe_z_mm": Millimetres(5),
                "revision": "r1",
                "taught_at_utc": datetime(2026, 8, 31, tzinfo=timezone.utc),
                "configuration_fingerprint": "fp",
                "provenance": "test",
            }
            kwargs[field] = value
            with self.assertRaises((TypeError, ValueError)):
                from xyz_klipper_tool.stations.models import StationRecord

                StationRecord(**kwargs)

    def test_fingerprint_is_stable_and_redacts_secrets(self) -> None:
        a = fingerprint({"z": 2, "secret_token": "do-not-store", "a": [1, True]})
        b = fingerprint({"a": [1, True], "secret_token": "other", "z": 2})
        self.assertEqual(a, b)
        self.assertNotIn("do-not-store", a.canonical_json)
        with self.assertRaises(ValueError):
            fingerprint(cast(Any, {1: "key"}))
        with self.assertRaises(ValueError):
            type(a)(True, a.digest, a.canonical_json)
        with self.assertRaises(ValueError):
            type(a)(1, "0" * 64, a.canonical_json)

    def test_teach_show_clear_and_safe_z_are_data_only(self) -> None:
        store = FakeStationStore()
        lock = FakeRunLock()
        printer = FakePrinter(self.pose())
        clock = FakeClock(datetime(2026, 8, 31, tzinfo=timezone.utc))
        with self.assertRaises(ValueError):
            teach_station(
                store,
                printer,
                clock,
                "cam",
                ProviderKind.CAMERA,
                "fp",
                "r1",
                "fake-pose",
                None,
                lock,
            )
        record = teach_station(
            store,
            printer,
            clock,
            "cam",
            ProviderKind.CAMERA,
            "fp",
            "r1",
            "fake-pose",
            Millimetres(5),
            lock,
        )
        self.assertEqual(record.pose.frame, CoordinateFrame.MACHINE)
        before = tuple(store.calls)
        self.assertEqual(show_stations(store, "cam", "fp", "fp"), (record,))
        self.assertEqual(tuple(store.calls[: len(before)]), before)
        self.assertEqual(
            clear_station(
                store,
                StationType.CAMERA,
                "cam",
                lock=lock,
                expected_configuration_fingerprint="fp",
                current_configuration_fingerprint="fp",
            ),
            (record,),
        )
        self.assertEqual(
            clear_station(
                store, StationType.CAMERA, "cam", "CLEAR:camera:cam", lock, "fp", "fp"
            ),
            (record,),
        )
        store.records[("camera", "broken")] = object()
        with self.assertRaises(TypeError):
            show_stations(store, "broken", "fp", "fp")

    def test_station_fingerprint_is_checked_before_show_and_clear(self) -> None:
        store = FakeStationStore()
        record = teach_station(
            store,
            FakePrinter(self.pose()),
            FakeClock(datetime(2026, 8, 31, tzinfo=timezone.utc)),
            "cam",
            ProviderKind.CAMERA,
            "old",
            "r1",
            "fake",
            Millimetres(5),
            FakeRunLock(),
        )
        with self.assertRaises(ValueError):
            show_stations(store, current_configuration_fingerprint="new")
        with self.assertRaises(ValueError):
            clear_station(
                store,
                StationType.CAMERA,
                "cam",
                "CLEAR:camera:cam",
                FakeRunLock(),
                "new",
                "new",
            )
        self.assertEqual(store.get("camera", "cam"), record)
        with self.assertRaises(ValueError):
            show_stations(store)

    def test_lock_conflict_and_wrong_release_fail_closed(self) -> None:
        lock = FakeRunLock()
        token = lock.acquire(RunOperation.RUN)
        with self.assertRaises(RuntimeError):
            lock.acquire(RunOperation.TEACH)
        with self.assertRaises(ValueError):
            lock.release(object())
        with self.assertRaises(ValueError):
            lock.release(cast(Any, None))
        with self.assertRaises(ValueError):
            FakeRunLock().release(token)
        lock.release(token)
        with self.assertRaises(ValueError):
            lock.release(cast(Any, None))
        apply_token = lock.acquire(RunOperation.APPLY)
        lock.release(apply_token)

    def test_teach_conflict_releases_after_store_fault(self) -> None:
        lock = FakeRunLock()
        token = lock.acquire(RunOperation.RUN)
        with self.assertRaises(RuntimeError):
            teach_station(
                FakeStationStore(),
                FakePrinter(self.pose()),
                FakeClock(datetime(2026, 8, 31, tzinfo=timezone.utc)),
                "cam",
                ProviderKind.CAMERA,
                "fp",
                "r1",
                "fake",
                Millimetres(5),
                lock,
            )
        lock.release(token)

        class FailingStore(FakeStationStore):
            def put(self, namespace: str, name: str, value: object) -> None:
                raise RuntimeError("primary store fault")

        with self.assertRaisesRegex(RuntimeError, "primary store fault"):
            teach_station(
                FailingStore(),
                FakePrinter(self.pose()),
                FakeClock(datetime(2026, 8, 31, tzinfo=timezone.utc)),
                "cam",
                ProviderKind.CAMERA,
                "fp",
                "r1",
                "fake",
                Millimetres(5),
                lock,
            )
        self.assertIsNone(lock.held)

    def test_atomic_store_rejects_corrupt_and_preserves_previous(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            store = JsonStationStore(root)
            record = teach_station(
                store,
                FakePrinter(self.pose()),
                FakeClock(datetime(2026, 8, 31, tzinfo=timezone.utc)),
                "cam",
                ProviderKind.CAMERA,
                "fp",
                "r1",
                "fake",
                Millimetres(5),
                FakeRunLock(),
            )
            path = root / "camera" / "cam.json"
            original = path.read_text()
            path.write_text(original[:-3])
            with self.assertRaises(PersistenceError):
                store.get("camera", "cam")
            path.write_text(original)
            self.assertEqual(store.get("camera", "cam"), record)
            store.put("camera", "cam", record)
            store.put("camera", "cam", record)
            self.assertTrue((root / "camera" / "cam.json.bak1").exists())
            self.assertTrue((root / "camera" / "cam.json.bak2").exists())
            for stage in (
                "before_temp",
                "after_write",
                "after_flush",
                "after_fsync",
                "before_replace",
                "backup",
                "backup_rotation_2",
                "backup_rotation_1",
            ):
                fault_store = JsonStationStore(root, fault_stage=stage)
                with self.assertRaises((PersistenceError, OSError)):
                    fault_store.put("camera", "cam", record)
                self.assertEqual(store.get("camera", "cam"), record)
            post_commit = JsonStationStore(root, fault_stage="after_replace")
            with self.assertRaises(PersistenceError) as error:
                post_commit.put("camera", "cam", record)
            self.assertTrue(error.exception.committed)
            self.assertEqual(post_commit.reconcile("camera", "cam"), record)
            with self.assertRaises(PersistenceError):
                store.put("switch_z", "cam", record)
            path.write_text('{"schema_version": 2}')
            with self.assertRaises(PersistenceError):
                store.get("camera", "cam")
            self.assertEqual(store.recover("camera", "cam").name, "cam")

    @unittest.skipUnless(
        jsonschema is not None, "jsonschema is required in the pinned venv"
    )
    def test_station_schema_contract_rejects_missing_and_wrong_version(self) -> None:
        schema = __import__("json").loads(
            Path("schemas/station-envelope.v1.schema.json").read_text(encoding="utf-8")
        )
        validator_module: Any = jsonschema
        validator = validator_module.Draft202012Validator(
            schema, format_checker=validator_module.FormatChecker()
        )
        self.assertTrue(validator.check_schema(schema) is None)
        with tempfile.TemporaryDirectory() as directory:
            store = JsonStationStore(Path(directory))
            _record = teach_station(
                store,
                FakePrinter(self.pose()),
                FakeClock(datetime(2026, 8, 31, tzinfo=timezone.utc)),
                "cam",
                ProviderKind.CAMERA,
                "fp",
                "r1",
                "fake",
                Millimetres(5),
                FakeRunLock(),
            )
            valid = __import__("json").loads(
                (Path(directory) / "camera" / "cam.json").read_text()
            )
            self.assertFalse(list(validator.iter_errors(valid)))
            for fault in (
                {**valid, "extra": 1},
                {**valid, "schema_version": "1"},
                {**valid, "record": {**valid["record"], "provider": "switch"}},
                {
                    **valid,
                    "record": {
                        **valid["record"],
                        "taught_at_utc": "2026-08-31T00:00:00+07:00",
                    },
                },
            ):
                self.assertTrue(list(validator.iter_errors(fault)))
        self.assertTrue(list(validator.iter_errors({"schema_version": 2})))

    def test_teach_never_calls_offset_writer(self) -> None:
        writer = FakeOffsetWriter()
        store = FakeStationStore()
        teach_station(
            store,
            FakePrinter(self.pose()),
            FakeClock(datetime(2026, 8, 31, tzinfo=timezone.utc)),
            "cam",
            ProviderKind.CAMERA,
            "fp",
            "r1",
            "fake",
            Millimetres(5),
            FakeRunLock(),
        )
        self.assertEqual(writer.calls, [])


if __name__ == "__main__":
    unittest.main()

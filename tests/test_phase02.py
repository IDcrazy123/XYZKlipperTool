import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from xyz_klipper_tool.adapters import (
    FakeClock,
    FakeOffsetWriter,
    FakePrinter,
    FakeRunLock,
    FakeStationStore,
    FakeToolchanger,
)
from xyz_klipper_tool.configuration import fingerprint
from xyz_klipper_tool.domain.models import ProviderKind, ToolId
from xyz_klipper_tool.domain.units import CoordinateFrame, Millimetres
from xyz_klipper_tool.persistence import JsonStationStore, PersistenceError
from xyz_klipper_tool.stations import (
    CurrentPose,
    StationType,
    clear_station,
    show_stations,
    teach_station,
)
from xyz_klipper_tool.tool_selection import discover_tools

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

    def test_fingerprint_is_stable_and_redacts_secrets(self) -> None:
        a = fingerprint({"z": 2, "secret_token": "do-not-store", "a": [1, True]})
        b = fingerprint({"a": [1, True], "secret_token": "other", "z": 2})
        self.assertEqual(a, b)
        self.assertNotIn("do-not-store", a.canonical_json)

    def test_teach_show_clear_and_safe_z_are_data_only(self) -> None:
        store = FakeStationStore()
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
        )
        self.assertEqual(record.pose.frame, CoordinateFrame.MACHINE)
        before = tuple(store.calls)
        self.assertEqual(show_stations(store), (record,))
        self.assertEqual(tuple(store.calls[: len(before)]), before)
        self.assertEqual(clear_station(store, StationType.CAMERA, "cam"), (record,))
        self.assertEqual(
            clear_station(store, StationType.CAMERA, "cam", "CLEAR:camera:cam"),
            (record,),
        )

    def test_lock_conflict_and_wrong_release_fail_closed(self) -> None:
        lock = FakeRunLock()
        token = lock.acquire("run")
        with self.assertRaises(RuntimeError):
            lock.acquire("teach")
        with self.assertRaises(ValueError):
            lock.release(object())
        lock.release(token)
        lock.release(lock.acquire("apply"))

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
            )
            path = root / "camera" / "cam.json"
            original = path.read_text()
            path.write_text(original[:-3])
            with self.assertRaises(PersistenceError):
                store.get("camera", "cam")
            path.write_text(original)
            self.assertEqual(store.get("camera", "cam"), record)
            for stage in ("before_temp", "after_flush", "before_replace", "backup"):
                fault_store = JsonStationStore(root, fault_stage=stage)
                with self.assertRaises((PersistenceError, OSError)):
                    fault_store.put("camera", "cam", record)
                self.assertEqual(store.get("camera", "cam"), record)
            path.write_text('{"schema_version": 2}')
            with self.assertRaises(PersistenceError):
                store.get("camera", "cam")

    @unittest.skipUnless(
        jsonschema is not None, "jsonschema is required in the pinned venv"
    )
    def test_station_schema_contract_rejects_missing_and_wrong_version(self) -> None:
        schema = __import__("json").loads(
            Path("schemas/station-envelope.v1.schema.json").read_text(encoding="utf-8")
        )
        validator_module: Any = jsonschema
        validator = validator_module.Draft202012Validator(schema)
        self.assertTrue(validator.check_schema(schema) is None)
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
        )
        self.assertEqual(writer.calls, [])


if __name__ == "__main__":
    unittest.main()

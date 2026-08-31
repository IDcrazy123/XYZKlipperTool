import json
import math
import unittest
from pathlib import Path
from typing import Any

from jsonschema import (
    Draft202012Validator,  # pyright: ignore[reportMissingModuleSource]
)

from xyz_klipper_tool.domain.models import (
    Axis,
    CartographerTouchMeasurementResult,
    FrameSampleId,
    MeasurementContext,
    OuterCycleId,
    ProviderKind,
    ReasonCode,
    RunId,
    SwitchZMeasurementResult,
    ToolVisitId,
    Verdict,
)
from xyz_klipper_tool.domain.schema import (
    SchemaPayloadError,
    SchemaVersionError,
    decode_cartographer_result,
    decode_switch_z_result,
    encode_cartographer_result,
    encode_switch_z_result,
)
from xyz_klipper_tool.domain.units import CoordinateFrame, Millimetres, SignConvention


def context(provider: ProviderKind) -> MeasurementContext:
    return MeasurementContext(
        RunId("r"),
        OuterCycleId("c"),
        ToolVisitId("v"),
        FrameSampleId("s"),
        "station",
        "fingerprint",
        "calibration",
        provider,
        Axis.Z,
    )


class SchemaTests(unittest.TestCase):
    def setUp(self) -> None:
        self.switch = SwitchZMeasurementResult(
            context(ProviderKind.SWITCH),
            Millimetres(1.25),
            CoordinateFrame.PROVIDER,
            SignConvention.PROVIDER_REPORTED,
            Verdict.PASS,
            ReasonCode.NONE,
        )
        self.cart = CartographerTouchMeasurementResult(
            context(ProviderKind.CARTOGRAPHER_TOUCH),
            Millimetres(-2.5),
            CoordinateFrame.PROVIDER,
            SignConvention.PROVIDER_REPORTED,
            Verdict.WARNING,
            ReasonCode.PROVIDER_CONTRACT_UNVERIFIED,
        )

    def test_both_provider_round_trips(self) -> None:
        self.assertEqual(
            decode_switch_z_result(encode_switch_z_result(self.switch)), self.switch
        )
        self.assertEqual(
            decode_cartographer_result(encode_cartographer_result(self.cart)), self.cart
        )

    def test_unknown_field_allowed_but_missing_version_malformed_wrong_enum_nonfinite_fail(
        self,
    ) -> None:
        payload = json.loads(encode_switch_z_result(self.switch))
        payload["future"] = True
        self.assertEqual(decode_switch_z_result(json.dumps(payload)), self.switch)
        for bad in (
            {k: v for k, v in payload.items() if k != "schema_version"},
            {**payload, "schema_version": 2},
            {k: v for k, v in payload.items() if k != "provider"},
            {**payload, "run_id": 42},
            {**payload, "axis": "Q"},
            {**payload, "z_offset_mm": float("nan")},
        ):
            with self.assertRaises(
                (SchemaPayloadError, SchemaVersionError, ValueError)
            ):
                decode_switch_z_result(json.dumps(bad))

    def test_json_schema_contract_matches_encoded_payload(self) -> None:
        root = Path(__file__).parents[1]
        for filename, encoded in (
            (
                "switch-measurement-result.v1.schema.json",
                encode_switch_z_result(self.switch),
            ),
            (
                "cartographer-touch-result.v1.schema.json",
                encode_cartographer_result(self.cart),
            ),
        ):
            schema = json.loads((root / "schemas" / filename).read_text())
            payload = json.loads(encoded)
            self.assertEqual(schema["type"], "object")
            for key in schema["required"]:
                self.assertIn(key, payload)
            for key, rule in schema["properties"].items():
                if "const" in rule:
                    self.assertEqual(payload[key], rule["const"])
                if "enum" in rule:
                    self.assertIn(payload[key], rule["enum"])
                if rule.get("type") == "number":
                    self.assertTrue(math.isfinite(payload[key]))

    def test_draft_2020_schema_rejects_negative_instances(self) -> None:
        root = Path(__file__).parents[1]
        cases = (
            (
                "switch-measurement-result.v1.schema.json",
                json.loads(encode_switch_z_result(self.switch)),
            ),
            (
                "cartographer-touch-result.v1.schema.json",
                json.loads(encode_cartographer_result(self.cart)),
            ),
        )
        for filename, positive in cases:
            validator: Any = Draft202012Validator(
                json.loads((root / "schemas" / filename).read_text())
            )
            self.assertEqual(list(validator.iter_errors(positive)), [])
            for field, value in (
                ("run_id", 42),
                ("provider", "other"),
                ("axis", "Q"),
                ("z_offset_mm", "nan"),
            ):
                negative = dict(positive)
                negative[field] = value
                self.assertTrue(
                    list(validator.iter_errors(negative)), (filename, field)
                )
            missing = dict(positive)
            missing.pop("schema_version")
            self.assertTrue(list(validator.iter_errors(missing)))


if __name__ == "__main__":
    unittest.main()

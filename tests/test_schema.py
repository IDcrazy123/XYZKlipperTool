import unittest

from xyz_klipper_tool.domain.models import ReasonCode, RunId, SwitchMeasurementResult, ToolVisitId, Verdict
from xyz_klipper_tool.domain.schema import SchemaVersionError, decode_switch_result, encode_switch_result
from xyz_klipper_tool.domain.units import Vector2Mm


class SchemaTests(unittest.TestCase):
    def setUp(self):
        self.value = SwitchMeasurementResult(RunId("run-1"), ToolVisitId("visit-1"), Vector2Mm(1.25, -2.5),
                                              Verdict.PASS, ReasonCode.NONE)

    def test_round_trip(self):
        self.assertEqual(decode_switch_result(encode_switch_result(self.value)), self.value)

    def test_unknown_field_is_backward_compatible(self):
        payload = encode_switch_result(self.value)[:-1] + ',"future_field":true}'
        self.assertEqual(decode_switch_result(payload), self.value)

    def test_unsupported_version_is_typed_error(self):
        with self.assertRaises(SchemaVersionError):
            decode_switch_result('{"schema_version":99}')


if __name__ == "__main__":
    unittest.main()

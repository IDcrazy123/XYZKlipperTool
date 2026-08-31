import json
import unittest
from pathlib import Path
from typing import cast

from xyz_klipper_tool.domain.models import (
    Axis,
    FrameSampleId,
    Hierarchy,
    OuterCycleId,
    ProviderKind,
    RunId,
    ToolId,
    ToolVisitId,
)
from xyz_klipper_tool.domain.statistics import Observation, summarize
from xyz_klipper_tool.domain.units import Millimetres


class EvidenceFixtureTests(unittest.TestCase):
    def test_t3_fixture_reproduces_evidence_statistics_without_defaulting_domain(
        self,
    ) -> None:
        fixture = json.loads(
            (Path(__file__).parent / "fixtures" / "ktamv-t3-evidence.json").read_text()
        )
        result = summarize(
            [
                Observation(
                    RunId("run"),
                    ToolId("T3"),
                    OuterCycleId(f"cycle-{i + 1}"),
                    ToolVisitId(f"visit-{i + 1}"),
                    FrameSampleId(f"t3-{i}"),
                    "station",
                    "fingerprint",
                    "calibration",
                    ProviderKind.CAMERA,
                    Axis.X,
                    Hierarchy.OUTER_CYCLE,
                    Millimetres(value),
                )
                for i, value in enumerate(fixture["x_mm_values"])
            ]
        )
        self.assertAlmostEqual(
            cast(float, result.filtered.mean_mm), 0.012666666666666666
        )
        self.assertAlmostEqual(cast(float, result.filtered.median_mm), 0.005)
        self.assertEqual(fixture["fixture_kind"], "evidence_only")


if __name__ == "__main__":
    unittest.main()

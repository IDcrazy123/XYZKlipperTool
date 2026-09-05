import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import cv2
import numpy as np


class ArchivedPixelCliTests(unittest.TestCase):
    def make_source(self, root: Path, digest_override: str | None = None) -> Path:
        raw_dir = root / "raw" / "T00" / "L001"
        raw_dir.mkdir(parents=True)
        image = np.zeros((32, 32, 3), dtype=np.uint8)
        cv2.circle(image, (16, 16), 6, (120, 120, 120), -1)
        path = raw_dir / "same.jpg"
        self.assertTrue(cv2.imwrite(str(path), image))
        digest = (
            digest_override
            or __import__("hashlib").sha256(path.read_bytes()).hexdigest()
        )
        manifest = root / "reports" / "canary-manifest.json"
        manifest.parent.mkdir()
        manifest.write_text(
            json.dumps(
                {
                    "frames": [
                        {
                            "raw": "raw/T00/L001/same.jpg",
                            "level": 1,
                            "frame": 1,
                            "sha256": digest,
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )
        return manifest

    def run_cli(
        self,
        root_a: Path,
        manifest_a: Path,
        root_b: Path,
        manifest_b: Path,
        output: Path,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                "scripts/archive_pixel_diagnostics.py",
                "--source-root",
                str(root_a),
                "--source-root",
                str(root_b),
                "--source-manifest",
                str(manifest_a),
                "--source-manifest",
                str(manifest_b),
                "--output",
                str(output),
                "--roi",
                "0",
                "0",
                "32",
                "32",
            ],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_same_basename_gets_two_non_overwriting_overlays(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            a = base / "a"
            b = base / "b"
            ma = self.make_source(a)
            mb = self.make_source(b)
            result = self.run_cli(a, ma, b, mb, base / "out")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(len(list((base / "out/overlays").rglob("*.jpg"))), 4)

    def test_duplicate_manifest_source_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            a = base / "a"
            ma = self.make_source(a)
            result = self.run_cli(a, ma, a, ma, base / "out")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("duplicate manifest", result.stderr)

    def test_existing_output_refuses_without_touching_it(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            a = base / "a"
            ma = self.make_source(a)
            out = base / "out"
            out.mkdir()
            marker = out / "marker"
            marker.write_text("keep", encoding="utf-8")
            result = self.run_cli(a, ma, a, ma, out)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(marker.read_text(encoding="utf-8"), "keep")


if __name__ == "__main__":
    unittest.main()

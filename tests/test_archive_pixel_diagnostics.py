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
                            "capture_status": "WARNING",
                            "corpus_inclusion": "EXCLUDED",
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )
        return manifest

    def make_photo_source(self, root: Path) -> Path:
        session_id = "session-x"
        tool = "T12"
        lighting_id = "L064"
        frame = "F02"
        photo_dir = root / "01_PHOTOS" / session_id / tool
        photo_dir.mkdir(parents=True)
        image = np.zeros((32, 32, 3), dtype=np.uint8)
        cv2.circle(image, (16, 16), 6, (120, 120, 120), -1)
        path = photo_dir / f"{tool}_{lighting_id}_{frame}.jpg"
        self.assertTrue(cv2.imwrite(str(path), image))
        digest = __import__("hashlib").sha256(path.read_bytes()).hexdigest()
        classification = "WARNING_DEVELOPMENT_ONLY_REQUIRES_REVIEW"
        manifest = root / "80_EVIDENCE" / session_id / "manifest.json"
        manifest.parent.mkdir(parents=True)
        manifest.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "session_id": session_id,
                    "status": "CAPTURED_UNREVIEWED",
                    "classification": classification,
                    "accepted_for_calibration": False,
                    "photos": [
                        {
                            "schema_version": 1,
                            "session_id": session_id,
                            "tool": tool,
                            "lighting_id": lighting_id,
                            "frame": frame,
                            "captured_utc": "2026-09-05T15:36:28.2801645Z",
                            "relative_photo_path": (
                                f"01_PHOTOS/{session_id}/{tool}/"
                                f"{tool}_{lighting_id}_{frame}.jpg"
                            ),
                            "sha256": digest,
                            "byte_count": path.stat().st_size,
                            "width_px": 32,
                            "height_px": 32,
                            "content_type": "image/jpeg",
                            "accepted": False,
                            "classification": classification,
                            "ring_brightness_255": 64,
                            "tool_leds": "verified_off",
                        }
                    ],
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

    def run_single(
        self, root: Path, manifest: Path, output: Path
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                "scripts/archive_pixel_diagnostics.py",
                "--source-root",
                str(root),
                "--source-manifest",
                str(manifest),
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

    def test_legacy_invalid_and_new_reason_codes_survive_full_cli(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            root = base / "source"
            manifest = self.make_source(root)
            data = json.loads(manifest.read_text(encoding="utf-8"))
            entry = data["frames"][0]
            entry.update(
                {
                    "capture_status": "INVALID",
                    "invalid_reason": "WRONG_CAMERA_SOURCE",
                    "corpus_inclusion": "EXCLUDED",
                }
            )
            metadata = root / "metadata" / "frame.json"
            metadata.parent.mkdir()
            metadata.write_text(
                json.dumps(
                    {
                        "reason_codes": ["HTTP_EVIDENCE_PERSISTENCE_FAILED"],
                        "claim_status": "WARNING",
                        "captured_at_utc": "2026-09-05T00:00:00Z",
                    }
                ),
                encoding="utf-8",
            )
            entry["metadata"] = "metadata/frame.json"
            manifest.write_text(json.dumps(data), encoding="utf-8")
            result = self.run_single(root, manifest, base / "out")
            self.assertEqual(result.returncode, 0, result.stderr)
            record = json.loads(
                (base / "out/reports.json").read_text(encoding="utf-8")
            )["records"][0]
            self.assertEqual(record["reason"], "HTTP_EVIDENCE_PERSISTENCE_FAILED")
            self.assertEqual(record["raw_http_evidence"], "MISSING")
            self.assertEqual(record["status"], "WARNING")
            legacy_root = base / "legacy"
            legacy_manifest = self.make_source(legacy_root)
            legacy_data = json.loads(legacy_manifest.read_text(encoding="utf-8"))
            legacy_data["frames"][0].update(
                {
                    "capture_status": "INVALID",
                    "invalid_reason": "WRONG_CAMERA_SOURCE",
                    "corpus_inclusion": "EXCLUDED",
                }
            )
            legacy_manifest.write_text(json.dumps(legacy_data), encoding="utf-8")
            legacy_result = self.run_single(
                legacy_root, legacy_manifest, base / "legacy-out"
            )
            self.assertEqual(legacy_result.returncode, 0, legacy_result.stderr)
            legacy_record = json.loads(
                (base / "legacy-out/reports.json").read_text(encoding="utf-8")
            )["records"][0]
            self.assertEqual(legacy_record["status"], "INVALID")
            self.assertEqual(legacy_record["reason"], "WRONG_CAMERA_SOURCE")

    def test_missing_metadata_contract_fails_actionably(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            root = base / "source"
            manifest = self.make_source(root)
            data = json.loads(manifest.read_text(encoding="utf-8"))
            data["frames"][0].pop("capture_status")
            data["frames"][0].pop("corpus_inclusion")
            manifest.write_text(json.dumps(data), encoding="utf-8")
            result = self.run_single(root, manifest, base / "out")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("metadata missing or unsupported", result.stderr)

    def test_malformed_metadata_fails_actionably(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            root = base / "source"
            manifest = self.make_source(root)
            metadata = root / "bad.json"
            metadata.write_text("{not-json", encoding="utf-8")
            data = json.loads(manifest.read_text(encoding="utf-8"))
            data["frames"][0]["metadata"] = "bad.json"
            manifest.write_text(json.dumps(data), encoding="utf-8")
            result = self.run_single(root, manifest, base / "out")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("metadata malformed", result.stderr)

    def test_capture_library_photos_contract_stays_excluded(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            root = base / "source"
            manifest = self.make_photo_source(root)
            result = self.run_single(root, manifest, base / "out")
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads((base / "out/reports.json").read_text(encoding="utf-8"))
            self.assertEqual(len(report["records"]), 1)
            record = report["records"][0]
            self.assertEqual(record["source_manifest_contract"], "photos")
            self.assertEqual(record["session_id"], "session-x")
            self.assertEqual(record["tool"], "T12")
            self.assertEqual(record["lighting_id"], "L064")
            self.assertEqual(record["level_uint8"], 64)
            self.assertEqual(record["frame"], "F02")
            self.assertEqual(record["status"], "WARNING")
            self.assertEqual(record["source_corpus_inclusion"], "EXCLUDED")
            self.assertFalse(record["source_declared_acceptance"])
            self.assertFalse(record["accepted_nozzle"])
            self.assertFalse(record["machine_eligibility"])
            self.assertEqual(len(list((base / "out/overlays").rglob("*.jpg"))), 2)

    def test_capture_library_declared_dimensions_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            root = base / "source"
            manifest = self.make_photo_source(root)
            data = json.loads(manifest.read_text(encoding="utf-8"))
            data["photos"][0]["width_px"] = 31
            manifest.write_text(json.dumps(data), encoding="utf-8")
            result = self.run_single(root, manifest, base / "out")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("decoded dimensions mismatch", result.stderr)

    def test_capture_library_refuses_preaccepted_input(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            root = base / "source"
            manifest = self.make_photo_source(root)
            data = json.loads(manifest.read_text(encoding="utf-8"))
            data["photos"][0]["accepted"] = True
            manifest.write_text(json.dumps(data), encoding="utf-8")
            result = self.run_single(root, manifest, base / "out")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("must remain unaccepted", result.stderr)

    def test_capture_library_path_traversal_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            root = base / "source"
            manifest = self.make_photo_source(root)
            data = json.loads(manifest.read_text(encoding="utf-8"))
            data["photos"][0]["relative_photo_path"] = (
                "01_PHOTOS/ignored/../session-x/T12/T12_L064_F02.jpg"
            )
            manifest.write_text(json.dumps(data), encoding="utf-8")
            result = self.run_single(root, manifest, base / "out")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("contains traversal", result.stderr)

    def test_ambiguous_manifest_collection_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            root = base / "source"
            manifest = self.make_photo_source(root)
            data = json.loads(manifest.read_text(encoding="utf-8"))
            data["frames"] = []
            manifest.write_text(json.dumps(data), encoding="utf-8")
            result = self.run_single(root, manifest, base / "out")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("exactly one of frames/items/photos", result.stderr)

    def test_empty_manifest_collection_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            root = base / "source"
            manifest = self.make_photo_source(root)
            data = json.loads(manifest.read_text(encoding="utf-8"))
            data["photos"] = []
            manifest.write_text(json.dumps(data), encoding="utf-8")
            result = self.run_single(root, manifest, base / "out")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("must not be empty", result.stderr)


if __name__ == "__main__":
    unittest.main()

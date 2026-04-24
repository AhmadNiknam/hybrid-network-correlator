from __future__ import annotations

import json
import os
import unittest
from pathlib import Path
from unittest.mock import patch

from src.evidence.collectors import (
    prepare_connectivity_test_request,
    prepare_packet_capture_request,
    prepare_windows_diagnostics_script_request,
)
from src.evidence.manifest import build_evidence_manifest_from_incident_summary, to_json_dict
from src.evidence.packager import write_manifest_json


class TestEvidenceScaffolding(unittest.TestCase):
    def setUp(self) -> None:
        self.repo_root = Path(__file__).resolve().parents[2]
        self.sample_summary_path = (
            self.repo_root
            / "samples"
            / "sample_outputs"
            / "scenario1_nsg_rule_change_expected_incident_summary.json"
        )

        self.out_dir = (
            self.repo_root / "samples" / "sample_outputs" / "evidence_manifests"
        )
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self._created_files: list[Path] = []

    def tearDown(self) -> None:
        for p in self._created_files:
            try:
                p.unlink(missing_ok=True)
            except TypeError:
                # Python < 3.8 compatibility: missing_ok not present
                if p.exists():
                    p.unlink()

    def _load_sample_summary(self) -> dict:
        with self.sample_summary_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def test_create_manifest_from_sample_summary(self) -> None:
        summary = self._load_sample_summary()

        actions = [
            prepare_packet_capture_request(target="vm-app-01", duration_seconds=60),
            prepare_windows_diagnostics_script_request(target_host="vm-app-01"),
            prepare_connectivity_test_request(
                source="vm-app-01", destination="10.20.30.40", protocol="tcp", port=443
            ),
        ]

        manifest = build_evidence_manifest_from_incident_summary(
            summary,
            timestamp_utc="2026-04-23T12:00:00Z",
            collection_actions=actions,
        )
        payload = to_json_dict(manifest)

        self.assertEqual(payload["incidentId"], "INC-0001")
        self.assertEqual(payload["scenario"], "scenario1_nsg_rule_change")
        self.assertEqual(payload["timestampUtc"], "2026-04-23T12:00:00Z")
        self.assertEqual(payload["topCause"], "NSG_CHANGE")
        self.assertAlmostEqual(payload["confidence"], 0.9)
        self.assertTrue(isinstance(payload["recommendedEvidence"], list))
        self.assertEqual(len(payload["collectionActions"]), 3)
        self.assertTrue(payload["safetyNotes"])

    def test_no_live_action_is_executed(self) -> None:
        summary = self._load_sample_summary()
        manifest = build_evidence_manifest_from_incident_summary(
            summary, timestamp_utc="2026-04-23T12:00:00Z"
        )

        # If any code attempts to execute, these patched calls would fail the test.
        with patch("subprocess.run", side_effect=AssertionError("subprocess.run called")):
            with patch("os.system", side_effect=AssertionError("os.system called")):
                with patch.object(
                    os, "popen", side_effect=AssertionError("os.popen called")
                ):
                    _ = to_json_dict(manifest)
                    _ = prepare_packet_capture_request(target="vm-app-01")
                    _ = prepare_windows_diagnostics_script_request(target_host="vm-app-01")
                    _ = prepare_connectivity_test_request(
                        source="vm-app-01",
                        destination="10.20.30.40",
                        protocol="tcp",
                        port=443,
                    )

    def test_manifest_json_created_correctly(self) -> None:
        summary = self._load_sample_summary()
        manifest = build_evidence_manifest_from_incident_summary(
            summary, timestamp_utc="2026-04-23T12:00:00Z"
        )

        out_path = write_manifest_json(
            manifest,
            repo_root=self.repo_root,
            filename="unit_test_manifest.json",
        )
        self._created_files.append(out_path)

        self.assertTrue(out_path.exists())
        self.assertEqual(out_path.parent.resolve(), self.out_dir.resolve())

        with out_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(data["incidentId"], "INC-0001")
        self.assertEqual(data["timestampUtc"], "2026-04-23T12:00:00Z")
        self.assertIn("safetyNotes", data)


if __name__ == "__main__":
    unittest.main()


from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from src.correlator.loader import load_scenario
from src.correlator.main import main, run


class TestCliOutputFormats(unittest.TestCase):
    def setUp(self) -> None:
        self.repo_root = Path(__file__).resolve().parents[2]
        self.scenario = "scenario1_nsg_rule_change"

    def _run_cli(self, argv: list[str]) -> str:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(argv)
        self.assertEqual(rc, 0)
        return buf.getvalue()

    def test_format_json_matches_run(self) -> None:
        out = self._run_cli(["--scenario", self.scenario, "--format", "json"])
        payload = json.loads(out)
        expected = run(self.scenario, repo_root=self.repo_root)
        self.assertEqual(payload, expected)

    def test_format_dashboard_is_compact_and_stable(self) -> None:
        out = self._run_cli(["--scenario", self.scenario, "--format", "dashboard"])
        payload = json.loads(out)

        # Required keys
        for k in [
            "incidentId",
            "topCause",
            "confidence",
            "severity",
            "impactedTarget",
            "timeWindow",
            "recommendedAction",
            "status",
        ]:
            self.assertIn(k, payload)

        alert, _, _ = load_scenario(self.repo_root, self.scenario)
        self.assertEqual(payload["incidentId"], alert.incidentId)
        self.assertEqual(payload["topCause"], "NSG_CHANGE")
        self.assertIsInstance(payload["confidence"], float)
        self.assertIn(payload["severity"], {"Low", "Medium", "High"})
        self.assertEqual(payload["timeWindow"], {"start": alert.timeWindow.start, "end": alert.timeWindow.end})
        self.assertIn(alert.azureVm.name, payload["impactedTarget"])
        self.assertIn(alert.onPremEndpoint.ipOrFqdn, payload["impactedTarget"])
        self.assertIsInstance(payload["recommendedAction"], str)
        self.assertIsInstance(payload["status"], str)

    def test_format_text_contains_admin_fields(self) -> None:
        out = self._run_cli(["--scenario", self.scenario, "--format", "text"])

        # Must include required admin report components
        self.assertIn("Incident ID:", out)
        self.assertIn("Scenario:", out)
        self.assertIn("Top 3 probable causes:", out)
        self.assertIn("Confidence (top cause):", out)
        self.assertIn("Key evidence:", out)
        self.assertIn("Recommended next checks:", out)
        self.assertIn("Summary:", out)


if __name__ == "__main__":
    unittest.main()


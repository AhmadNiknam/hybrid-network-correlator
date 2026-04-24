from __future__ import annotations

import json
import unittest
from pathlib import Path

from src.correlator.loader import scenario_paths
from src.correlator.main import run


class TestScenarios(unittest.TestCase):
    def setUp(self) -> None:
        self.repo_root = Path(__file__).resolve().parents[2]

    def _load_expected(self, scenario: str) -> dict:
        _, _, _, expected_path = scenario_paths(self.repo_root, scenario)
        with expected_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def _assert_reports_equal(self, actual: dict, expected: dict) -> None:
        # Keep schemaVersion flexible in case we bump later; otherwise exact match.
        actual = dict(actual)
        expected = dict(expected)
        self.assertEqual(actual.get("scenario"), expected.get("scenario"))
        self.assertEqual(actual.get("incidentId"), expected.get("incidentId"))
        self.assertEqual(actual.get("timeWindow"), expected.get("timeWindow"))
        self.assertEqual(actual.get("symptoms"), expected.get("symptoms"))
        self.assertEqual(actual.get("rankedCauses"), expected.get("rankedCauses"))
        self.assertEqual(actual.get("summaryText"), expected.get("summaryText"))

    def test_scenario1_nsg_rule_change(self) -> None:
        scenario = "scenario1_nsg_rule_change"
        actual = run(scenario, repo_root=self.repo_root)
        expected = self._load_expected(scenario)
        self._assert_reports_equal(actual, expected)

    def test_scenario2_udr_route_change(self) -> None:
        scenario = "scenario2_udr_route_change"
        actual = run(scenario, repo_root=self.repo_root)
        expected = self._load_expected(scenario)
        self._assert_reports_equal(actual, expected)

    def test_scenario3_vpn_tunnel_instability(self) -> None:
        scenario = "scenario3_vpn_tunnel_instability"
        actual = run(scenario, repo_root=self.repo_root)
        expected = self._load_expected(scenario)
        self._assert_reports_equal(actual, expected)


if __name__ == "__main__":
    unittest.main()


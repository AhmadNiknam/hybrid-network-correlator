from __future__ import annotations

import unittest

from src.integrations import kql_queries


class TestKqlQueries(unittest.TestCase):
    def test_recent_activity_changes_minutes_substitution(self) -> None:
        q = kql_queries.recent_activity_changes_last_minutes(15)
        self.assertIn("ago(15m)", q)
        self.assertIn("AzureActivity", q)

    def test_connection_failures_minutes_substitution(self) -> None:
        q = kql_queries.connection_failures_last_minutes(5)
        self.assertIn("ago(5m)", q)
        self.assertIn("NetworkDiagnostics", q)

    def test_heartbeat_missing_minutes_substitution(self) -> None:
        q = kql_queries.heartbeat_missing_last_minutes(30)
        self.assertIn("ago(30m)", q)
        self.assertIn("Heartbeat", q)

    def test_high_latency_threshold_and_minutes(self) -> None:
        q = kql_queries.high_latency_indicators_last_minutes(10, threshold_ms=250)
        self.assertIn("ago(10m)", q)
        self.assertIn("LatencyMs >= 250", q)

    def test_minutes_validation(self) -> None:
        with self.assertRaises(ValueError):
            kql_queries.recent_activity_changes_last_minutes(0)

        with self.assertRaises(ValueError):
            kql_queries.connection_failures_last_minutes(-1)

    def test_threshold_validation(self) -> None:
        with self.assertRaises(ValueError):
            kql_queries.high_latency_indicators_last_minutes(5, threshold_ms=0)


if __name__ == "__main__":
    unittest.main()


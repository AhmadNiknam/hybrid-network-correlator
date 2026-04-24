from __future__ import annotations

import os
import unittest

from src.integrations.azure_client import AzureClient


class TestAzureClientGuardrails(unittest.TestCase):
    def setUp(self) -> None:
        self._saved = dict(os.environ)

    def tearDown(self) -> None:
        os.environ.clear()
        os.environ.update(self._saved)

    def test_live_mode_false_by_default_returns_simulated_responses(self) -> None:
        os.environ.pop("LIVE_AZURE_ENABLED", None)
        os.environ.pop("AZURE_TENANT_ID", None)
        os.environ.pop("AZURE_CLIENT_ID", None)
        os.environ.pop("AZURE_CLIENT_SECRET", None)
        os.environ.pop("AZURE_SUBSCRIPTION_ID", None)
        os.environ.pop("LOG_ANALYTICS_WORKSPACE_ID", None)

        client = AzureClient()
        self.assertFalse(client.live_enabled)

        result = client.query_log_analytics(query="SecurityEvent | take 1")
        self.assertEqual(result.source, "mock")
        self.assertEqual(result.rows, [])

        logs = client.get_activity_logs(minutes=15)
        self.assertEqual(logs, [])

    def test_live_mode_true_does_not_perform_live_calls(self) -> None:
        os.environ["LIVE_AZURE_ENABLED"] = "true"
        os.environ.pop("AZURE_TENANT_ID", None)
        os.environ.pop("AZURE_CLIENT_ID", None)
        os.environ.pop("AZURE_CLIENT_SECRET", None)
        os.environ.pop("AZURE_SUBSCRIPTION_ID", None)
        os.environ.pop("LOG_ANALYTICS_WORKSPACE_ID", None)

        client = AzureClient()
        self.assertTrue(client.live_enabled)

        with self.assertRaises(ValueError) as ctx:
            client.query_log_analytics(query="SecurityEvent | take 1")
        self.assertIn("LIVE_AZURE_ENABLED=true", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()


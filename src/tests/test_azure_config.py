from __future__ import annotations

import os
import unittest

from src.integrations.config import load_azure_config


class TestAzureConfig(unittest.TestCase):
    def setUp(self) -> None:
        self._saved = dict(os.environ)

    def tearDown(self) -> None:
        os.environ.clear()
        os.environ.update(self._saved)

    def test_load_non_strict_allows_missing(self) -> None:
        os.environ.pop("AZURE_TENANT_ID", None)
        os.environ.pop("AZURE_CLIENT_ID", None)
        os.environ.pop("AZURE_CLIENT_SECRET", None)
        os.environ.pop("AZURE_SUBSCRIPTION_ID", None)
        os.environ.pop("LOG_ANALYTICS_WORKSPACE_ID", None)

        cfg = load_azure_config(strict=False)
        self.assertFalse(cfg.is_configured)

    def test_load_strict_requires_all(self) -> None:
        os.environ.pop("AZURE_TENANT_ID", None)
        with self.assertRaises(ValueError) as ctx:
            load_azure_config(strict=True)
        self.assertIn("AZURE_TENANT_ID", str(ctx.exception))

    def test_load_reads_expected_env_vars(self) -> None:
        os.environ["AZURE_TENANT_ID"] = "tenant"
        os.environ["AZURE_CLIENT_ID"] = "client"
        os.environ["AZURE_CLIENT_SECRET"] = "secret"
        os.environ["AZURE_SUBSCRIPTION_ID"] = "sub"
        os.environ["LOG_ANALYTICS_WORKSPACE_ID"] = "workspace"

        cfg = load_azure_config(strict=True)
        self.assertTrue(cfg.is_configured)
        self.assertEqual(cfg.tenant_id, "tenant")
        self.assertEqual(cfg.client_id, "client")
        self.assertEqual(cfg.client_secret, "secret")
        self.assertEqual(cfg.subscription_id, "sub")
        self.assertEqual(cfg.log_analytics_workspace_id, "workspace")


if __name__ == "__main__":
    unittest.main()


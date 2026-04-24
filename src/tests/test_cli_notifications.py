from __future__ import annotations

import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from src.correlator.main import main


class TestCliNotifications(unittest.TestCase):
    def _run_cli_stdout(self, argv: list[str]) -> str:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(argv)
        self.assertEqual(rc, 0)
        return buf.getvalue()

    def test_default_notify_none_preserves_text_output(self) -> None:
        out_default = self._run_cli_stdout(["--scenario", "scenario1_nsg_rule_change", "--format", "text"])
        out_explicit = self._run_cli_stdout(
            ["--scenario", "scenario1_nsg_rule_change", "--format", "text", "--notify", "none"]
        )
        self.assertEqual(out_default, out_explicit)
        self.assertNotIn("Notification result (teams)", out_default)

    def test_notify_teams_disabled_does_not_send(self) -> None:
        with patch.dict("os.environ", {"TEAMS_ENABLED": "false"}, clear=True):
            with patch("urllib.request.urlopen", side_effect=AssertionError("network used")):
                out = self._run_cli_stdout(
                    ["--scenario", "scenario1_nsg_rule_change", "--format", "text", "--notify", "teams"]
                )
        self.assertIn("Notification result (teams)", out)
        self.assertIn("simulated=True", out)

    def test_notify_teams_missing_webhook_fails_safely(self) -> None:
        with patch.dict("os.environ", {"NOTIFICATIONS_ENABLED": "true", "TEAMS_ENABLED": "true"}, clear=True):
            with patch("urllib.request.urlopen", side_effect=AssertionError("network used")):
                out = self._run_cli_stdout(
                    ["--scenario", "scenario1_nsg_rule_change", "--format", "text", "--notify", "teams"]
                )
        self.assertIn("Notification result (teams)", out)
        self.assertIn("ok=False", out)
        self.assertIn("simulated=False", out)

    def test_notify_teams_enabled_uses_mocked_network_only_and_no_secrets_in_output(self) -> None:
        secret_url = "https://webhook.example.invalid/teams/VERY_SECRET"

        class _FakeResp:
            status = 200

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

        def _fake_urlopen(req, timeout=None):
            # Ensure we never print/log the URL, and that a network call is made only via this mock.
            self.assertIsNotNone(timeout)
            return _FakeResp()

        with patch.dict(
            "os.environ",
            {"NOTIFICATIONS_ENABLED": "true", "TEAMS_ENABLED": "true", "TEAMS_WEBHOOK_URL": secret_url},
            clear=True,
        ):
            with patch("urllib.request.urlopen", side_effect=_fake_urlopen) as mocked:
                out = self._run_cli_stdout(
                    ["--scenario", "scenario1_nsg_rule_change", "--format", "text", "--notify", "teams"]
                )
                self.assertTrue(mocked.called)

        self.assertIn("Notification result (teams)", out)
        self.assertIn("ok=True", out)
        self.assertIn("simulated=False", out)
        self.assertNotIn("webhook.example.invalid", out)
        self.assertNotIn(secret_url, out)


if __name__ == "__main__":
    unittest.main()


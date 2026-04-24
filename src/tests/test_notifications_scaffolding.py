from __future__ import annotations

import json
import socket
import unittest
from pathlib import Path
from unittest.mock import patch
from src.notifications.config import load_notification_config
from src.notifications.dispatcher import (
    dispatch_notification,
    prepare_email_notification,
    prepare_sms_notification,
    prepare_webhook_notification,
)
from src.notifications.models import NotificationChannel, NotificationRecipient
from src.notifications.templates import (
    render_email_incident_report,
    render_sms_alert,
    render_webhook_payload,
)


class TestNotificationScaffolding(unittest.TestCase):
    def setUp(self) -> None:
        self.repo_root = Path(__file__).resolve().parents[2]
        self.sample_summary_path = (
            self.repo_root
            / "samples"
            / "sample_outputs"
            / "scenario1_nsg_rule_change_expected_incident_summary.json"
        )

    def _load_sample_incident_summary(self) -> dict:
        with self.sample_summary_path.open("r", encoding="utf-8") as f:
            raw = json.load(f)
        # Templates expect the "dashboard-style" keys too; synthesize minimal values.
        top = (raw.get("rankedCauses") or [{}])[0]
        raw["topCause"] = str(top.get("cause", "UNKNOWN"))
        raw["confidence"] = float(top.get("confidence", 0.0) or 0.0)
        raw.setdefault("severity", "High")
        raw.setdefault(
            "recommendedAction",
            ((top.get("nextChecks") or ["Collect additional evidence."])[0]),
        )
        return raw

    def test_config_loading_missing_env_vars_is_ok(self) -> None:
        with patch.dict("os.environ", {}, clear=True):
            cfg = load_notification_config()
        self.assertFalse(cfg.enabled)
        self.assertIsNone(cfg.adminEmail)
        self.assertIsNone(cfg.adminPhoneE164)
        self.assertIsNone(cfg.adminWebhookUrl)

    def test_templates_generate_expected_fields(self) -> None:
        summary = self._load_sample_incident_summary()

        sms = render_sms_alert(incident_summary=summary, evidence_manifest_path="samples/x.json")
        self.assertIn("INCIDENT", sms)
        self.assertIn(summary["incidentId"], sms)
        self.assertIn("cause=", sms)
        self.assertIn("conf=", sms)
        self.assertIn("evidence=samples/x.json", sms)

        subject, email_body = render_email_incident_report(
            incident_summary=summary,
            evidence_manifest_path="samples/x.json",
        )
        self.assertIn(summary["incidentId"], subject)
        self.assertIn(summary["topCause"], subject)
        self.assertIn("incidentId:", email_body)
        self.assertIn("topCause:", email_body)
        self.assertIn("confidence:", email_body)
        self.assertIn("severity:", email_body)
        self.assertIn("recommendedAction:", email_body)
        self.assertIn("evidenceManifestPath:", email_body)

        payload = render_webhook_payload(
            incident_summary=summary,
            evidence_manifest_path="samples/x.json",
        )
        for k in ["incidentId", "topCause", "confidence", "severity", "recommendedAction", "evidenceManifestPath"]:
            self.assertIn(k, payload)

    def test_templates_omit_evidence_manifest_path_when_missing(self) -> None:
        summary = self._load_sample_incident_summary()
        sms = render_sms_alert(incident_summary=summary, evidence_manifest_path=None)
        self.assertNotIn("evidenceManifestPath", sms)
        self.assertNotIn("evidence=", sms)

        _, email_body = render_email_incident_report(incident_summary=summary, evidence_manifest_path=None)
        self.assertNotIn("evidenceManifestPath:", email_body)

        payload = render_webhook_payload(incident_summary=summary, evidence_manifest_path=None)
        self.assertNotIn("evidenceManifestPath", payload)

    def test_simulated_dispatch_when_disabled(self) -> None:
        summary = self._load_sample_incident_summary()
        recipient = NotificationRecipient(channel=NotificationChannel.EMAIL, address="admin@example.invalid")
        msg = prepare_email_notification(incident_summary=summary, recipient=recipient)

        with patch.dict("os.environ", {}, clear=True):
            result = dispatch_notification(message=msg, recipient=recipient)

        self.assertTrue(result.ok)
        self.assertTrue(result.simulated)
        self.assertEqual(result.status, "simulated")

    def test_enabled_dispatch_is_not_implemented_and_does_not_send(self) -> None:
        summary = self._load_sample_incident_summary()
        recipient = NotificationRecipient(channel=NotificationChannel.WEBHOOK, address="https://example.invalid/hook")
        msg = prepare_webhook_notification(incident_summary=summary, recipient=recipient)

        # Still safe by default: Teams is disabled unless TEAMS_ENABLED=true and a webhook URL is set.
        # If any delivery mechanism is attempted, these patched calls should fail.
        with patch.dict("os.environ", {"NOTIFICATIONS_ENABLED": "true"}, clear=True):
            with patch("smtplib.SMTP", side_effect=AssertionError("SMTP used")):
                with patch("urllib.request.urlopen", side_effect=AssertionError("urlopen used")):
                    with patch("http.client.HTTPSConnection", side_effect=AssertionError("HTTPSConnection used")):
                        with patch.object(
                            socket,
                            "create_connection",
                            side_effect=AssertionError("socket connection used"),
                        ):
                            result = dispatch_notification(message=msg, recipient=recipient)

        self.assertTrue(result.ok)
        self.assertTrue(result.simulated)
        self.assertEqual(result.status, "simulated")

    def test_teams_enabled_missing_webhook_fails_safely(self) -> None:
        summary = self._load_sample_incident_summary()
        recipient = NotificationRecipient(channel=NotificationChannel.WEBHOOK, address="https://example.invalid/hook")
        msg = prepare_webhook_notification(incident_summary=summary, recipient=recipient)

        with patch.dict(
            "os.environ",
            {"NOTIFICATIONS_ENABLED": "true", "TEAMS_ENABLED": "true"},
            clear=True,
        ):
            with patch("urllib.request.urlopen", side_effect=AssertionError("urlopen used")):
                result = dispatch_notification(message=msg, recipient=recipient)

        self.assertFalse(result.ok)
        self.assertFalse(result.simulated)
        self.assertEqual(result.status, "failed")
        self.assertIn("TEAMS_WEBHOOK_URL", result.detail)

    def test_teams_enabled_sends_via_urllib_and_does_not_expose_url(self) -> None:
        summary = self._load_sample_incident_summary()
        recipient = NotificationRecipient(channel=NotificationChannel.WEBHOOK, address="https://example.invalid/hook")
        msg = prepare_webhook_notification(incident_summary=summary, recipient=recipient)

        class _FakeResp:
            status = 200

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

        def _fake_urlopen(req, timeout=None):
            # Assert we never accidentally try to hit a real network URL from the message/recipient.
            self.assertNotIn("https://example.invalid/hook", getattr(req, "full_url", ""))
            self.assertIsNotNone(timeout)
            return _FakeResp()

        with patch.dict(
            "os.environ",
            {
                "NOTIFICATIONS_ENABLED": "true",
                "TEAMS_ENABLED": "true",
                "TEAMS_WEBHOOK_URL": "https://webhook.example.invalid/teams",
            },
            clear=True,
        ):
            with patch("urllib.request.urlopen", side_effect=_fake_urlopen) as mocked:
                result = dispatch_notification(message=msg, recipient=recipient)
                self.assertTrue(mocked.called)

        self.assertTrue(result.ok)
        self.assertFalse(result.simulated)
        self.assertEqual(result.status, "sent")
        self.assertNotIn("webhook.example.invalid", result.detail)

    def test_prepare_functions_match_channel(self) -> None:
        summary = self._load_sample_incident_summary()

        email_r = NotificationRecipient(channel=NotificationChannel.EMAIL, address="admin@example.invalid")
        sms_r = NotificationRecipient(channel=NotificationChannel.SMS, address="+15551234567")
        wh_r = NotificationRecipient(channel=NotificationChannel.WEBHOOK, address="https://example.invalid/hook")

        email_m = prepare_email_notification(incident_summary=summary, recipient=email_r)
        sms_m = prepare_sms_notification(incident_summary=summary, recipient=sms_r)
        wh_m = prepare_webhook_notification(incident_summary=summary, recipient=wh_r)

        self.assertEqual(email_m.channel, NotificationChannel.EMAIL)
        self.assertEqual(sms_m.channel, NotificationChannel.SMS)
        self.assertEqual(wh_m.channel, NotificationChannel.WEBHOOK)


if __name__ == "__main__":
    unittest.main()


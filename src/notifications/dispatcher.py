from __future__ import annotations

from typing import Any, Dict, Optional

from .config import NotificationConfig, load_notification_config
from .models import (
    NotificationChannel,
    NotificationDispatchResult,
    NotificationMessage,
    NotificationRecipient,
)
from .templates import render_email_incident_report, render_sms_alert, render_webhook_payload


def prepare_email_notification(
    *,
    incident_summary: Dict[str, Any],
    recipient: NotificationRecipient,
    evidence_manifest_path: Optional[str] = None,
) -> NotificationMessage:
    subject, body = render_email_incident_report(
        incident_summary=incident_summary,
        evidence_manifest_path=evidence_manifest_path,
    )
    return NotificationMessage(
        channel=NotificationChannel.EMAIL,
        incidentId=str(incident_summary.get("incidentId", "")),
        subject=subject,
        bodyText=body,
        metadata={"to": recipient.address},
    )


def prepare_sms_notification(
    *,
    incident_summary: Dict[str, Any],
    recipient: NotificationRecipient,
    evidence_manifest_path: Optional[str] = None,
) -> NotificationMessage:
    text = render_sms_alert(
        incident_summary=incident_summary,
        evidence_manifest_path=evidence_manifest_path,
    )
    return NotificationMessage(
        channel=NotificationChannel.SMS,
        incidentId=str(incident_summary.get("incidentId", "")),
        bodyText=text,
        metadata={"to": recipient.address},
    )


def prepare_webhook_notification(
    *,
    incident_summary: Dict[str, Any],
    recipient: NotificationRecipient,
    evidence_manifest_path: Optional[str] = None,
) -> NotificationMessage:
    payload = render_webhook_payload(
        incident_summary=incident_summary,
        evidence_manifest_path=evidence_manifest_path,
    )
    return NotificationMessage(
        channel=NotificationChannel.WEBHOOK,
        incidentId=str(incident_summary.get("incidentId", "")),
        webhookPayload=payload,
        metadata={"url": recipient.address},
    )


def dispatch_notification(
    *,
    message: NotificationMessage,
    recipient: NotificationRecipient,
    config: Optional[NotificationConfig] = None,
) -> NotificationDispatchResult:
    """
    Safe dispatcher placeholder.

    - If NOTIFICATIONS_ENABLED is not true, returns a simulated dispatch result.
    - If NOTIFICATIONS_ENABLED is true, still does not send anything; it returns a
      "live dispatch not implemented" result.
    """
    cfg = config or load_notification_config()

    if not cfg.enabled:
        return NotificationDispatchResult(
            channel=message.channel,
            recipient=recipient,
            status="simulated",
            ok=True,
            detail="Notifications disabled (NOTIFICATIONS_ENABLED not true); simulated dispatch only.",
            messageId=None,
            simulated=True,
        )

    return NotificationDispatchResult(
        channel=message.channel,
        recipient=recipient,
        status="live_dispatch_not_implemented",
        ok=False,
        detail="NOTIFICATIONS_ENABLED=true but live dispatch is not implemented; no message was sent.",
        messageId=None,
        simulated=False,
    )


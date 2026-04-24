from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any, Dict, Optional

from .config import NotificationConfig, load_notification_config
from .models import (
    NotificationChannel,
    NotificationDispatchResult,
    NotificationMessage,
    NotificationRecipient,
)
from .templates import render_email_incident_report, render_sms_alert, render_webhook_payload


def _parse_bool(value: Optional[str]) -> bool:
    if value is None:
        return False
    v = value.strip().lower()
    return v in {"1", "true", "yes", "y", "on"}


def _is_teams_webhook_channel(message: NotificationMessage, recipient: NotificationRecipient) -> bool:
    # Requirement: only send real Teams delivery when channel is "teams/webhook".
    # Keep existing NotificationChannel.WEBHOOK, and use metadata routing.
    return (
        message.channel == NotificationChannel.WEBHOOK
        and recipient.channel == NotificationChannel.WEBHOOK
        and str(message.metadata.get("channel", "")).strip().lower() == "teams/webhook"
    )


def _to_teams_messagecard(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert the internal compact webhook payload into a Teams MessageCard.
    This format is accepted by classic "Incoming Webhook" connectors and many
    workflow-based webhook endpoints.
    """
    incident_id = str(payload.get("incidentId") or "UNKNOWN")
    severity = str(payload.get("severity") or "Unknown")
    top_cause = str(payload.get("topCause") or "UNKNOWN")
    confidence = str(payload.get("confidence") if payload.get("confidence") is not None else "0.0")
    recommended = str(payload.get("recommendedAction") or "")
    evidence = str(payload.get("evidenceManifestPath") or "")

    theme_color = {"High": "D13438", "Medium": "FFAA44", "Low": "2D7D46"}.get(severity, "0078D4")

    facts = [
        {"name": "Incident", "value": incident_id},
        {"name": "Severity", "value": severity},
        {"name": "Top cause", "value": top_cause},
        {"name": "Confidence", "value": confidence},
    ]
    if recommended:
        facts.append({"name": "Recommended action", "value": recommended})
    if evidence:
        facts.append({"name": "Evidence", "value": evidence})

    return {
        "@type": "MessageCard",
        "@context": "https://schema.org/extensions",
        "summary": f"Incident {incident_id} ({severity})",
        "themeColor": theme_color,
        "title": f"[{severity}] Incident {incident_id} — {top_cause}",
        "sections": [{"facts": facts, "markdown": True}],
    }


def _send_teams_webhook(
    *,
    webhook_url: str,
    payload: Dict[str, Any],
    timeout_seconds: float,
) -> tuple[bool, str]:
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        webhook_url,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "User-Agent": "hybrid-network-correlator/teams-webhook",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout_seconds) as resp:
            status = getattr(resp, "status", None)
            ok = (status is None) or (200 <= int(status) < 300)
            return ok, f"HTTP {status}" if status is not None else "OK"
    except urllib.error.HTTPError as e:
        return False, f"HTTPError {getattr(e, 'code', 'unknown')}"
    except urllib.error.URLError:
        return False, "URLError (connection failed)"
    except Exception:
        return False, "Unexpected error while sending Teams webhook"


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
        # Route webhooks to Teams by default in this MVP scaffolding.
        metadata={"url": recipient.address, "channel": "teams/webhook"},
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

    # Teams webhook delivery (real) is allowed only when explicitly enabled and routed.
    if _is_teams_webhook_channel(message, recipient):
        if not cfg.teamsEnabled:
            return NotificationDispatchResult(
                channel=message.channel,
                recipient=recipient,
                status="simulated",
                ok=True,
                detail="Teams disabled (TEAMS_ENABLED not true); simulated dispatch only.",
                messageId=None,
                simulated=True,
            )

        if not cfg.teamsWebhookUrl:
            return NotificationDispatchResult(
                channel=message.channel,
                recipient=recipient,
                status="failed",
                ok=False,
                detail="TEAMS_ENABLED=true but TEAMS_WEBHOOK_URL is missing; no message was sent.",
                messageId=None,
                simulated=False,
            )

        timeout_raw = (message.metadata.get("timeoutSeconds") or "").__str__().strip()
        timeout_s = 5.0
        if timeout_raw:
            try:
                timeout_s = float(timeout_raw)
            except ValueError:
                timeout_s = 5.0

        internal_payload = message.webhookPayload or {}
        teams_payload = _to_teams_messagecard(internal_payload)
        ok, detail = _send_teams_webhook(
            webhook_url=str(cfg.teamsWebhookUrl),
            payload=teams_payload,
            timeout_seconds=timeout_s,
        )
        return NotificationDispatchResult(
            channel=message.channel,
            recipient=recipient,
            status="sent" if ok else "failed",
            ok=ok,
            detail=f"Teams webhook dispatch: {detail}",
            messageId=None,
            simulated=False,
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


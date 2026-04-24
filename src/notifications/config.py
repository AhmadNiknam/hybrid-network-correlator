from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional


def _parse_bool(value: Optional[str]) -> bool:
    if value is None:
        return False
    v = value.strip().lower()
    return v in {"1", "true", "yes", "y", "on"}


@dataclass(frozen=True)
class NotificationConfig:
    emailEnabled: bool = False
    teamsEnabled: bool = False

    # Shared / routing fields (optional in MVP)
    adminEmail: Optional[str] = None
    teamsWebhookUrl: Optional[str] = None

    # SMTP scaffolding fields (optional; no live delivery yet)
    smtpHost: Optional[str] = None
    smtpPort: int = 587
    smtpUsername: Optional[str] = None
    smtpPassword: Optional[str] = None
    emailFrom: Optional[str] = None


def load_notification_config(env: Optional[dict[str, str]] = None) -> NotificationConfig:
    """
    Load notification configuration from environment variables.

    All variables are optional; missing values should not break tests.
    """
    source = env if env is not None else os.environ

    admin_email = source.get("ADMIN_EMAIL") or None
    teams_webhook = source.get("TEAMS_WEBHOOK_URL") or None

    email_enabled = _parse_bool(source.get("EMAIL_ENABLED"))
    teams_enabled = _parse_bool(source.get("TEAMS_ENABLED"))

    smtp_host = source.get("SMTP_HOST") or None
    smtp_port_raw = source.get("SMTP_PORT")
    smtp_port = 587
    if smtp_port_raw:
        try:
            smtp_port = int(str(smtp_port_raw).strip())
        except ValueError:
            smtp_port = 587
    smtp_username = source.get("SMTP_USERNAME") or None
    smtp_password = source.get("SMTP_PASSWORD") or None
    email_from = source.get("EMAIL_FROM") or None

    return NotificationConfig(
        emailEnabled=email_enabled,
        teamsEnabled=teams_enabled,
        adminEmail=admin_email,
        teamsWebhookUrl=teams_webhook,
        smtpHost=smtp_host,
        smtpPort=smtp_port,
        smtpUsername=smtp_username,
        smtpPassword=smtp_password,
        emailFrom=email_from,
    )


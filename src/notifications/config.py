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
    enabled: bool
    adminEmail: Optional[str] = None
    adminPhoneE164: Optional[str] = None
    adminWebhookUrl: Optional[str] = None


def load_notification_config(env: Optional[dict[str, str]] = None) -> NotificationConfig:
    """
    Load notification configuration from environment variables.

    All variables are optional; missing values should not break tests.
    """
    source = env if env is not None else os.environ

    enabled = _parse_bool(source.get("NOTIFICATIONS_ENABLED"))
    admin_email = source.get("ADMIN_EMAIL") or None
    admin_phone = source.get("ADMIN_PHONE_E164") or None
    admin_webhook = source.get("ADMIN_WEBHOOK_URL") or None

    return NotificationConfig(
        enabled=enabled,
        adminEmail=admin_email,
        adminPhoneE164=admin_phone,
        adminWebhookUrl=admin_webhook,
    )


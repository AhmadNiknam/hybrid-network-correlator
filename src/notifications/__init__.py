"""
Notification scaffolding (prepare-only).

This package defines data models, templates, configuration loading, and a
dispatcher that *does not* send any real messages yet.
"""

from .config import NotificationConfig, load_notification_config
from .dispatcher import (
    dispatch_notification,
    prepare_email_notification,
    prepare_sms_notification,
    prepare_webhook_notification,
)
from .models import (
    NotificationChannel,
    NotificationDispatchResult,
    NotificationMessage,
    NotificationRecipient,
)

__all__ = [
    "NotificationChannel",
    "NotificationConfig",
    "NotificationDispatchResult",
    "NotificationMessage",
    "NotificationRecipient",
    "dispatch_notification",
    "load_notification_config",
    "prepare_email_notification",
    "prepare_sms_notification",
    "prepare_webhook_notification",
]


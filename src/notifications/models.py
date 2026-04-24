from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional


class NotificationChannel(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    WEBHOOK = "webhook"


@dataclass(frozen=True)
class NotificationRecipient:
    channel: NotificationChannel
    address: str
    displayName: Optional[str] = None


@dataclass(frozen=True)
class NotificationMessage:
    channel: NotificationChannel
    incidentId: str
    subject: Optional[str] = None
    bodyText: Optional[str] = None
    bodyHtml: Optional[str] = None
    webhookPayload: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class NotificationDispatchResult:
    channel: NotificationChannel
    recipient: NotificationRecipient
    status: str
    ok: bool
    detail: str
    messageId: Optional[str] = None
    simulated: bool = True


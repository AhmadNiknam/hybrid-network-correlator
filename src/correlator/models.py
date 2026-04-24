from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class ProbableCause(str, Enum):
    NSG_CHANGE = "NSG_CHANGE"
    ROUTE_UDR_CHANGE = "ROUTE_UDR_CHANGE"
    VPN_GATEWAY_ISSUE = "VPN_GATEWAY_ISSUE"
    DNS_ISSUE = "DNS_ISSUE"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class TimeWindow:
    start: str
    end: str


@dataclass(frozen=True)
class AzureVm:
    name: str
    resourceId: str


@dataclass(frozen=True)
class OnPremEndpoint:
    ipOrFqdn: str
    protocol: Optional[str] = None
    port: Optional[int] = None


@dataclass(frozen=True)
class AlertPayload:
    schemaVersion: str
    scenario: str
    incidentId: str
    timeWindow: TimeWindow
    azureVm: AzureVm
    onPremEndpoint: OnPremEndpoint
    symptoms: List[str]


@dataclass(frozen=True)
class ActivityEvent:
    eventId: str
    timestamp: str
    operationName: str
    resourceId: str
    status: str
    caller: str
    summary: str


@dataclass(frozen=True)
class ActivityLog:
    schemaVersion: str
    scenario: str
    events: List[ActivityEvent]


@dataclass(frozen=True)
class TelemetryObservation:
    observationId: str
    timestamp: str
    type: str
    result: str
    details: Optional[str] = None
    target: Optional[str] = None
    query: Optional[str] = None
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TelemetryBundle:
    schemaVersion: str
    scenario: str
    observations: List[TelemetryObservation]


@dataclass
class RankedCause:
    cause: ProbableCause
    score: int
    confidence: float
    evidenceSupport: List[str] = field(default_factory=list)
    evidenceAgainst: List[str] = field(default_factory=list)
    nextChecks: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class IncidentSummary:
    schemaVersion: str
    scenario: str
    incidentId: str
    timeWindow: TimeWindow
    symptoms: List[str]
    rankedCauses: List[RankedCause]
    summaryText: str


def as_str_list(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(x) for x in value]
    return [str(value)]


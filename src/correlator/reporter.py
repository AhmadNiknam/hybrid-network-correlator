from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict, List

from .models import ActivityLog, AlertPayload, IncidentSummary, ProbableCause, RankedCause, TelemetryBundle


def build_summary_text(alert: AlertPayload, ranked: List[RankedCause]) -> str:
    top = ranked[0]
    vm = alert.azureVm.name
    endpoint = alert.onPremEndpoint.ipOrFqdn
    port = alert.onPremEndpoint.port
    port_s = f":{port}" if port is not None else ""

    cause_phrase = {
        ProbableCause.NSG_CHANGE: "a recent NSG rule change is blocking traffic",
        ProbableCause.ROUTE_UDR_CHANGE: "a recent route/UDR change altered the path and degraded connectivity",
        ProbableCause.VPN_GATEWAY_ISSUE: "VPN gateway/tunnel instability is impacting connectivity",
        ProbableCause.DNS_ISSUE: "a DNS/name resolution issue is preventing reliable connectivity",
        ProbableCause.UNKNOWN: "the available evidence is insufficient to identify a specific root cause",
    }[top.cause]

    # Keep it short and admin-friendly; reference a couple evidence IDs when present.
    support_ids = _extract_ids(top.evidenceSupport)[:3]
    against_ids = _extract_ids(top.evidenceAgainst)[:2]

    parts: List[str] = []
    parts.append(
        f"Probable cause: {cause_phrase} between {vm} and {endpoint}{port_s}."
    )
    if support_ids:
        parts.append(f"Supporting evidence: {', '.join(support_ids)}.")
    if against_ids:
        parts.append(f"Counter-evidence: {', '.join(against_ids)}.")

    return " ".join(parts)


def build_incident_summary(
    *,
    schema_version: str,
    alert: AlertPayload,
    ranked: List[RankedCause],
) -> IncidentSummary:
    return IncidentSummary(
        schemaVersion=schema_version,
        scenario=alert.scenario,
        incidentId=alert.incidentId,
        timeWindow=alert.timeWindow,
        symptoms=alert.symptoms,
        rankedCauses=ranked,
        summaryText=build_summary_text(alert, ranked),
    )


def to_json_dict(summary: IncidentSummary) -> Dict[str, Any]:
    raw = asdict(summary)
    # Serialize Enum values as strings
    for rc in raw.get("rankedCauses", []):
        if isinstance(rc.get("cause"), ProbableCause):
            rc["cause"] = rc["cause"].value
        else:
            rc["cause"] = str(rc["cause"])
    return raw


def _extract_ids(lines: List[str]) -> List[str]:
    ids: List[str] = []
    for line in lines:
        for token in line.replace(":", " ").replace("(", " ").replace(")", " ").split():
            if token.startswith("act-") or token.startswith("obs-"):
                ids.append(token)
    return ids


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


def render_admin_text(*, alert: AlertPayload, ranked: List[RankedCause], incident_summary: Dict[str, Any]) -> str:
    """
    Human-readable administrator report (text mode).
    """
    incident_id = incident_summary.get("incidentId", alert.incidentId)
    scenario = incident_summary.get("scenario", alert.scenario)
    time_window = incident_summary.get("timeWindow", asdict(alert.timeWindow))
    summary_sentence = incident_summary.get("summaryText", "") or ""

    vm = alert.azureVm.name
    endpoint = alert.onPremEndpoint.ipOrFqdn
    port = alert.onPremEndpoint.port
    port_s = f":{port}" if port is not None else ""
    impacted = f"{vm} -> {endpoint}{port_s}"

    top3 = ranked[:3] if ranked else []
    top = top3[0] if top3 else None
    top_conf = (top.confidence if top else 0.0)

    evidence_lines: List[str] = []
    if top is not None:
        # Keep evidence focused: first few support lines + any counter-evidence (first 1-2)
        for s in (top.evidenceSupport or [])[:4]:
            evidence_lines.append(f"- {s}")
        for a in (top.evidenceAgainst or [])[:2]:
            evidence_lines.append(f"- (counter) {a}")

    next_checks = (top.nextChecks if top is not None else []) or []
    if not next_checks:
        next_checks = ["Collect additional evidence (NSG effective rules, routes, VPN health, DNS resolution)"]

    lines: List[str] = []
    lines.append("Hybrid Network Correlator — Admin Report")
    lines.append("")
    lines.append(f"Incident ID: {incident_id}")
    lines.append(f"Scenario: {scenario}")
    lines.append(f"Impacted target: {impacted}")
    lines.append(f"Time window: {time_window.get('start', '')} to {time_window.get('end', '')}")
    lines.append("")

    lines.append("Top 3 probable causes:")
    if top3:
        for i, rc in enumerate(top3, start=1):
            lines.append(f"{i}. {rc.cause.value} (confidence={rc.confidence:.2f}, score={rc.score})")
    else:
        lines.append("1. UNKNOWN (confidence=0.00, score=0)")
    lines.append("")

    lines.append(f"Confidence (top cause): {top_conf:.2f}")
    lines.append("")

    lines.append("Key evidence:")
    if evidence_lines:
        lines.extend(evidence_lines)
    else:
        lines.append("- No key evidence captured in current window.")
    lines.append("")

    lines.append("Recommended next checks:")
    for c in next_checks[:5]:
        lines.append(f"- {c}")
    lines.append("")

    if summary_sentence:
        lines.append("Summary:")
        lines.append(summary_sentence)
    else:
        lines.append("Summary:")
        lines.append("No summary sentence was produced.")

    return "\n".join(lines).rstrip() + "\n"


def to_dashboard_dict(
    *,
    alert: AlertPayload,
    ranked: List[RankedCause],
    incident_summary: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Dashboard-friendly compact JSON summary.
    """
    top = ranked[0] if ranked else RankedCause(cause=ProbableCause.UNKNOWN, score=0, confidence=0.0)

    confidence = float(getattr(top, "confidence", 0.0) or 0.0)
    if top.cause == ProbableCause.UNKNOWN:
        severity = "Low"
        status = "NeedsEvidence"
    elif confidence >= 0.75:
        severity = "High"
        status = "ActionRequired"
    elif confidence >= 0.4:
        severity = "Medium"
        status = "Review"
    else:
        severity = "Low"
        status = "Monitor"

    vm = alert.azureVm.name
    endpoint = alert.onPremEndpoint.ipOrFqdn
    port = alert.onPremEndpoint.port
    port_s = f":{port}" if port is not None else ""

    recommended = None
    if getattr(top, "nextChecks", None):
        recommended = (top.nextChecks or [None])[0]
    if not recommended:
        recommended = "Collect additional evidence and validate current effective configuration."

    return {
        "incidentId": incident_summary.get("incidentId", alert.incidentId),
        "topCause": top.cause.value,
        "confidence": confidence,
        "severity": severity,
        "impactedTarget": f"{vm} -> {endpoint}{port_s}",
        "timeWindow": incident_summary.get("timeWindow", asdict(alert.timeWindow)),
        "recommendedAction": recommended,
        "status": status,
    }


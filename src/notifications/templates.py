from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple


def _get(summary: Dict[str, Any], key: str, default: str = "") -> str:
    v = summary.get(key, default)
    return default if v is None else str(v)


def _humanize_cause(value: str) -> str:
    v = (value or "").strip()
    if not v:
        return "Unknown"
    mapping = {
        "NSG_CHANGE": "Probable NSG Change",
        "ROUTE_UDR_CHANGE": "Probable Route/UDR Change",
        "VPN_GATEWAY_ISSUE": "Probable VPN Gateway Issue",
        "DNS_ISSUE": "Probable DNS Issue",
        "UNKNOWN": "Unknown / Needs Evidence",
    }
    if v in mapping:
        return mapping[v]
    return v.replace("_", " ").title()


def _top_evidence_lines(summary: Dict[str, Any], limit: int = 4) -> List[str]:
    ranked = summary.get("rankedCauses") or []
    if not isinstance(ranked, list) or not ranked:
        return []
    top = ranked[0] if isinstance(ranked[0], dict) else {}
    lines = top.get("evidenceSupport") or []
    if not isinstance(lines, list):
        return []
    out: List[str] = []
    for s in lines[:limit]:
        if s is None:
            continue
        out.append(str(s))
    return out


def render_sms_alert(
    *,
    incident_summary: Dict[str, Any],
    evidence_manifest_path: Optional[str] = None,
) -> str:
    incident_id = _get(incident_summary, "incidentId", "UNKNOWN")
    top_cause = _get(incident_summary, "topCause", _get(incident_summary, "topCause", "UNKNOWN"))
    severity = _get(incident_summary, "severity", "Unknown")
    confidence = _get(incident_summary, "confidence", "0.0")

    parts = [f"INCIDENT {incident_id}", f"sev={severity}", f"cause={top_cause}", f"conf={confidence}"]
    if evidence_manifest_path:
        parts.append(f"evidence={evidence_manifest_path}")
    return " | ".join(parts)


def render_email_incident_report(
    *,
    incident_summary: Dict[str, Any],
    evidence_manifest_path: Optional[str] = None,
) -> Tuple[str, str]:
    incident_id = _get(incident_summary, "incidentId", "UNKNOWN")
    severity = _get(incident_summary, "severity", "Unknown")
    top_cause_raw = _get(incident_summary, "topCause", "UNKNOWN")
    top_cause = _humanize_cause(top_cause_raw)
    confidence = _get(incident_summary, "confidence", "0.0")
    impact = _get(incident_summary, "impactedTarget", "")
    tw = incident_summary.get("timeWindow") or {}
    time_start = str(getattr(tw, "get", lambda _k, _d=None: _d)("start", "") or "")
    time_end = str(getattr(tw, "get", lambda _k, _d=None: _d)("end", "") or "")
    time_s = time_start if time_start else "UNKNOWN"
    if time_end and time_end != time_start:
        time_s = f"{time_start} to {time_end}"
    recommended = _get(incident_summary, "recommendedAction", "Collect additional evidence and validate configuration.")

    subject = f"[{severity}] Incident {incident_id} - {top_cause}"

    lines: list[str] = []
    lines.append("Hybrid Network Correlator — Incident Report")
    lines.append("")
    lines.append(f"Incident ID: {incident_id}")
    lines.append(f"Time: {time_s}")
    lines.append(f"Top Cause: {top_cause}")
    lines.append(f"Confidence: {confidence}")
    lines.append(f"Impact: {impact or 'UNKNOWN'}")
    lines.append(f"Recommended Action: {recommended}")

    lines.append("")
    lines.append("Evidence summary:")
    if evidence_manifest_path:
        lines.append(f"- Evidence manifest: {evidence_manifest_path}")
    evidence_lines = _top_evidence_lines(incident_summary, limit=4)
    if evidence_lines:
        for s in evidence_lines:
            lines.append(f"- {s}")
    else:
        lines.append("- No evidence lines available in the current incident summary.")

    lines.append("")
    lines.append("Safety:")
    lines.append("- This report was generated locally; live delivery is not implemented in the MVP.")
    lines.append("- Do not reply with secrets. Handle evidence according to your organization policies.")

    return subject, "\n".join(lines).rstrip() + "\n"


def render_teams_payload(
    *,
    incident_summary: Dict[str, Any],
    evidence_manifest_path: Optional[str] = None,
) -> Dict[str, Any]:
    incident_id = _get(incident_summary, "incidentId", "UNKNOWN")
    severity = _get(incident_summary, "severity", "Unknown")
    top_cause_raw = _get(incident_summary, "topCause", "UNKNOWN")
    top_cause = _humanize_cause(top_cause_raw)
    confidence = _get(incident_summary, "confidence", "0.0")
    impact = _get(incident_summary, "impactedTarget", "")
    recommended = _get(incident_summary, "recommendedAction", "")

    theme_color = {
        "High": "D13438",
        "Medium": "FFAA44",
        "Low": "2D7D46",
    }.get(severity, "0078D4")

    facts: List[Dict[str, str]] = [
        {"name": "Incident", "value": incident_id},
        {"name": "Severity", "value": severity},
        {"name": "Top cause", "value": top_cause},
        {"name": "Confidence", "value": confidence},
    ]
    if impact:
        facts.append({"name": "Impact", "value": impact})
    if recommended:
        facts.append({"name": "Recommended action", "value": recommended})
    if evidence_manifest_path:
        facts.append({"name": "Evidence", "value": evidence_manifest_path})

    return {
        "@type": "MessageCard",
        "@context": "https://schema.org/extensions",
        "summary": f"Incident {incident_id} ({severity})",
        "themeColor": theme_color,
        "title": f"[{severity}] Incident {incident_id} — {top_cause}",
        "sections": [{"facts": facts, "markdown": True}],
    }


def render_webhook_payload(
    *,
    incident_summary: Dict[str, Any],
    evidence_manifest_path: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Backwards-compatible name for the MVP's webhook template.

    In the enterprise notification scaffolding, this is primarily used for Teams
    incoming webhooks.
    """
    return render_teams_payload(
        incident_summary=incident_summary,
        evidence_manifest_path=evidence_manifest_path,
    )


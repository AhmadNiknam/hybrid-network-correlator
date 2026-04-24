from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple


def _get(summary: Dict[str, Any], key: str, default: str = "") -> str:
    v = summary.get(key, default)
    return default if v is None else str(v)


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
    confidence = _get(incident_summary, "confidence", "0.0")
    impact = _get(incident_summary, "impactedTarget", "")
    tw = incident_summary.get("timeWindow") or {}
    time_start = str(getattr(tw, "get", lambda _k, _d=None: _d)("start", "") or "")
    time_end = str(getattr(tw, "get", lambda _k, _d=None: _d)("end", "") or "")
    time_s = time_start if time_start else "UNKNOWN"
    if time_end and time_end != time_start:
        time_s = f"{time_start} to {time_end}"
    recommended = _get(incident_summary, "recommendedAction", "Collect additional evidence and validate configuration.")

    # Keep subject stable for tests and backward compatibility (use raw cause token).
    subject = f"[{severity}] Incident {incident_id} - {top_cause_raw}"

    lines: list[str] = []
    lines.append("Hybrid Network Correlator — Incident Report")
    lines.append("")
    # Keys are intentionally machine-greppable and asserted by unit tests.
    lines.append(f"incidentId: {incident_id}")
    lines.append(f"severity: {severity}")
    lines.append(f"topCause: {top_cause_raw}")
    lines.append(f"confidence: {confidence}")
    if time_s:
        lines.append(f"timeWindow: {time_s}")
    if impact:
        lines.append(f"impactedTarget: {impact}")
    lines.append(f"recommendedAction: {recommended}")

    lines.append("")
    lines.append("Evidence summary:")
    if evidence_manifest_path:
        lines.append(f"evidenceManifestPath: {evidence_manifest_path}")
    evidence_lines = _top_evidence_lines(incident_summary, limit=4)
    if evidence_lines:
        for s in evidence_lines:
            lines.append(f"- {s}")
    else:
        lines.append("- No evidence lines available in the current incident summary.")

    lines.append("")
    lines.append("Safety:")
    lines.append("- This report was generated locally; delivery is controlled by explicit enablement flags.")
    lines.append("- Do not reply with secrets. Handle evidence according to your organization policies.")

    return subject, "\n".join(lines).rstrip() + "\n"


def render_webhook_payload(
    *,
    incident_summary: Dict[str, Any],
    evidence_manifest_path: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Backwards-compatible name for the MVP's webhook template.

    This returns a compact, stable JSON-ready dict for webhook channels.
    The dispatcher may transform it into a Teams-specific payload at send time.
    """
    payload: Dict[str, Any] = {
        "incidentId": _get(incident_summary, "incidentId", "UNKNOWN"),
        "topCause": _get(incident_summary, "topCause", "UNKNOWN"),
        "confidence": float(incident_summary.get("confidence", 0.0) or 0.0),
        "severity": _get(incident_summary, "severity", "Unknown"),
        "recommendedAction": _get(incident_summary, "recommendedAction", ""),
    }
    if evidence_manifest_path:
        payload["evidenceManifestPath"] = evidence_manifest_path
    return payload


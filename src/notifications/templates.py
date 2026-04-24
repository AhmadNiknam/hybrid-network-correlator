from __future__ import annotations

from typing import Any, Dict, Optional, Tuple


def _get(summary: Dict[str, Any], key: str, default: str = "") -> str:
    v = summary.get(key, default)
    return default if v is None else str(v)


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
    top_cause = _get(incident_summary, "topCause", "UNKNOWN")
    severity = _get(incident_summary, "severity", "Unknown")
    confidence = _get(incident_summary, "confidence", "0.0")
    recommended = _get(incident_summary, "recommendedAction", "Collect additional evidence and validate configuration.")

    subject = f"[{severity}] Hybrid Network Incident {incident_id}: {top_cause}"

    lines: list[str] = []
    lines.append("Hybrid Network Correlator — Incident Report (prepare-only)")
    lines.append("")
    lines.append(f"incidentId: {incident_id}")
    lines.append(f"topCause: {top_cause}")
    lines.append(f"confidence: {confidence}")
    lines.append(f"severity: {severity}")
    lines.append(f"recommendedAction: {recommended}")
    if evidence_manifest_path:
        lines.append(f"evidenceManifestPath: {evidence_manifest_path}")
    lines.append("")
    lines.append("Safety:")
    lines.append("- This message was generated locally by scaffolding and was not sent by any live delivery provider.")
    lines.append("- Do not reply with secrets; handle incident evidence according to your organization policies.")

    return subject, "\n".join(lines).rstrip() + "\n"


def render_webhook_payload(
    *,
    incident_summary: Dict[str, Any],
    evidence_manifest_path: Optional[str] = None,
) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "incidentId": incident_summary.get("incidentId"),
        "topCause": incident_summary.get("topCause"),
        "confidence": incident_summary.get("confidence"),
        "severity": incident_summary.get("severity"),
        "recommendedAction": incident_summary.get("recommendedAction"),
    }
    if evidence_manifest_path:
        payload["evidenceManifestPath"] = evidence_manifest_path
    return payload


from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List


@dataclass(frozen=True)
class EvidenceManifest:
    incidentId: str
    scenario: str
    timestampUtc: str
    topCause: str
    confidence: float
    recommendedEvidence: List[str] = field(default_factory=list)
    collectionActions: List[Dict[str, Any]] = field(default_factory=list)
    safetyNotes: List[str] = field(default_factory=list)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def to_json_dict(manifest: EvidenceManifest) -> Dict[str, Any]:
    return asdict(manifest)


def build_evidence_manifest_from_incident_summary(
    summary: Dict[str, Any],
    *,
    timestamp_utc: str | None = None,
    recommended_evidence: List[str] | None = None,
    collection_actions: List[Dict[str, Any]] | None = None,
    safety_notes: List[str] | None = None,
) -> EvidenceManifest:
    incident_id = str(summary.get("incidentId", ""))
    scenario = str(summary.get("scenario", ""))

    ranked = summary.get("rankedCauses") or []
    top = ranked[0] if ranked else {}
    top_cause = str(top.get("cause", "UNKNOWN"))
    confidence = float(top.get("confidence", 0.0) or 0.0)

    next_checks = top.get("nextChecks") or []
    inferred_recommended = [str(x) for x in next_checks if str(x).strip()]

    safety_defaults = [
        "Prepare-only scaffolding: no live evidence collection is executed.",
        "No packet capture is started by this layer.",
        "No PowerShell scripts are executed by this layer.",
        "No live Azure APIs are called by this layer.",
        "All returned actions are requests for an operator or later execution layer.",
    ]

    return EvidenceManifest(
        incidentId=incident_id,
        scenario=scenario,
        timestampUtc=timestamp_utc or utc_now_iso(),
        topCause=top_cause,
        confidence=confidence,
        recommendedEvidence=recommended_evidence if recommended_evidence is not None else inferred_recommended,
        collectionActions=collection_actions if collection_actions is not None else [],
        safetyNotes=safety_notes if safety_notes is not None else safety_defaults,
    )


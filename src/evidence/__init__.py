"""
Phase 3 - Evidence collection scaffolding.

This package is intentionally "prepare-only": it generates structured collection
requests and manifests without executing live actions (no packet capture, no
PowerShell execution, no Azure API calls).
"""

from .manifest import EvidenceManifest, build_evidence_manifest_from_incident_summary
from .packager import write_manifest_json

__all__ = [
    "EvidenceManifest",
    "build_evidence_manifest_from_incident_summary",
    "write_manifest_json",
]

"""
Phase 3 - Evidence collection scaffolding.

This package is intentionally "prepare-only": it generates structured collection
requests and manifests without executing live actions (no packet capture, no
PowerShell execution, no Azure API calls).
"""

from .manifest import EvidenceManifest, build_evidence_manifest_from_incident_summary
from .packager import write_manifest_json

__all__ = [
    "EvidenceManifest",
    "build_evidence_manifest_from_incident_summary",
    "write_manifest_json",
]


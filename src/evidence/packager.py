from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Union

from .manifest import EvidenceManifest, to_json_dict


def _repo_root_from_here() -> Path:
    # src/evidence/packager.py -> repo root is 2 parents up
    return Path(__file__).resolve().parents[2]


def write_manifest_json(
    manifest: Union[EvidenceManifest, Dict[str, Any]],
    *,
    repo_root: Path | None = None,
    filename: str | None = None,
) -> Path:
    """
    Write a manifest JSON file to:
      samples/sample_outputs/evidence_manifests/

    Returns the path to the written file.
    """
    repo_root = repo_root or _repo_root_from_here()
    out_dir = repo_root / "samples" / "sample_outputs" / "evidence_manifests"
    out_dir.mkdir(parents=True, exist_ok=True)

    payload: Dict[str, Any]
    if isinstance(manifest, EvidenceManifest):
        payload = to_json_dict(manifest)
    else:
        payload = dict(manifest)

    incident_id = str(payload.get("incidentId", "")).strip() or "INCIDENT"
    ts = str(payload.get("timestampUtc", "")).replace(":", "").replace("-", "")
    ts = ts.replace("Z", "Z").replace(".", "")
    ts = ts or "timestamp"

    safe_name = "".join(c for c in incident_id if c.isalnum() or c in {"-", "_"})
    default_filename = f"{safe_name}_{ts}_evidence_manifest.json"
    out_path = out_dir / (filename or default_filename)

    with out_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
        f.write("\n")

    return out_path


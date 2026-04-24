from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List, Tuple

from .models import (
    ActivityEvent,
    ActivityLog,
    AlertPayload,
    AzureVm,
    OnPremEndpoint,
    TelemetryBundle,
    TelemetryObservation,
    TimeWindow,
)


def _read_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return data


def _as_time_window(obj: Dict[str, Any]) -> TimeWindow:
    return TimeWindow(start=str(obj["start"]), end=str(obj["end"]))


def load_alert(path: Path) -> AlertPayload:
    raw = _read_json(path)
    tw = _as_time_window(raw["timeWindow"])
    vm = AzureVm(name=str(raw["azureVm"]["name"]), resourceId=str(raw["azureVm"]["resourceId"]))
    ep_raw = raw.get("onPremEndpoint", {})
    ep = OnPremEndpoint(
        ipOrFqdn=str(ep_raw.get("ipOrFqdn", "")),
        protocol=(str(ep_raw["protocol"]) if "protocol" in ep_raw else None),
        port=(int(ep_raw["port"]) if "port" in ep_raw and ep_raw["port"] is not None else None),
    )
    symptoms = [str(s) for s in (raw.get("symptoms") or [])]
    return AlertPayload(
        schemaVersion=str(raw.get("schemaVersion", "1.0")),
        scenario=str(raw.get("scenario", "")),
        incidentId=str(raw.get("incidentId", "")),
        timeWindow=tw,
        azureVm=vm,
        onPremEndpoint=ep,
        symptoms=symptoms,
    )


def load_activity_log(path: Path) -> ActivityLog:
    raw = _read_json(path)
    events_raw = raw.get("events") or []
    events: List[ActivityEvent] = []
    for ev in events_raw:
        events.append(
            ActivityEvent(
                eventId=str(ev["eventId"]),
                timestamp=str(ev["timestamp"]),
                operationName=str(ev["operationName"]),
                resourceId=str(ev["resourceId"]),
                status=str(ev.get("status", "")),
                caller=str(ev.get("caller", "")),
                summary=str(ev.get("summary", "")),
            )
        )
    return ActivityLog(
        schemaVersion=str(raw.get("schemaVersion", "1.0")),
        scenario=str(raw.get("scenario", "")),
        events=events,
    )


def load_telemetry(path: Path) -> TelemetryBundle:
    raw = _read_json(path)
    obs_raw = raw.get("observations") or []
    observations: List[TelemetryObservation] = []
    for ob in obs_raw:
        extra = {k: v for k, v in ob.items() if k not in {"observationId", "timestamp", "type", "result", "details", "target", "query"}}
        observations.append(
            TelemetryObservation(
                observationId=str(ob["observationId"]),
                timestamp=str(ob["timestamp"]),
                type=str(ob["type"]),
                result=str(ob["result"]),
                details=(str(ob["details"]) if "details" in ob else None),
                target=(str(ob["target"]) if "target" in ob else None),
                query=(str(ob["query"]) if "query" in ob else None),
                extra=extra,
            )
        )
    return TelemetryBundle(
        schemaVersion=str(raw.get("schemaVersion", "1.0")),
        scenario=str(raw.get("scenario", "")),
        observations=observations,
    )


def _candidate_scenario_slugs(base: Path, scenario: str) -> List[str]:
    """
    Given a user-provided scenario value (e.g. "scenario1"), return possible
    full slugs detected from sample filenames (e.g. "scenario1_nsg_rule_change").
    """
    slugs: set[str] = set()

    sample_alerts = base / "sample_alerts"
    if sample_alerts.exists():
        for p in sample_alerts.glob(f"{scenario}*_alert.json"):
            if p.is_file():
                stem = p.stem
                if stem.endswith("_alert"):
                    slugs.add(stem[: -len("_alert")])

    sample_activity = base / "sample_activity_logs"
    if sample_activity.exists():
        for p in sample_activity.glob(f"{scenario}*_activity_log.json"):
            if p.is_file():
                stem = p.stem
                if stem.endswith("_activity_log"):
                    slugs.add(stem[: -len("_activity_log")])

    sample_outputs = base / "sample_outputs"
    if sample_outputs.exists():
        for p in sample_outputs.glob(f"{scenario}*_telemetry.json"):
            if p.is_file():
                stem = p.stem
                if stem.endswith("_telemetry"):
                    slugs.add(stem[: -len("_telemetry")])

    return sorted(slugs)


def resolve_scenario_slug(repo_root: Path, scenario: str) -> str:
    """
    Accepts either a full slug (scenario1_nsg_rule_change) or a short selector
    (scenario1) and returns the correct slug based on sample files on disk.
    """
    base = repo_root / "samples"

    # Fast-path: the caller already provided the full slug we expect.
    direct_alert = base / "sample_alerts" / f"{scenario}_alert.json"
    direct_activity = base / "sample_activity_logs" / f"{scenario}_activity_log.json"
    direct_telemetry = base / "sample_outputs" / f"{scenario}_telemetry.json"
    if direct_alert.exists() and direct_activity.exists() and direct_telemetry.exists():
        return scenario

    candidates = _candidate_scenario_slugs(base, scenario)
    if len(candidates) == 1:
        return candidates[0]
    if len(candidates) > 1:
        # Deterministic choice; keep behavior stable for tests/CI.
        return candidates[0]

    raise FileNotFoundError(
        "Scenario samples not found for "
        f"{scenario!r}. Looked under {str(base)!r}. "
        "Expected files like "
        f"'samples/sample_alerts/{scenario}_*_alert.json'."
    )


def scenario_paths(repo_root: Path, scenario: str) -> Tuple[Path, Path, Path, Path]:
    base = repo_root / "samples"
    slug = resolve_scenario_slug(repo_root, scenario)
    alert = base / "sample_alerts" / f"{slug}_alert.json"
    activity = base / "sample_activity_logs" / f"{slug}_activity_log.json"
    telemetry = base / "sample_outputs" / f"{slug}_telemetry.json"
    expected = base / "sample_outputs" / f"{slug}_expected_incident_summary.json"
    return alert, activity, telemetry, expected


def load_scenario(repo_root: Path, scenario: str) -> Tuple[AlertPayload, ActivityLog, TelemetryBundle]:
    alert_p, activity_p, telemetry_p, _ = scenario_paths(repo_root, scenario)
    return load_alert(alert_p), load_activity_log(activity_p), load_telemetry(telemetry_p)


def dump_json(obj: Any) -> str:
    try:
        payload = asdict(obj)  # dataclasses
    except Exception:
        payload = obj
    return json.dumps(payload, indent=2, sort_keys=True)


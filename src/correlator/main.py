from __future__ import annotations

import argparse
import json
from pathlib import Path

from .loader import load_scenario
from .reporter import build_incident_summary, render_admin_text, to_dashboard_dict, to_json_dict
from .scorer import score_probable_causes


def _repo_root_from_here() -> Path:
    # src/correlator/main.py -> repo root is 2 parents up
    # (.../repo/src/correlator/main.py -> parents[2] == .../repo)
    return Path(__file__).resolve().parents[2]


def run(scenario: str, repo_root: Path | None = None) -> dict:
    repo_root = repo_root or _repo_root_from_here()
    alert, activity, telemetry = load_scenario(repo_root, scenario)
    ranked = score_probable_causes(alert, activity, telemetry)
    summary = build_incident_summary(schema_version="1.0", alert=alert, ranked=ranked)
    return to_json_dict(summary)


def _run_full(scenario: str, repo_root: Path | None = None) -> tuple[object, list[object], dict]:
    """
    Internal helper for CLI output modes that need alert context.

    Returns (alert, ranked, incident_summary_dict).
    """
    repo_root = repo_root or _repo_root_from_here()
    alert, activity, telemetry = load_scenario(repo_root, scenario)
    ranked = score_probable_causes(alert, activity, telemetry)
    summary = build_incident_summary(schema_version="1.0", alert=alert, ranked=ranked)
    return alert, ranked, to_json_dict(summary)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Hybrid Network Correlator (Phase 1 MVP)")
    parser.add_argument(
        "--scenario",
        default="scenario1",
        help="Scenario selector or slug (e.g. scenario1 or scenario1_nsg_rule_change)",
    )
    parser.add_argument(
        "--format",
        default="text",
        choices=["text", "json", "dashboard"],
        help="Output format: text (default), json (detailed), dashboard (compact JSON)",
    )
    args = parser.parse_args(argv)

    if args.format == "json":
        report = run(args.scenario)
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0

    alert, ranked, report = _run_full(args.scenario)
    if args.format == "dashboard":
        payload = to_dashboard_dict(alert=alert, ranked=ranked, incident_summary=report)
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0

    # text (default)
    print(render_admin_text(alert=alert, ranked=ranked, incident_summary=report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


from __future__ import annotations

import argparse
import json
from pathlib import Path

from .loader import load_scenario
from .reporter import build_incident_summary, to_json_dict
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Hybrid Network Correlator (Phase 1 MVP)")
    parser.add_argument(
        "--scenario",
        default="scenario1",
        help="Scenario selector or slug (e.g. scenario1 or scenario1_nsg_rule_change)",
    )
    parser.add_argument("--json-only", action="store_true", help="Print JSON report only")
    args = parser.parse_args(argv)

    report = run(args.scenario)
    print(json.dumps(report, indent=2, sort_keys=True))
    if not args.json_only:
        print()
        print(report.get("summaryText", ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


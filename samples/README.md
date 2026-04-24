# Phase 1 mock samples (Hybrid Network Correlator)

This folder contains deterministic, realistic-but-fake JSON fixtures used to build and test the Phase 1 correlation logic **before** any live Azure integrations.

## Folder structure

- `sample_alerts/`: Incoming alert payloads that start an investigation
- `sample_activity_logs/`: Azure Activity Log events representing recent change activity
- `sample_outputs/`: Evidence/telemetry bundles and the expected incident summaries

## Scenario files

Each scenario has four artifacts, sharing the same scenario slug:

- `*_alert.json`: alert payload fixture
- `*_activity_log.json`: Azure activity log fixture (typically a small list of events)
- `*_telemetry.json`: evidence/telemetry bundle fixture (probes, derived signals, timelines)
- `*_expected_incident_summary.json`: deterministic expected output for unit tests

Scenarios included:

1. `scenario1_nsg_rule_change_*`: Connectivity failure caused by an NSG rule change
2. `scenario2_udr_route_change_*`: Connectivity degradation caused by a route table / UDR change
3. `scenario3_vpn_tunnel_instability_*`: Intermittent connectivity caused by VPN gateway/tunnel instability

## Data safety rules

- No real tenant IDs, subscription IDs, IP addresses, passwords, tokens, or secrets are included.
- ARM IDs use placeholders like `<subscription-id>`, `<tenant-id>`, `<resource-group>`.
- Values (IDs and timestamps) are fixed to keep fixtures deterministic for unit tests.

## Common conventions

- **Timestamps**: ISO 8601 UTC with `Z` suffix (e.g. `2026-04-20T09:15:00Z`)
- **Deterministic IDs**: short, human-readable strings (no GUIDs)
- **Cross-references**: expected summaries reference `eventId`s from activity logs and `observationId`s from telemetry

## How Phase 1 uses these samples

Phase 1 correlation takes:

1. An alert payload (`sample_alerts`)
2. Recent change events (`sample_activity_logs`)
3. Supporting evidence/telemetry (`sample_outputs/*_telemetry.json`)

…and produces an incident summary that should match `sample_outputs/*_expected_incident_summary.json`.


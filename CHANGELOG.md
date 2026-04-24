# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## v1.0.0 - 2026-04-23

### Added
- Deterministic, mock-first incident correlation workflow for hybrid connectivity (Azure ↔ on‑prem).
- Scenario fixtures under `samples/` covering NSG change, UDR route change, and VPN tunnel instability.
- Output renderers for `text`, `json`, and compact `dashboard` payloads intended for future UI/ingestion.

### Implemented
- Explainable scoring over a focused hypothesis set (`NSG_CHANGE`, `ROUTE_UDR_CHANGE`, `VPN_GATEWAY_ISSUE`, `DNS_ISSUE`, `UNKNOWN`).
- CLI entry point to run a scenario and emit the selected output format.
- Evidence collection **scaffolding** that generates “what to collect” manifests (prepare-only).
- KQL query template helpers and Azure configuration loading (scaffolded for future read-only integrations).

### Security
- Read-only / safe scaffolding by default: no automated remediation and no destructive Azure actions.
- Evidence guidance is generated as a manifest; it does not execute diagnostics automatically.
- Unit tests assert that common execution primitives (e.g., `subprocess.run`, `os.system`) are not invoked by the scaffolding path.

### Documentation
- Operator-focused docs for vision, use cases, architecture, backlog, PowerShell diagnostics guidance, and security model.
- Release notes for the first trusted public MVP release.

### Known Limitations
- No live Azure authentication or query execution in the MVP (placeholders/templates only).
- No write operations, remediation, or changes to Azure resources.
- Evidence collection is not automated; operators run diagnostics manually and provide artifacts out-of-band.
- Coverage is intentionally scoped to a small set of scenarios and hypotheses; additional signals and scenarios are planned.


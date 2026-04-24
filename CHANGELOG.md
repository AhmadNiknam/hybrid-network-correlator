# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## v1.1.0 - 2026-04-23

### Added
- Notification layer scaffolding (prepare-only) to format incident reports for future delivery channels.
- Email, SMS, and webhook notification models.
- Safe simulated dispatch behavior (no live sending).
- Notification documentation under `docs/notifications.md`.

### Security
- No live sending: the MVP does not send real email/SMS/webhook notifications.
- No real contact details in the repository: examples use placeholders and recommend environment variables.
- No external API calls: notification dispatch is simulated and does not invoke provider SDKs or network requests.

## v1.2.0 - 2026-04-24

### Added
- **Live Azure readiness controls (guardrails)**: documented, explicit enablement flags and read-only intent for future live Azure querying (still not implemented). See `docs/live-azure-readiness.md`.
- **Safer environment configuration**:
  - `.env.example` template for local configuration
  - clearer defaults that keep live integrations and notifications disabled unless explicitly enabled
- **GitHub Actions CI**: automated unit tests on push and pull requests via `.github/workflows/python-tests.yml`.
- **Enterprise notification readiness**: documentation and guardrails for enterprise-friendly notification enablement and secrets handling. See `docs/enterprise-notifications.md`.

### Implemented
- **Real Microsoft Teams webhook delivery** for the `teams/webhook` route, with explicit opt-in guardrails and secret handling guidance. It remains **disabled by default**. See `docs/notifications.md` and `docs/enterprise-notifications.md`.

### Security
- **Safe defaults preserved**: notifications and live Azure mode remain off unless explicitly enabled via environment flags.
- **Webhook secret handling**: documentation reinforces treating `TEAMS_WEBHOOK_URL` as a secret and avoiding logging/committing sensitive endpoints.
- **Read-only Azure posture reinforced**: live Azure integration remains a controlled, read-only readiness design—not a production Azure integration.

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


## Hybrid Network Correlator

[![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python&logoColor=white)](https://www.python.org/)
![MVP](https://img.shields.io/badge/Status-MVP-brightgreen)
![Tests](https://img.shields.io/badge/Tests-unittest%20(local)-informational)
![Azure Hybrid Monitoring Concept](https://img.shields.io/badge/Azure-Hybrid%20Monitoring%20Concept-0078D4?logo=microsoftazure&logoColor=white)

**Hybrid Network Correlator** is a practical incident-correlation tool for **network and infrastructure administrators** operating **hybrid connectivity** (Azure ↔ on‑prem). It generates a concise, evidence-backed triage summary by correlating **recent changes** with **telemetry signals** using **deterministic, explainable scoring**.

### Release information

- **Current stable version**: **v1.1.0**
- **Release status**: **Public MVP**

### Trust and safety statement

This repository is designed to be safe to evaluate and run in a local environment:

- **Read-only / safe scaffolding**: the MVP uses mock fixtures and deterministic logic; Azure integration is scaffolded as placeholders.
- **No destructive Azure actions**: there are no automated “write” operations, remediation steps, or resource-modifying commands.
- **Prepare-only evidence guidance**: evidence collection outputs are manifests describing what to collect; they do not execute diagnostics automatically.
- **Live Azure readiness (future)**: live Azure read-only integration is **disabled by default** and is not implemented yet. See `docs/live-azure-readiness.md`.

### Elevator pitch

When “Azure VM → on‑prem endpoint” connectivity fails, responders often bounce between activity logs, routing/NSG checks, and ad-hoc diagnostics. This project turns that hunt into a **repeatable workflow**: **input a scoped alert + evidence bundle → get ranked probable causes + supporting evidence + next checks**.

### Feature highlights

- **Explainable correlation**: ranked hypotheses with confidence, evidence-for/against, and recommended next checks
- **Mock-first, deterministic MVP**: realistic-but-fake fixtures under `samples/` keep behavior stable for iteration and tests
- **Admin-friendly outputs**: `text` report plus `json` and compact `dashboard` payloads
- **Safety by design**:
  - **Azure integration** is scaffolded **read-only placeholders** (no live auth/queries in MVP)
  - evidence collection is **prepare-only** (creates “what to collect” manifests; does not run diagnostics automatically)

### Current status (MVP)

- **What works today**:
  - Scenario ingestion from fixtures (`samples/`)
  - Deterministic scoring over a small hypothesis set:
    - `NSG_CHANGE`, `ROUTE_UDR_CHANGE`, `VPN_GATEWAY_ISSUE`, `DNS_ISSUE`, `UNKNOWN`
  - Output formats: `text`, `json`, `dashboard`
  - Notification layer **scaffolding only** (email/SMS/webhook models + templates + simulated dispatch; no live sending)
  - Unit tests verifying stable outputs and safety constraints
- **What is intentionally not implemented yet**:
  - Live Azure query execution/authentication
  - Any “write” actions or automated remediation
  - Automatic PowerShell execution / packet capture / live probing
  - Live notification delivery (no real email/SMS/webhook sending in the MVP)

### Quick start (CLI)

From the repository root:

```powershell
# Text report (default)
python -m src.correlator.main --scenario scenario1_nsg_rule_change --format text

# Detailed JSON summary (stable for tests)
python -m src.correlator.main --scenario scenario1_nsg_rule_change --format json

# Compact JSON for future dashboard ingestion
python -m src.correlator.main --scenario scenario1_nsg_rule_change --format dashboard
```

Scenario slugs included:

- `scenario1_nsg_rule_change`
- `scenario2_udr_route_change`
- `scenario3_vpn_tunnel_instability`

### Example output (text report)

Snippet from `scenario1_nsg_rule_change`:

```text
Hybrid Network Correlator - Admin Report

Incident ID: INC-0001
Scenario: scenario1_nsg_rule_change
Impacted target: vm-app-01 -> 10.20.30.40:443
Time window: 2026-04-20T09:10:00Z to 2026-04-20T09:30:00Z

Top 3 probable causes:
1. NSG_CHANGE (confidence=0.90, score=9)
2. VPN_GATEWAY_ISSUE (confidence=0.10, score=1)
3. UNKNOWN (confidence=0.00, score=0)

Summary:
Probable cause: a recent NSG rule change is blocking traffic between vm-app-01 and 10.20.30.40:443.
```

More sanitized sample reports live in `samples/sample_outputs/`.

### Example output (JSON summary)

```json
{
  "incidentId": "INC-0001",
  "scenario": "scenario1_nsg_rule_change",
  "rankedCauses": [
    { "cause": "NSG_CHANGE", "confidence": 0.9, "score": 9 }
  ],
  "summaryText": "Probable cause: a recent NSG rule change is blocking traffic..."
}
```

### Run unit tests

```powershell
python -m unittest discover -s src\tests -p "test_*.py"
```

### Configuration (.env)

This repo includes a safe template at `.env.example`.

- Copy `.env.example` to `.env` locally.
- Keep `LIVE_AZURE_ENABLED=false` (default). Live Azure integration is not implemented yet.
- Never commit `.env` or any secrets.

### Tested modules (unit tests)

The MVP includes unit tests validating output stability and safety boundaries across these areas:

- **CLI and output formats**: `src.correlator.main` (text/json/dashboard output shapes)
- **Scenario loading and expected outputs**: `src.correlator.loader` + `samples/` fixtures
- **Evidence scaffolding (prepare-only)**: `src.evidence.collectors`, `src.evidence.manifest`, `src.evidence.packager`
- **Integration scaffolding**: `src.integrations.kql_queries` (KQL template helpers) and `src.integrations.config` (Azure env config loading)

### Repository map

- `src/`: Python correlation engine (CLI + scoring + output rendering) and scaffolding modules
- `samples/`: deterministic JSON fixtures used by the MVP and tests
- `scripts/powershell/`: optional, read-only diagnostic scripts admins can run manually
- `docs/`: architecture, backlog, and operator-focused documentation

### Skills demonstrated (what this repo shows)

- **Hybrid networking incident triage thinking** (Azure ↔ on‑prem failure modes, evidence, next checks)
- **Deterministic correlation/scoring design** (explainable outputs and stable regression fixtures)
- **Safety-first automation approach** (read-only / prepare-only boundaries; no hidden side effects)
- **Testable engineering** (fixtures + stable JSON outputs + unit tests)
- **Clear technical documentation** for IT administrators (vision, use cases, architecture)

### Roadmap (practical next steps)

- **Phase 2**: implement **read-only** Azure Activity Log + Log Analytics querying and normalization to internal models
- **Phase 3**: standardize operator evidence collection bundles (still read-only) and ingestion of collected artifacts
- **Phase 4**: dashboard requirements and production hardening (auditability, RBAC assumptions, error handling)

For the full backlog, see `docs/backlog.md`.

### Example future notification flow (not implemented yet)

The notification layer is included today to standardize message shapes and delivery-channel formatting while staying safe and offline.
When live delivery is implemented later, an end-to-end flow is expected to look like:

1. Correlate an incident from an alert payload (plus optional evidence bundle).
2. Render notification content for the selected channel(s):
   - Email: detailed incident report
   - SMS: short paging-style summary
   - Webhook: compact JSON payload for ticketing/chat-ops
3. Dispatch via a provider integration (future), with audit logging and explicit enablement.
4. Confirm delivery outcomes (success/failure metadata) without exposing secrets or contact details in logs.

### Contribution / learning note

This project is intentionally scoped as a **portfolio-grade MVP**: small, explainable, and safe. If you’re using it to learn hybrid monitoring patterns, a good path is:

- start by adding a new mock scenario under `samples/`
- add/adjust scoring rules and update expected outputs
- document the hypothesis + evidence checklist in `docs/`

### Key documents

- `docs/vision.md`: problem statement and MVP definition
- `docs/use-cases.md`: MVP use case and explicit non-goals
- `docs/architecture.md`: implemented module architecture and data flow
- `docs/backlog.md`: phased roadmap and next recommended work
- `docs/powershell-diagnostics.md`: safe, read-only Windows/on-prem evidence collection scripts
- `docs/release-notes-v1.md`: v1.0.0 public MVP release notes
- `docs/release-notes-v1.1.md`: v1.1.0 release notes (notification scaffolding and safety model)
- `docs/notifications.md`: notification layer scaffolding (simulated/prepare-only)

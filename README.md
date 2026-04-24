## Hybrid Network Correlator

A practical incident-correlation tool for **network and infrastructure administrators** operating **hybrid connectivity** (Azure ↔ on-prem).

### What it does (MVP)

When connectivity between an **Azure VM** and an **on-prem endpoint** degrades or fails, the system:

- Looks at **recent Azure activity changes** near the incident window
- Reviews relevant **telemetry and diagnostics evidence**
- Produces a **probable-cause summary** and **next checks** for the administrator

The MVP is intentionally narrow: it correlates a small set of common causes using **mock data** and **deterministic, rule-based scoring**.

### Why this exists

Hybrid incidents often require a human to manually piece together:

- “What changed recently in Azure?”
- “Which components are implicated?”
- “What evidence supports each hypothesis?”

This project aims to reduce time-to-triage by generating a concise, evidence-backed summary.

### Project status

- **Phase 1 (current target)**: mock data + rule-based correlation
- Later phases add read-only Azure integration, evidence collection, and a dashboard

See `[docs/backlog.md](docs/backlog.md)` for the phased roadmap and MVP backlog.

### Key documents

- `[docs/vision.md](docs/vision.md)`: product vision, scope, and success criteria
- `[docs/use-cases.md](docs/use-cases.md)`: MVP scenario and out-of-scope use cases
- `[docs/architecture.md](docs/architecture.md)`: intended components and data flow (documentation-first)
- `[docs/backlog.md](docs/backlog.md)`: phased roadmap and backlog items

### Assumptions (MVP)

- The incident involves **Azure VM → on-prem endpoint** connectivity (direct or via hub/spoke).
- The system receives (or loads) an **alert payload** that provides:
  - The Azure VM identity (name/id), on-prem endpoint (IP/FQDN), and time window
  - Basic symptom labels (packet loss, latency spike, unreachable)
- During Phase 1, all inputs are **mock JSON** (no live Azure calls).
- Output is a **human-readable text report** (not a dashboard).

### Out of scope (explicitly not MVP)

- Automated remediation (changes to NSG/UDR/firewall, restarts, etc.)
- Production deployments, CI/CD, or Azure infrastructure-as-code
- Full topology discovery across all subscriptions/tenants
- Real-time streaming analytics
- Generative AI “free-form” root-cause reasoning (start deterministic first)

### Repository structure (current / intended)

- `README.md`: entry point for admins and contributors
- `docs/`: documentation set (vision, use cases, architecture, backlog)
- Source code and Azure deployment assets will be added **later**, after docs and data contracts are stable.

### How to review changes

- Open the updated docs in your editor:
  - `README.md`
  - `docs/vision.md`
  - `docs/use-cases.md`
  - `docs/architecture.md`
  - `docs/backlog.md`
- If you use git, review with `git diff` (or your IDE’s “Source Control” diff view).

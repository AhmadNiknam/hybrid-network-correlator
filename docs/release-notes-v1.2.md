# Release Notes — v1.2.0

v1.2.0 strengthens the project’s **release readiness** without changing the core MVP posture: **mock-first**, **safe by default**, and **no destructive actions**. This release focuses on clearer operational guardrails, safer configuration patterns, and a CI baseline—plus an enterprise-friendly notification pathway via Microsoft Teams **with explicit opt-in**.

## What changed since v1.1.0

Since v1.1.0’s notification scaffolding, v1.2.0 adds:

- **Live Azure readiness controls (documentation + guardrails)** for a future, **read-only** live mode.
- A safer **environment configuration** approach (`.env.example`) that keeps integrations disabled unless explicitly enabled.
- **GitHub Actions CI** for automated unit tests on pushes and pull requests.
- **Enterprise notification readiness** documentation and explicit guardrails.
- **Microsoft Teams webhook delivery** implementation with explicit opt-in and secret-handling guidance.
- Security posture refinements and documentation reinforcing safe defaults.

## Why v1.2.0 is important

Hybrid incident tooling becomes risky when it quietly “goes live” (queries production telemetry, contacts people, or leaks endpoints) without explicit operator intent. v1.2.0 is important because it:

- Preserves the MVP’s **offline-by-default** posture.
- Adds **clear enablement controls** for future live Azure read-only work (without claiming it is implemented today).
- Makes notification delivery safer by ensuring Teams delivery is **implemented but disabled by default**, and only sends when explicitly enabled.
- Establishes **repeatable CI** so regression checks run automatically in pull requests.

## Features added / improved

### Live Azure readiness (read-only, future)

The project now documents a controlled future state for live Azure read-only querying:

- **Default remains offline** (`LIVE_AZURE_ENABLED=false`).
- The intended live mode is **read-only** (no write operations, no remediation).
- Permissions guidance follows **least privilege** (scope as narrowly as possible).

See `docs/live-azure-readiness.md` for the readiness model and guardrails.

### Safer environment configuration

Configuration is guided via a safe template:

- `.env.example` provides placeholders and safe defaults.
- Secrets and endpoints are expected to be supplied **outside** git (local environment, CI secret store, or a managed secret store in future deployments).

See the `.env` guidance in `README.md` and the safety notes in `docs/security-model.md`.

### CI workflow (automated unit tests)

Automated tests run in GitHub Actions:

- Triggers: **push** and **pull_request**
- Runtime: Ubuntu + Python 3.11
- Command: `python -m unittest -v`

Workflow file: `.github/workflows/python-tests.yml`

### Enterprise notification readiness

Notification documentation is expanded to support enterprise-safe enablement:

- Clear guardrails for explicit opt-in
- Guidance for storing secrets (treat webhook URLs as secrets)
- Recommended patterns for Teams tenants that restrict classic connectors

See `docs/enterprise-notifications.md` and `docs/notifications.md`.

### Microsoft Teams webhook delivery (implemented, disabled by default)

Microsoft Teams webhook delivery is implemented for the `teams/webhook` route, but will only send when all are true:

- `NOTIFICATIONS_ENABLED=true`
- `TEAMS_ENABLED=true`
- `TEAMS_WEBHOOK_URL` is provided
- the message is routed to `teams/webhook`

This preserves the “safe by default” posture while enabling real-world enterprise evaluation when explicitly intended.

## Security model (how v1.2.0 should be understood)

v1.2.0 does not change the security posture fundamentals:

- **No destructive actions**: no resource modifications, no remediation.
- **No live Azure integration today**: the live Azure work is readiness/guardrails for a future **read-only** mode; it is not a production Azure integration.
- **Secrets must not enter git**: webhook URLs, tokens, connection strings, and real contact details must be provided externally.

See `docs/security-model.md` for trust boundaries and the safe-by-default model.

## Known limitations

This release remains an MVP and is intentionally constrained:

- **No live Azure authentication or query execution** (readiness controls exist; integration is not implemented).
- **No write actions / remediation**.
- **Evidence collection is operator-driven**; the tool does not run PowerShell diagnostics automatically.
- **Email/SMS delivery is not implemented** (templates/models exist; delivery is future work).
- Teams webhook delivery is **off by default** and requires explicit enablement and a valid webhook endpoint.

## Future roadmap (directional)

Planned next steps build toward practical, audited, read-only operations:

- **Read-only Azure querying** (Activity Log + Log Analytics) with explicit guardrails and least-privilege guidance.
- Normalization of live telemetry into internal evidence models while keeping offline fixtures as the regression baseline.
- Improved evidence bundle standards and ingestion (operator-provided artifacts; still no automated probing).
- Additional notification integrations via brokered workflows (e.g., Logic Apps / Power Automate) for governance, retries, and auditing.

For broader sequencing, see `docs/backlog.md`.


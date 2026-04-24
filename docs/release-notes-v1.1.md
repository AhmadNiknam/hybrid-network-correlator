# Release Notes — v1.1.0

## What changed since v1.0.0

v1.1.0 adds a **safe notification layer scaffolding** to the MVP. This introduces standardized models and templates for future delivery channels while preserving the project’s trust posture: **mock-first**, **read-only**, and **no external side effects**.

### Added

- **Notification layer scaffolding** (prepare-only): structured message models and templates for incident notifications.
- **Channel concepts and models**:
  - **Email**: detailed incident report content shape (plain text)
  - **SMS**: short paging-style alert text
  - **Webhook**: compact JSON-ready payload for downstream systems
- **Safe simulated dispatch behavior**:
  - no provider SDK calls
  - no network requests
  - simulated results returned to support testing and iteration
- **Notification documentation**: see `docs/notifications.md`.

## Why notification scaffolding was added

Incident correlation outputs are most useful when they can be routed into operational workflows (paging, ticketing, chat-ops, and incident timelines). The v1.1.0 scaffolding exists to:

- standardize message shapes early (stable contracts for future integrations)
- keep delivery behavior **explicitly off** in the MVP
- enable deterministic testing of notification formatting without introducing credentials, contact data, or external dependencies

## Safety model (MVP)

Notifications in v1.1.0 are intentionally safe:

- **No live sending**: the repository does not send real email/SMS/webhook notifications.
- **No real contact details**: do not commit email addresses, phone numbers, or webhook URLs. Use placeholders in docs and provide any values via environment variables outside the repo.
- **No external API calls**: dispatch behavior is simulated and does not call external services.

This design prevents accidental contact, reduces data leakage risk during development, and keeps the MVP safe to run locally.

For details, see `docs/notifications.md` and `docs/security-model.md`.

## Future integration options (directional)

When the project is ready for opt-in, audited, live delivery, the scaffolding can be wired to one or more of the following approaches:

- **Azure Communication Services**
  - Email and SMS delivery via Azure-managed channels
  - Key Vault for secrets (if required) and managed identity where possible
- **Logic Apps**
  - HTTP-triggered workflow to route incidents to email, Teams, service desk, or other connectors
  - Centralized governance, retries, and connector management
- **Webhook / Teams**
  - Direct webhook delivery to Teams channels (or via an intermediate workflow for governance)
  - Compact payloads aligned to ticket/chat-ops ingestion
- **ITSM tools**
  - Create/update incidents in tools such as ServiceNow, Jira Service Management, or other service desks
  - Prefer a workflow broker (Logic Apps or an internal gateway) for policy, secrets, and auditing

## Release readiness notes

v1.1.0 is suitable for local evaluation and iteration. It remains an MVP with explicit non-goals:

- no live Azure authentication/query execution
- no remediation or write operations
- no automated execution of diagnostics scripts
- no live notification delivery


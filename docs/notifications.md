# Notifications (safe by default)

This document describes the notification layer for the Hybrid Network Correlator MVP.

## Current design (today)

The notification package exists to **format** incident reports for delivery channels while keeping the MVP safe by default.

- **Data models**: `src/notifications/models.py` defines recipients, messages, channels, and dispatch results.
- **Templates**: `src/notifications/templates.py` renders:
  - short SMS alert text
  - detailed email incident report (plain text)
  - compact webhook payload (JSON-ready dict)
- **Config**: `src/notifications/config.py` reads optional environment variables.
- **Dispatcher**: `src/notifications/dispatcher.py` returns **simulated** results by default.

This mirrors the project’s overall MVP safety posture: **read-only** and **scaffold-first**.

## Supported future channels

The scaffolding supports these delivery channels conceptually:

- **email**: incident report to an administrator distribution list
- **sms**: short paging-style alert for high severity incidents
- **webhook**: compact JSON payload to incident tooling (ticketing, chat-ops, SIEM, etc.)

## Safety model (why no real messages are sent)

Notifications are intentionally safe in the MVP by default:

- **No external APIs**: no network calls are made.
- **No live email/SMS**: no SMTP, SMS gateway, or provider SDK calls are made.
- **No secrets required**: tests run with no environment variables set.
- **Explicit guardrail**: `dispatch_notification()` returns simulated results unless `NOTIFICATIONS_ENABLED=true`.

### Exception: Teams webhook delivery (explicit opt-in)

Microsoft Teams webhook delivery is implemented, but will only send when all are true:

- `NOTIFICATIONS_ENABLED=true`
- `TEAMS_ENABLED=true`
- `TEAMS_WEBHOOK_URL` is provided
- the message is routed to `teams/webhook`

See `docs/enterprise-notifications.md` for setup and security guidance.

This reduces risk of accidental contact, data leakage, and unreviewed operational behavior during early development.

## Environment variables (optional)

These variables are *optional* and must be provided outside the repo (developer environment, CI secrets, Azure app settings, etc.):

- `NOTIFICATIONS_ENABLED`: `true|false` (default `false`)
- `ADMIN_EMAIL`: administrator email address (do not commit real values)
- `ADMIN_PHONE_E164`: administrator phone in E.164 format, e.g. `+15551234567` (do not commit real values)
- `ADMIN_WEBHOOK_URL`: administrator webhook endpoint (do not commit real values)

## Required future Azure services (when implementing live delivery)

Two common Azure approaches for delivery are anticipated:

### Option A: Azure Communication Services (ACS)

- Email:
  - **Azure Communication Services Email** (or SMTP relay if policy allows)
- SMS:
  - **Azure Communication Services SMS**
- Secrets/config:
  - **Azure Key Vault** for connection strings / keys (if not using managed identity)
- Execution:
  - **Azure Functions** (recommended) or Container Apps

### Option B: Logic Apps / Power Automate + Webhooks

- Webhook:
  - **Logic Apps** HTTP trigger to route to email/SMS/Teams/service desk tools
- Secrets/config:
  - **Key Vault**-backed connectors / managed identity where possible
- Execution:
  - Hybrid Network Correlator posts to Logic Apps endpoint (future)

## Why secrets and real contact details must not be committed

This repo is designed to stay safe and shareable:

- Real emails, phone numbers, and webhook URLs can be considered **sensitive operational data**.
- Provider credentials (keys, tokens, connection strings) are secrets and must never enter git history.
- Incident reports can contain environment identifiers and evidence paths; treat them as sensitive.

Use:
- local environment variables for development
- CI secret stores
- Azure app settings and Key Vault (future)


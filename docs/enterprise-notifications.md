# Enterprise notifications (Microsoft Teams webhook)

This project’s default posture is **safe and offline**. Notification delivery is **disabled by default** and must be explicitly enabled.

## What is implemented

- **Microsoft Teams webhook delivery** is implemented for the `teams/webhook` route.
- **Email/SMS delivery is not implemented** (templates exist only).

## Prerequisites

- A Microsoft Teams destination that can accept webhook POSTs:
  - **Classic “Incoming Webhook” connector** (where available), or
  - A **Teams Workflow / Power Automate** flow with an HTTP request trigger that posts into a channel (recommended in many tenants).

## Create a Teams webhook endpoint

Your tenant may support one or both patterns below. Use whichever your organization allows.

### Option A: Incoming Webhook (classic connector)

1. In Microsoft Teams, open the target **Team** and **Channel**.
2. Open the channel menu and add/configure **Incoming Webhook** (connector).
3. Copy the generated webhook URL.

### Option B: Workflow webhook (recommended in many tenants)

1. Create a new **Workflow** in Teams (or a Power Automate flow) for the target channel.
2. Use a trigger like **“When an HTTP request is received”**.
3. In the workflow, add an action to **post a message** to the channel.
4. Save the workflow and copy the generated HTTP endpoint URL.

## Configure environment variables (safe)

Do **not** store webhook URLs in source control.

- Copy `.env.example` to `.env` (local use only).
- Set:
  - `NOTIFICATIONS_ENABLED=true`
  - `TEAMS_ENABLED=true`
  - `TEAMS_WEBHOOK_URL=<your webhook URL>`

## Enablement guardrails (important)

Real Teams delivery occurs **only** when all are true:

- `NOTIFICATIONS_ENABLED=true`
- `TEAMS_ENABLED=true`
- `TEAMS_WEBHOOK_URL` is provided
- the message route is `teams/webhook` (internal routing guardrail)

If any condition is not met, the dispatcher will **not send** and will return either a **simulated** result or a **failed** result with a clear message.

## Security warnings

- Treat the Teams webhook URL as a **secret**. Anyone with the URL can usually post messages.
- Do not print, log, or return webhook URLs in application output.
- Prefer storing webhook URLs in:
  - CI secret store, or
  - Azure App Settings / Key Vault (future deployment), not plaintext files

## Troubleshooting

- **Nothing is delivered and result says “simulated”**
  - Confirm `NOTIFICATIONS_ENABLED=true`
  - Confirm `TEAMS_ENABLED=true`
- **Result says TEAMS_WEBHOOK_URL is missing**
  - Ensure `TEAMS_WEBHOOK_URL` is set in the runtime environment
- **Result says HTTPError**
  - Verify the webhook endpoint is valid and not expired/rotated
  - Check tenant policies (some block connector webhooks)
- **Result says URLError**
  - Check outbound network access / proxy requirements
  - Validate DNS resolution from the host running the tool


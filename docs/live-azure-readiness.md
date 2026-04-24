# Live Azure readiness (future, read-only)

This document explains how the project will support **optional, controlled live Azure read-only querying** in a future phase, without introducing destructive behaviors.

## Current status (today)

- **Default is offline**: `LIVE_AZURE_ENABLED=false` by default.
- **No live Azure SDK/API calls**: the repository ships with **mock-first scaffolding** only.
- **Read-only intent**: any future live mode must remain strictly read-only and must not modify resources.

## How live mode will work (future)

When implemented, live mode will:

- be **explicitly enabled** via `LIVE_AZURE_ENABLED=true`
- use **read-only** data sources only (e.g., Azure Activity Logs, Log Analytics)
- normalize results into the project’s internal “evidence” shapes
- record enough metadata for auditability (e.g., which query template ran, time window, and source)

Live mode will not:

- create/update/delete resources
- change NSGs/routes/firewalls
- enable tracing/packet capture
- execute PowerShell scripts automatically

## Required Azure permissions (least privilege)

Live mode should follow **least privilege** and scope access as narrowly as possible (resource group or specific workspace).

Typical read-only needs (subject to final implementation):

- **Log Analytics / Azure Monitor Logs**:
  - ability to query a specific Log Analytics workspace
  - prefer workspace-scoped permissions over subscription-wide when possible
- **Azure Activity Logs**:
  - ability to read activity events for the relevant scope (subscription/resource group)

If your organization uses custom roles, prefer a custom role that includes only “read” actions required for these queries.

## Managed identity recommendation

When running in Azure (Functions, Container Apps, VM, etc.), prefer:

- **Managed identity** (workload identity) over client secrets

Benefits:

- no long-lived secrets on developer machines
- simpler rotation and auditing
- easier to scope permissions to the workload

## Why service principal secrets must not be committed

Service principal secrets are equivalent to passwords.

- If committed to git history, they can be leaked to forks, caches, logs, and mirrors.
- A revert does not remove them from history.
- Rotation/revocation must be considered mandatory if exposure occurs.

Use environment variables and secure secret stores (e.g., Key Vault) instead.

## Using `.env.example` safely

- Copy `.env.example` to `.env` locally.
- Replace placeholders with real values **only on your machine**.
- Never commit `.env` or any credential material.

The repository `.gitignore` is hardened to reduce accidental commits, but it is not a substitute for careful review.

## Current limitations (important)

- `LIVE_AZURE_ENABLED=true` does **not** enable live querying yet.
- The integration layer will stop with a clear “not implemented yet” message rather than attempting unknown SDK/API calls.
- Unit tests never make live calls; they validate default-off behavior and safe simulated responses.


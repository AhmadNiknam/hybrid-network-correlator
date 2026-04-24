# Security model (MVP)

This document explains the **security and trust posture** of the current Hybrid Network Correlator MVP and what must change before any real-world deployment.

## Summary (today)

- **Read-only by design**: the MVP correlates incidents using **local, deterministic fixtures**.
- **No live Azure actions**: there is **no authentication** and **no query execution** against Azure in the MVP.
- **No secret storage in the repo**: examples use placeholders; configuration is expected to be provided externally.
- **Operator-in-the-loop evidence**: PowerShell scripts are **manual**, **read-only** templates; the Python layer does **not** run them.

## Trust boundaries

### Boundary A: Repository / code

- Public code and docs must remain free of secrets and real customer data.
- `samples/` contains sanitized fixtures only.
- `.gitignore` is hardened to reduce accidental commits of secrets, keys, and local outputs.

### Boundary B: Operator environment (where scripts run)

PowerShell scripts run on an operator-controlled Windows host (on-prem or VM) and may access:

- local network configuration
- DNS settings/cache (best-effort)
- route tables, neighbor tables, adapter metadata
- connectivity checks (ICMP/TCP) to a specified target

Outputs can contain environment identifiers (hostnames, internal IPs, DNS servers). Treat outputs as sensitive incident evidence.

### Boundary C: External systems (future)

Future integrations may query Azure read-only telemetry sources (Activity Logs, Log Analytics). Until implemented, these are scaffolds only.

## Read-only design (what “safe” means here)

The MVP is designed to be “safe” in two ways:

1. **No destructive actions**: no code path performs Azure resource modifications, service restarts, firewall changes, route changes, or cache flushing.
2. **No credential handling**: the repo does not prompt for, store, or transmit credentials.

Note: some PowerShell scripts may create output directories/files **only when `-OutputPath` is provided**. This is treated as an evidence-handling convenience, not system configuration change.

## No live Azure destructive actions

Current posture:

- Azure client code is **scaffolded** and does not execute live requests in the MVP.
- Any future Azure integration must remain **read-only** initially and include explicit guardrails (e.g., no SDK calls that mutate resources).

## Secrets: no storage in repo

Rules:

- No secrets, tokens, certificates, connection strings, or real tenant/subscription identifiers in git history.
- Examples must use placeholders like `<tenant-id>` and `<subscription-id>`.
- Evidence artifacts from real incidents must never be committed to the repo.

## Webhooks (Teams) are secrets (implemented, disabled by default)

This MVP now includes a **Microsoft Teams webhook dispatcher**, but it is **disabled by default** and requires explicit enablement flags.

Security expectations:

- Treat `TEAMS_WEBHOOK_URL` as a **secret**.
- Do not print, log, or return webhook URLs in application output.
- Store webhook URLs in a secret store (CI secrets, app settings, Key Vault in future deployment), not in git-tracked files.

## Future authentication approach (managed identity)

If/when Azure queries are implemented, the preferred approach is:

- **Managed identity** (workload identity) where possible
- otherwise a secure secret store (e.g., Key Vault) with short-lived tokens and strict access controls

Avoid long-lived client secrets in developer machines and avoid placing secrets in config files.

## Least privilege principle (future read-only access)

Any future Azure integration should:

- request only read-only permissions required for incident triage
- avoid subscription-wide access if a narrower scope is sufficient
- be transparent about required roles (documented)

## Evidence collection safety model

Evidence collection is **operator-driven**:

- Python produces correlation outputs and “what to collect” manifests.
- PowerShell scripts are **manual** and **read-only** templates; they should not:
  - ask for credentials
  - write to system configuration
  - enable logging, packet capture, or tracing automatically
  - attempt remediation

Before using in a real environment, review evidence handling:

- where outputs are stored
- how long they are retained
- who can access them
- whether outputs contain customer-identifying data


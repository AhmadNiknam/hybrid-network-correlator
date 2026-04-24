# Security Policy

## Supported status

This repository is a **learning / MVP project** intended for **read-only incident correlation** using **mock fixtures**.

- **Support level**: best-effort community support only
- **Security updates**: no guaranteed SLA
- **Not production-hardened**: do not rely on this repo for security-sensitive operations without an independent review

## How to report security issues

If you believe you have found a security vulnerability:

- **Do not** open a public GitHub issue with sensitive details.
- Send a report via **GitHub Private Vulnerability Reporting** (preferred) if enabled for the repo.
- If private reporting is not available, open a minimal issue titled **"Security report: request for private contact"** and include **no technical details**, then share details only after a maintainer replies with a private channel.

Please include:

- A clear description of the issue and potential impact
- Steps to reproduce (using **sanitized** inputs only)
- A suggested fix or mitigation if you have one

## Learning/MVP disclaimer and warranty

This project is provided **as-is**, without warranty of any kind.

- **No warranty**: express or implied (including merchantability, fitness for a particular purpose, and noninfringement)
- **Use at your own risk**: you are responsible for validating safety, permissions, and outputs in your environment

## Safe handling of secrets (important)

This repository **must not** contain real:

- passwords, tokens, API keys, connection strings
- tenant IDs, subscription IDs, client IDs
- private keys/certificates, SSH keys, VPN configs

Guidelines:

- Use environment variables for any future integration configuration.
- Use placeholders in docs and samples (e.g., `<tenant-id>`, `<subscription-id>`).
- Never paste real incident artifacts into issues, PRs, or logs. Treat evidence as potentially sensitive.

If you accidentally commit a secret:

- rotate/revoke it immediately
- remove it from history (do not rely on a normal revert)
- assume it has been compromised if it was pushed to any remote

## Scope of current functionality (trust/safety boundaries)

### What the repo does today (MVP)

- **Reads local fixtures** under `samples/` and produces correlation outputs (`text` / `json` / `dashboard`).
- Generates **prepare-only** evidence collection manifests (instructions/data) and does **not** execute diagnostics automatically.
- Includes optional PowerShell scripts under `scripts/powershell/` intended for **manual**, **read-only** evidence collection.

### What the repo does not do (intentionally)

- No live Azure authentication or query execution in the MVP.
- No write or destructive operations against Azure resources.
- No automated remediation.
- No credential prompting, storage, or secret management.

### Data safety model (current)

- Input data is expected to be **sanitized** and non-sensitive in this public repo.
- Any real-world usage would involve processing evidence that may contain hostnames, IPs, and configuration details; treat all outputs as **sensitive** and handle per your organization’s policy.

For more detail, see `docs/security-model.md`.


# Portfolio Summary — Hybrid Network Correlator

This document is designed to help you present the project consistently across your README, LinkedIn, and resume. It stays within the repo’s stated MVP scope: **mock-first**, **deterministic**, **safe local evaluation**, and **no completed live Azure integration**.

## Recruiter-friendly summary

Hybrid Network Correlator is a portfolio-grade Python project that models how network/cloud administrators can triage **hybrid connectivity incidents (Azure ↔ on‑prem)**. It turns common troubleshooting steps into a repeatable workflow that outputs an **evidence-backed probable-cause ranking** and recommended next checks. The MVP is intentionally safe: it runs on sanitized fixtures and does not perform live Azure actions.

## Technical summary

- **Input (today)**: deterministic scenario fixtures under `samples/` representing a scoped incident time window and evidence signals.
- **Core logic**: deterministic, explainable scoring across a small hypothesis set (e.g., NSG change, UDR route change, VPN gateway issue, DNS issue, unknown).
- **Outputs**:
  - `text`: admin-friendly report for incident notes
  - `json`: stable structured summary (regression-friendly)
  - `dashboard`: compact JSON payload intended for future ingestion
- **Safety model**:
  - mock-first fixtures for repeatability
  - no authentication / no live Azure queries in the MVP
  - no write/remediation actions
  - “prepare-only” evidence guidance (manifests describing what to collect next)
  - notification templates + simulated dispatch (no live sending)

## Skills demonstrated

- Hybrid incident triage framing (Azure ↔ on‑prem failure modes: NSG/UDR/VPN/DNS)
- Deterministic correlation/scoring design (explainable, testable outputs)
- Safety-first automation boundaries (read-only / prepare-only posture)
- Testability and engineering hygiene (fixtures + unit tests + stable output contracts)
- Operator-focused documentation (architecture, security model, roadmap, release notes)

## Tools and technologies

- Python 3.x
- `unittest` (local unit tests)
- PowerShell (optional, manual diagnostic templates)
- KQL templates (placeholders for future Log Analytics queries)
- Git/GitHub workflow documentation (release notes, security posture docs)

## GitHub repository link

- **Repository**: `<GITHUB_REPO_URL>`

## One-paragraph version (for a personal portfolio site)

Hybrid Network Correlator is a mock-first Python MVP that demonstrates a safe, repeatable approach to triaging hybrid network incidents between Azure and on‑prem environments. It correlates evidence signals into an explainable ranking of probable causes and produces admin-friendly summaries plus structured JSON outputs for future integrations. The project prioritizes deterministic behavior, unit-test stability, and explicit read-only/prepare-only boundaries, with future Azure integration planned as read-only telemetry ingestion rather than production deployment claims.


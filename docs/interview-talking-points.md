# Interview Talking Points (Hybrid Network Correlator)

Use this as a quick reference in interviews. It’s written to be **professional, honest, and aligned to the repo’s MVP scope** (mock-first fixtures, deterministic scoring, no production deployment claims, no live Azure integration completed).

## Short explanation (15–20 seconds)

Hybrid Network Correlator is a **mock-first Python MVP** that helps triage **Azure ↔ on‑prem connectivity incidents** by correlating evidence signals (currently sanitized fixtures) into an **administrator-friendly summary**: ranked probable causes, supporting evidence, and recommended next checks.

## The problem it solves

- **Hybrid incidents are cross-domain**: responders jump between change history, routing/NSG checks, VPN/ER health, DNS, and host-level diagnostics.
- **Triage is repetitive and inconsistent**: two people can follow different paths and miss the same root cause.
- **The project standardizes “first 15 minutes” triage** into a repeatable workflow with explainable outputs.

## Architecture (high-level)

What exists today (MVP):

- **Correlation engine** (`src/correlator/`)
  - CLI orchestration, scenario loading from fixtures, deterministic scoring, and output rendering.
- **Evidence scaffolding (prepare-only)** (`src/evidence/`)
  - Produces “what to collect next” manifests as data objects (does not execute diagnostics).
- **Azure integration scaffolding (placeholders)** (`src/integrations/`)
  - Config loading and KQL template helpers; **no live auth/query execution in the MVP**.
- **Notifications scaffolding (v1.1.0, simulated)** (`src/notifications/`)
  - Message models/templates + simulated dispatch; **no live sending**.

Data flow (today):

- **Fixtures (`samples/`) → scoring → outputs** (`text`, `json`, `dashboard`)

Forward path (documented, not claimed as complete):

- Swap fixture loaders with **read-only Azure queries** (Activity Logs + Log Analytics) normalized into the same internal evidence model.

## Why deterministic scoring first (instead of “AI-first”)

- **Explainability for operators**: admins need to understand *why* a hypothesis ranks highest and what evidence supports it.
- **Regression-friendly**: deterministic fixtures + stable outputs enable unit tests and safe iteration.
- **Safety and scope control**: avoids overclaiming intelligence, avoids unpredictable behavior, and keeps trust boundaries clear.
- **AI as an additive layer later** (optional): once evidence models are robust, AI can help with narrative summarization or “next checks” phrasing—without changing the core evidence logic.

## Security model (what you can say confidently)

Based on `docs/security-model.md` and the repo’s design:

- **Mock-first / local evaluation**: MVP runs against sanitized fixtures, not live environments.
- **No live Azure actions**: no authentication and no query execution in the current MVP.
- **No destructive behavior**: no remediation, no writes, no configuration changes.
- **Operator-in-the-loop diagnostics**: PowerShell scripts (if used) are manual, read-only templates; the Python tool doesn’t execute them.
- **No secrets in the repo**: examples use placeholders; evidence artifacts from real incidents should not be committed.

## Limitations (be direct)

- **No live Azure integration yet**: Azure query execution/auth is scaffolded only.
- **Limited hypothesis coverage**: small explicit set (NSG/UDR/VPN/DNS/UNKNOWN).
- **No automated diagnostics execution**: evidence collection remains operator-driven.
- **No production deployment claims**: this is a portfolio-grade MVP intended for safe local evaluation and iteration.
- **Notifications are scaffolding only**: message formatting exists; delivery is simulated and opt-in integrations are future work.

## What I would improve next (practical next steps)

- **Read-only Azure data collection**:
  - implement Activity Log + Log Analytics querying (still read-only)
  - normalize results into internal evidence models
- **Evidence bundle ingestion**:
  - define a standard “evidence pack” format (timestamps, artifacts, metadata)
  - validate + replay correlation deterministically for auditability
- **Expand scenario families**:
  - ExpressRoute patterns, firewall/proxy, DNS forwarding, asymmetric routing
- **Operational hardening**:
  - structured logging, error taxonomy, validation, deterministic replay guarantees
- **Integration contracts**:
  - stable webhook/ITSM payloads; optional dashboard integration without building UI into the core

## How it maps to common roles

### Network Analyst

- Demonstrates structured triage thinking across **NSG/UDR/VPN/DNS** failure modes.
- Shows **evidence-backed hypothesis ranking** and “next checks” guidance.
- Emphasizes **repeatability** and documented operator workflows.

### IT Administrator

- Produces **admin-friendly output** for incident notes and handoffs.
- Encodes a standard workflow for the “first response” phase.
- Respects safety boundaries: prepare-only evidence guidance, no hidden automation.

### Cloud Administrator / Cloud Operations

- Aligns with **least privilege** and future **read-only** integrations.
- Uses contracts that could feed operational tooling (dashboard/webhook/ITSM) without overbuilding UI.
- Shows good engineering hygiene: deterministic fixtures, unit tests, explicit non-goals, release notes.

## Common interview questions (suggested answers)

- **“Is this in production?”**  
  “No. It’s a public MVP designed for safe local evaluation with mock fixtures. Production readiness would require authenticated read-only integrations, hardening, and governance work.”

- **“Does it integrate with Azure today?”**  
  “Not live. Azure integration is scaffolded (config + query templates), but the MVP does not authenticate or run queries.”

- **“Why not just use an LLM to infer the root cause?”**  
  “Because responders need explainable, testable behavior. Deterministic scoring creates a trustworthy baseline; AI can be layered later for summarization once the evidence model is solid.”


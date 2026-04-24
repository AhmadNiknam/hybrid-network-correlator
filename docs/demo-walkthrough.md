# Demo Walkthrough (Portfolio-Ready)

This walkthrough is designed for a **~3 minute live demo** of the Hybrid Network Correlator MVP. It stays honest about what is implemented today (mock fixtures + deterministic scoring) and what is intentionally scaffolded (read-only Azure integrations, notifications).

## Pre-demo setup (30 seconds)

- Start in the repository root.
- Have a terminal visible.
- Optional: open `docs/architecture.md` in an editor tab for a quick architecture reference.

### Note about scenario names

This repo’s `README.md` documents scenario slugs like `scenario1_nsg_rule_change`. This demo script includes the **exact commands requested** (using `--scenario scenario1`). If `scenario1` is not a valid scenario slug in your local repo state, use the documented slug that matches the scenario you want to show (for example `scenario1_nsg_rule_change`).

## 3-minute demo script

### 0:00–0:20 — Elevator pitch

“Hybrid Network Correlator is a small, safe MVP that helps administrators triage **Azure ↔ on‑prem connectivity failures**. Instead of manually bouncing between change history and telemetry, it correlates a scoped incident against evidence signals and produces a **ranked, explainable probable-cause summary** with recommended next checks.”

Key honesty statement:

“In this MVP, the evidence comes from **sanitized fixtures** in `samples/` so behavior is deterministic and testable. Live Azure queries are **not implemented yet**—only scaffolded.”

### 0:20–1:40 — Show the text report output (core value)

Run:

```powershell
python -m src.correlator.main --scenario scenario1 --format text
```

What this demonstrates:

- The **end-to-end workflow**: scenario ingestion → deterministic scoring → admin-friendly report.
- A **ranked list of probable causes** (hypotheses like NSG/UDR/VPN/DNS/UNKNOWN).
- **Explainability**: evidence supporting/contradicting the top hypothesis and “next checks.”

Talk track while output is visible:

- “This output is written for an on-call admin. It summarizes the incident scope, the likely cause, and the next checks to confirm.”
- “The scoring is deterministic so we can regression-test it and keep it stable as we expand scenarios.”

Suggested screenshot(s) to capture:

- Terminal screenshot showing: incident ID, impacted target, Top 3 probable causes with confidence, and the first few ‘next checks.’
  - Suggested filename later: `docs/assets/screenshots/cli-text-report-scenario1.png`

### 1:40–2:20 — Show the dashboard payload format (integration-friendly)

Run:

```powershell
python -m src.correlator.main --scenario scenario1 --format dashboard
```

What this demonstrates:

- A **compact JSON payload** intended for future ingestion (dashboard / ITSM / webhook).
- Separation of concerns: the core engine produces stable data contracts; UI and integrations can come later without changing the scoring logic.

Suggested screenshot(s) to capture:

- Cropped view showing keys like: incident ID, scenario, ranked causes list, and summary text.
  - Suggested filename later: `docs/assets/screenshots/dashboard-payload-scenario1.png`

### 2:20–2:55 — Prove repeatability with tests (engineering discipline)

Run:

```powershell
python -m unittest -v
```

What this demonstrates:

- The project is built to be **repeatable** and **safe to evaluate locally**.
- Unit tests validate **stable output shapes** and enforce **safety boundaries** (no live actions).

Suggested screenshot(s) to capture:

- Test output showing multiple passing tests and the overall `OK`.
  - Suggested filename later: `docs/assets/screenshots/unittest-pass.png`

### 2:55–3:00 — Close (what’s next)

“Next, I’d replace fixtures with **read-only Azure Activity Log / Log Analytics queries** while keeping the same internal evidence models and tests. I’d keep it operator-friendly and audit-friendly: deterministic replay, explicit RBAC assumptions, and no remediation/writes.”

## How to explain “mock mode” honestly (recommended phrasing)

Use language like:

- “This MVP runs on **sanitized, deterministic fixtures** so reviewers can run the same scenario and get the same output.”
- “It’s **mock-first by design**: before I connect to live Azure data, I want the correlation rules, data contracts, and tests to be solid.”
- “The Azure integration is a **scaffold** (config + query templates / placeholders). There is **no live authentication or query execution** in the MVP.”

Avoid language like:

- “This pulls from Azure today” (it doesn’t).
- “Production-ready / deployed” (not claimed).

## How to explain future Azure integration (without over-claiming)

Keep it specific and bounded:

- **Goal**: swap fixture loaders with read-only collectors that pull from:
  - Azure Activity Logs (recent changes)
  - Log Analytics (connectivity telemetry signals)
- **Approach**:
  - Normalize query results into the same internal evidence models used by fixtures.
  - Maintain deterministic tests by recording sanitized sample responses and validating output contracts.
  - Start **read-only** with least privilege, preferably managed identity (when running in Azure later).
- **Non-goal (initially)**: no remediation, no resource changes, no auto-executed diagnostics.

## Suggested screenshot checklist (portfolio-friendly set)

Capture these from **sanitized** scenarios only:

- **Text report**: ranked causes + evidence + next checks.
- **Dashboard payload**: compact JSON payload view.
- **Unit tests**: passing test suite output.
- Optional (if present in outputs): a **prepare-only evidence manifest** snippet that clearly reads like “what to collect next,” not automation that executes diagnostics.

## Quick Q&A prompts (if you get interrupted mid-demo)

- “Is this using AI?”  
  “Not in the MVP. It’s deterministic scoring for explainability and stable testing. AI could be added later for summarization, but only on top of a trustworthy evidence model.”

- “Does it change anything in Azure?”  
  “No. The MVP is designed to be safe: **no authentication, no query execution, no writes**. Future integration would start read-only.”


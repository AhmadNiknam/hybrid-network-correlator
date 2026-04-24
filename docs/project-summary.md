## Hybrid Network Correlator — Project Summary (MVP)

### Project title

**Hybrid Network Correlator**

### Problem statement

Hybrid connectivity incidents (Azure VM ↔ on‑prem endpoint) often trigger a manual, time‑pressured triage process across:

- recent change history (what changed, by whom, when)
- telemetry signals (symptoms, timing, blast radius)
- diagnostic evidence (NSGs/UDRs, VPN/ER status, DNS, routing, host-level tests)

That investigation is repetitive, error‑prone, and hard to standardize—especially for on‑call responders who need a fast, evidence-backed starting point.

### Solution overview

Hybrid Network Correlator is a **mock-first, deterministic incident-correlation workflow** designed for **IT and network administrators**. Given a scoped alert payload and evidence signals (currently fixtures), it produces an **administrator-friendly triage summary**:

- ranked probable causes with confidence
- evidence supporting and contradicting each hypothesis
- recommended “next checks” to validate the likely cause

The MVP prioritizes **repeatability and explainability** over “black box” reasoning and keeps safety boundaries explicit (**read-only** and **prepare-only** by design).

### Current implemented capabilities (MVP)

- **Scenario ingestion from deterministic fixtures** under `samples/`
- **Rule-based scoring and correlation** within an incident time window
- **Hypothesis set (current)**:
  - `NSG_CHANGE`
  - `ROUTE_UDR_CHANGE`
  - `VPN_GATEWAY_ISSUE`
  - `DNS_ISSUE`
  - `UNKNOWN`
- **Admin-friendly outputs**:
  - `text` report for responders
  - `json` detailed summary (stable output shape for tests)
  - `dashboard` compact JSON payload for future ingestion
- **Prepare-only evidence manifest scaffolding**:
  - generates “what to collect next” manifests as data (no execution)
- **Notification layer scaffolding (v1.1.0)**:
  - standardized message models and templates for email/SMS/webhook
  - dispatch behavior is **simulated**; **no live sending**
- **Unit tests** to validate output stability and safety constraints

### Architecture overview

The MVP is implemented as a small, testable Python module set under `src/`:

- **Correlation engine** (`src/correlator/`)
  - CLI orchestration, scenario loading, deterministic scoring, and rendering
- **Evidence scaffolding (prepare-only)** (`src/evidence/`)
  - evidence manifest models, “collection action request” objects, and JSON packaging
- **Azure integration scaffolding (read-only placeholders)** (`src/integrations/`)
  - environment-based config loader, client shape, and KQL template helpers
- **Notifications scaffolding (prepare-only)** (`src/notifications/`)
  - notification models, templates, and a simulated dispatcher

Data flow (today): **fixtures → scoring → report outputs**. A forward path is documented for swapping fixtures with **read-only** Azure query results (future phase).

### Security and trust model

The MVP is intentionally safe to evaluate locally:

- **Mock-first / local execution**: correlation runs against sanitized fixtures; no live Azure auth or querying in the MVP.
- **Read-only boundaries**: no code paths perform Azure write operations, remediation, or configuration changes.
- **Operator-in-the-loop evidence**:
  - Python produces correlation outputs and “what to collect” manifests.
  - PowerShell diagnostics are **manual, read-only templates** (the Python layer does not execute them).
- **No secrets in the repo**:
  - examples use placeholders (no tenant/subscription IDs, tokens, connection strings)
  - evidence artifacts from real incidents should not be committed
- **Least privilege (future)**:
  - planned Azure integration is intended to remain read-only initially and use managed identity where possible.

### Technologies used

- **Python 3.x**
- **PowerShell** (optional, manual Windows/on‑prem diagnostics templates)
- **KQL templates** (placeholders for future Log Analytics queries)
- **Unit testing** with Python `unittest`
- **Git/GitHub**-oriented documentation and release notes

### Skills demonstrated

- **Hybrid networking triage thinking** (Azure ↔ on‑prem failure modes, evidence selection, operator next steps)
- **Deterministic correlation design** (explainable scoring, stable regression fixtures)
- **Safety-first automation** (read-only / prepare-only boundaries; no hidden side effects)
- **Testable implementation** (unit tests + stable output contracts)
- **Operator-focused documentation** (vision, use cases, architecture, security model, release notes)

### Current limitations

- **No live Azure integration yet**: authentication and query execution against Azure Activity Logs / Log Analytics are scaffolded only.
- **No production deployment claims**: this is a public MVP designed for learning and portfolio-grade iteration.
- **No automated diagnostics execution**: PowerShell scripts are not run by the tool; evidence collection remains operator-driven.
- **Limited hypothesis coverage**: the MVP covers a small, explicit set of causes; it may return `UNKNOWN` when evidence is insufficient.
- **No end-to-end operational workflow integration**: notifications are formatted but not delivered; ITSM/chat-ops integrations are not implemented.

### Future roadmap (directional)

- **Phase 2 (read-only Azure integration)**:
  - implement authenticated, read-only querying for Activity Logs and Log Analytics
  - normalize query results into internal evidence models without breaking existing fixture-based tests
- **Phase 3 (evidence bundle ingestion)**:
  - standardize evidence pack format (manifests + operator-collected artifacts)
  - ingest/validate evidence bundles for correlation replay and auditability
- **Phase 4 (operational hardening + integrations)**:
  - structured logging, error taxonomy, input validation, deterministic replay
  - optional dashboard/ITSM/webhook integration contracts
  - opt-in, audited notification delivery via services such as Azure Communication Services or Logic Apps


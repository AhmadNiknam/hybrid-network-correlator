## Vision

### One-sentence description

Hybrid Network Correlator helps an IT administrator quickly understand **why connectivity between an Azure VM and an on-prem endpoint degraded or failed**, by correlating recent Azure changes with telemetry and diagnostic evidence, and producing a **probable-cause summary**.

### Problem

When hybrid connectivity breaks, triage usually becomes a manual hunt across:

- Change history (who changed what and when)
- Network telemetry (symptoms, timing, blast radius)
- Diagnostic evidence (routing, NSGs, firewall logs, VPN/ER status, DNS)

This is time-consuming and error-prone, especially under outage pressure.

### Target users

- Network administrators
- Infrastructure/cloud operations engineers
- On-call responders for hybrid connectivity

### MVP goal (Phase 1)

Deliver a narrow, practical workflow that:

- Accepts an incident “alert payload” (mock JSON)
- Correlates it with a fixed set of evidence signals (mock JSON)
- Produces a short report:
  - Most likely cause(s), with confidence score
  - Evidence that supports or contradicts each cause
  - Suggested next verification steps

### What “success” looks like

- The report is understandable by an IT admin without reading code.
- For common failure patterns (e.g., NSG change, UDR change, gateway issue), the tool points to the right hypothesis and the evidence that led there.
- The correlation outcome is repeatable and explainable (deterministic scoring).

### Product principles

- **Narrow before broad**: solve one scenario well before adding more.
- **Explainable output**: always show evidence and reasoning.
- **Mock first**: prove logic with mock data before connecting to Azure.
- **Read-only by default**: no automated changes to customer environments.
- **Security-first**: no secrets in the repo; least-privilege assumptions.

### Assumptions

- Focus is Azure VM ↔ on-prem endpoint connectivity.
- An incident has a bounded time window (start/end or “last N minutes”).
- Azure Activity changes near the incident window are relevant signals.
- Telemetry/evidence can be represented as structured events with timestamps and properties.

### Out of scope (until later phases)

- Any “write” operations in Azure (remediation, configuration changes)
- Full production hardening (RBAC model, audit trails, HA, etc.)
- A complete UI/dashboard (later phase)

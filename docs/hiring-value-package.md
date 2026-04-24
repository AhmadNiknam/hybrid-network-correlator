# Hiring Value Package — Hybrid Network Correlator (MVP)

This document is designed to help you present this repository in job applications and interviews in a **professional, honest, recruiter-friendly** way.

Scope clarity (important):
- This is a **public MVP** intended for **safe local evaluation**.
- It is **mock-first** and **deterministic** (fixtures → scoring → outputs).
- **No production deployment** is claimed or required for the project to be valuable.
- **No live Azure integration is completed** (Azure auth/query execution is scaffolded only).

---

## A) How this project creates hiring value (by role)

### IT Administrator
- **Standardizes first-response triage**: turns common “first 15 minutes” checks into a repeatable workflow with ranked hypotheses and “next checks.”
- **Produces admin-friendly outputs**: a concise text report for incident notes plus structured JSON for handoffs.
- **Safety-first posture**: clear boundaries (read-only / prepare-only) reduce risk and make it suitable for evaluation in restricted environments.

### Network Analyst
- **Encodes network troubleshooting logic** across common hybrid failure modes (NSG, UDR routing, VPN gateway instability, DNS).
- **Evidence-backed reasoning**: shows supporting and contradicting evidence for each probable cause (explainability over guesswork).
- **Time-window correlation**: demonstrates understanding of incident timelines and how “recent change” relates to symptoms.

### Cloud Administrator
- **Cloud ops mindset without overclaiming**: scaffolds a path to read-only Azure telemetry (Activity Logs / Log Analytics) while keeping the MVP offline.
- **Least-privilege and trust boundaries**: aligns with real enterprise patterns (managed identity preference, no secrets in repo, read-only intent).
- **Integration-ready outputs**: stable JSON shapes and a compact “dashboard” payload demonstrate thinking in contracts and downstream consumers.

### Infrastructure Support
- **Cross-domain clarity**: bridges cloud signals and on-prem diagnostics by pairing correlation outputs with operator-driven “what to collect next” manifests.
- **Practical documentation**: architecture + security model + release notes show you can document systems for maintainers and operators.
- **Repeatability under pressure**: highlights incident response hygiene: consistent steps, evidence traceability, and safe defaults.

### Junior DevOps / Automation
- **Automation boundaries and guardrails**: emphasizes “prepare-only” evidence guidance and simulated notifications to avoid unintended side effects.
- **Test discipline**: deterministic fixtures + stable output contracts + unit tests + CI demonstrate quality habits.
- **Operational thinking**: models how tools evolve from offline MVP → read-only integration → hardening, without claiming it’s already production-ready.

---

## B) What business problems it addresses

- **Inconsistent incident triage**: different responders follow different paths and miss signals; the project defines a consistent workflow.
- **Slow time-to-first-action**: provides a fast evidence-backed starting point (ranked causes + next checks) for on-call responders.
- **Poor handoffs and weak incident notes**: outputs are structured and admin-readable, supporting ticket updates and shift handoffs.
- **Risky “automation” in sensitive environments**: uses safe design (read-only / prepare-only) so evaluation doesn’t introduce changes to systems.
- **Hard-to-test operations logic**: deterministic fixtures and stable outputs enable regression testing of troubleshooting logic.

---

## C) Skills demonstrated (what you can credibly point to)

- **Troubleshooting logic**
  - Encodes common hybrid incident failure modes into explicit hypotheses and evidence checks.
  - Uses a time-windowed correlation approach (recent change + telemetry timing).
- **Automation mindset**
  - Turns a manual workflow into repeatable steps and standardized outputs.
  - Establishes guardrails (“safe by default,” operator-in-the-loop).
- **Python scripting**
  - CLI-driven execution, modular design, structured models, deterministic scoring and rendering.
- **PowerShell diagnostics**
  - Provides read-only, operator-run diagnostic templates for Windows/on-prem evidence collection (not auto-executed by Python).
- **Azure monitoring concepts**
  - Uses the right mental model (Activity Logs, Log Analytics/KQL templates) while being explicit that live querying is not implemented in the MVP.
- **Security awareness**
  - No secrets in repo; placeholders only; explicit trust boundaries; least-privilege and managed identity guidance for future phases.
- **Testing / CI**
  - Unit tests validate stable outputs and safety constraints; CI runs tests on push/PR.
- **Documentation**
  - Clear MVP scope, architecture, security model, roadmap direction, and release notes; written for operators (not only developers).

---

## D) How to explain this project honestly in interviews

Use this structure:

1) **What it is (one sentence)**  
“It’s a mock-first Python MVP that correlates hybrid connectivity incident signals into an explainable ranking of probable causes and recommended next checks.”

2) **Why it matters (one sentence)**  
“Hybrid incidents are repetitive and cross-domain; this standardizes the triage workflow and improves consistency and handoffs.”

3) **What’s implemented (2–3 bullets)**
- Deterministic fixtures → scoring → outputs (`text`, `json`, `dashboard`)
- Small hypothesis set (NSG/UDR/VPN/DNS/UNKNOWN) with evidence-for/against
- Prepare-only evidence manifests and simulated notification scaffolding (no live sending)

4) **What is explicitly not implemented (be direct)**
- No production deployment
- No live Azure authentication or query execution (scaffolding only)
- No automated PowerShell execution or remediation actions

5) **What you’d do next (shows maturity)**
- Implement optional **read-only** Azure data collection (Activity Logs + Log Analytics) with least privilege and managed identity
- Expand hypothesis coverage and strengthen validation/error taxonomy
- Improve evidence bundle ingestion and auditability (deterministic replay)

---

## E) What not to claim (avoid credibility damage)

- Do not claim it is **production deployed** or “running in Azure” today.
- Do not claim **live Azure integration** is implemented (auth + query execution are not completed).
- Do not claim it performs **automatic remediation** or makes changes to NSGs/routes/VPN/DNS.
- Do not claim it runs **automated diagnostics** on hosts; PowerShell is operator-run and read-only templates.
- Do not claim it uses “AI to find root cause” if the current design is deterministic scoring (you can say AI could be layered later for summarization, not core logic).


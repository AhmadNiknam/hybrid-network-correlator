# Interview Questions — Hybrid Network Correlator (Project Q&A)

This is a hiring-focused Q&A set for discussing the repository honestly. It stays aligned with the repo’s current state: **mock-first fixtures**, **deterministic scoring**, **prepare-only evidence guidance**, **simulated notifications**, **unit tests/CI**, **no production deployment**, and **no completed live Azure integration**.

---

## 1) Why did you build this?

**Strong sample answer**  
Hybrid connectivity incidents are repetitive and cross-domain: responders bounce between recent changes, routing/NSG checks, VPN health, DNS, and host-level evidence. I built a mock-first MVP that standardizes the first-response workflow into deterministic correlation outputs: ranked probable causes, evidence-for/against, and recommended next checks. It’s designed to be safe to evaluate locally and easy to extend.

**Short version**  
To standardize hybrid incident triage into an explainable, repeatable workflow.

---

## 2) What problem does it solve for a team?

**Strong sample answer**  
It reduces variance in early incident response. Instead of everyone troubleshooting differently, the tool produces a consistent triage summary and a structured “next checks” path. That helps with time-to-first-action, better incident notes, and cleaner handoffs between on-call responders.

**Short version**  
Faster, more consistent first-response triage and handoffs.

---

## 3) Why rule-based scoring first instead of an AI-first approach?

**Strong sample answer**  
Operators need explainability and predictability. Deterministic scoring lets you see exactly why a hypothesis ranks highest, and it’s regression-friendly because fixtures and outputs are stable for unit tests. I see AI as optional later for narrative summarization or phrasing, but not as a replacement for evidence-driven logic.

**Short version**  
Explainable, testable behavior first; AI can be additive later.

---

## 4) What are the current inputs and outputs?

**Strong sample answer**  
Today, inputs are deterministic incident fixtures under `samples/` representing an alert payload, recent activity, and telemetry observations within a time window. Outputs are: a responder-friendly text report, a detailed JSON summary with stable shape for tests, and a compact JSON payload intended for future dashboard ingestion.

**Short version**  
Fixtures in → ranked causes + evidence + next checks out (text/JSON).

---

## 5) What hypotheses does the MVP cover?

**Strong sample answer**  
The MVP intentionally covers a small, explicit set: NSG change, UDR/route change, VPN gateway issue, DNS issue, and UNKNOWN when evidence is insufficient. The goal is clarity and safe iteration rather than claiming broad coverage.

**Short version**  
NSG, UDR, VPN, DNS, or UNKNOWN.

---

## 6) What limitations exist today?

**Strong sample answer**  
There’s no live Azure authentication or query execution; the integration layer is scaffolded only. Diagnostics aren’t automated; PowerShell scripts are manual, read-only templates. Notifications are formatting + simulated dispatch only—no live sending. The hypothesis set is intentionally small, and UNKNOWN is a valid outcome when evidence is missing.

**Short version**  
Offline fixtures only; no live Azure; no automated diagnostics; limited scope.

---

## 7) How would you integrate Azure “for real” (read-only) in a next phase?

**Strong sample answer**  
I’d implement optional, explicitly enabled, read-only querying for Azure Activity Logs and Log Analytics. The key is to normalize live results into the same internal evidence models used by fixtures, so the scoring engine stays deterministic and existing tests remain valuable. I’d keep the default offline mode, and add a small number of integration tests that are opt-in and never run in CI by default.

**Short version**  
Read-only Activity Logs + Log Analytics → normalize → reuse existing scoring.

---

## 8) How would you secure credentials for a live Azure mode?

**Strong sample answer**  
Prefer managed identity when running in Azure, with least-privilege roles scoped to the required workspace/resource group. If a secret is unavoidable, store it in Key Vault and use short-lived tokens and tight access controls. In all cases, keep secrets out of git, use placeholders in docs, and make live mode explicitly enabled.

**Short version**  
Managed identity + least privilege; otherwise Key Vault; never commit secrets.

---

## 9) How would you prevent the tool from accidentally making changes in Azure?

**Strong sample answer**  
By design, keep the integration layer read-only and enforce guardrails: no SDK calls that mutate resources, explicit allowlists of read operations, and tests that fail if write-capable methods are invoked. Also keep live mode default-off behind a clear feature flag and document the trust boundaries.

**Short version**  
Read-only integration + guardrails + default-off live flag.

---

## 10) How would you scale this if you needed to process more incidents?

**Strong sample answer**  
First, separate concerns: ingestion, evidence retrieval (read-only), scoring, and rendering. The scoring itself is lightweight; scaling is mostly about I/O and concurrency of evidence retrieval. I’d implement caching for repeated queries by time window, add structured logging and error taxonomy, and optionally run the correlator as a stateless service (e.g., Functions later) that writes outputs to a queue or storage for downstream systems.

**Short version**  
Scale I/O and ingestion; keep scoring stateless; add caching and observability.

---

## 11) Why does CI/CD matter for an ops-focused tool like this?

**Strong sample answer**  
Because small logic changes can silently change incident outcomes. CI ensures unit tests validate output stability and safety boundaries on every push/PR. That reduces regressions, improves reviewer confidence, and creates a disciplined feedback loop—especially important when the “users” are responders relying on consistent triage outputs.

**Short version**  
It prevents regressions in incident outcomes and safety behavior.

---

## 12) How do you test something like incident correlation realistically without production data?

**Strong sample answer**  
By using sanitized fixtures that preserve the structure and timing logic without exposing sensitive data. Deterministic fixtures allow reproducible scenarios and stable expected outputs. Over time, you expand scenario families, add negative cases, and validate the evidence model—then optionally add a separate, opt-in layer for live environment validation.

**Short version**  
Sanitized deterministic fixtures + expected outputs; expand scenarios over time.

---

## 13) What would you improve next if you had more time?

**Strong sample answer**  
Phase 2 would be optional read-only Azure querying and normalization into internal evidence models. Then I’d expand hypothesis coverage (ExpressRoute patterns, firewall/proxy, DNS forwarding, asymmetric routing), improve input validation and error taxonomy, and formalize an “evidence pack” ingestion format for deterministic replay and auditability.

**Short version**  
Read-only Azure ingestion, expand hypotheses, improve validation/auditability.

---

## 14) What security concerns did you think about even in an MVP?

**Strong sample answer**  
Secrets hygiene (no secrets or real identifiers in repo), trust boundaries (repo vs operator environment vs future external systems), and least privilege for future live mode. Also evidence handling: real incident artifacts can contain sensitive hostnames/IPs, so the project emphasizes sanitized fixtures for public use and warns against committing real evidence.

**Short version**  
No secrets in repo, explicit trust boundaries, least privilege, sensitive evidence handling.

---

## 15) If you were asked “Is this production-ready?”, how do you answer?

**Strong sample answer**  
No—this is a portfolio-grade MVP designed for safe local evaluation. Production readiness would require live read-only integrations, hardening (logging, validation, error taxonomy), governance (RBAC, auditing), and careful evidence handling procedures. I’m explicit about what’s implemented and what’s still roadmap work.

**Short version**  
No—MVP only; production would require integration + hardening + governance.

---

## 16) Why include PowerShell diagnostics at all?

**Strong sample answer**  
Because hybrid incidents often require host- and network-adjacent evidence that isn’t purely “cloud telemetry.” The important boundary is that PowerShell is operator-run and read-only; the Python tool doesn’t execute it. The project focuses on guiding evidence collection safely, not automating risky actions.

**Short version**  
To support real hybrid troubleshooting—operator-run, read-only templates.

---

## 17) Why include notifications if you’re not sending anything yet?

**Strong sample answer**  
Because message formatting and payload contracts matter for operational workflows (paging, ticketing, chat-ops). The MVP includes scaffolding to standardize shapes early, but dispatch is simulated to avoid credentials/contact data and external side effects. It’s a safe way to design integration contracts without claiming live delivery.

**Short version**  
To standardize message contracts safely; dispatch is intentionally simulated.

---

## 18) What’s a good “30 second” explanation to a recruiter?

**Strong sample answer**  
It’s a Python MVP that models how to triage Azure ↔ on-prem connectivity incidents. It correlates incident signals into a ranked list of probable causes with evidence and next checks, using deterministic fixtures and unit-tested outputs. It’s intentionally safe: no production deployment, no live Azure querying, and no automated remediation.

**Short version**  
Explainable, testable hybrid incident triage MVP (safe/offline).


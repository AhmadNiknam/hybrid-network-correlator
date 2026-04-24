# LinkedIn Featured Section — Hybrid Network Correlator (MVP)

## Short text (Featured card)

Hybrid Network Correlator is a **mock-first Python MVP** for triaging **Azure ↔ on‑prem connectivity incidents**. It produces an **explainable probable-cause ranking** (with evidence-for/against) and recommended next checks, using deterministic fixtures and unit-tested outputs. **No production deployment** and **no completed live Azure integration** are claimed.

**GitHub**: `<GITHUB_REPO_URL>`

---

## Professional summary (2–4 sentences)

I built Hybrid Network Correlator to standardize the “first-response” phase of hybrid network incidents. The MVP correlates a scoped incident time window into ranked hypotheses (NSG/UDR/VPN/DNS/UNKNOWN) and generates admin-friendly summaries plus structured JSON outputs designed for future integrations. The project prioritizes safety and trust boundaries: mock-first fixtures, read-only / prepare-only posture, simulated notifications, and CI-backed unit tests.

---

## What value it shows (recruiter-friendly bullets)

- **Troubleshooting mindset**: evidence-backed hypothesis ranking and clear “next checks.”
- **Automation with guardrails**: prepares evidence collection guidance without running diagnostics or changing systems.
- **Python engineering hygiene**: modular design, stable output contracts, and unit tests with CI.
- **Cloud/ops awareness (honest scope)**: Azure monitoring concepts and a documented read-only integration path, without claiming it’s implemented.
- **Security awareness**: no secrets in repo, explicit trust boundaries, least-privilege guidance for future phases.

---

## Optional “what I’d do next” (one line)

Next step would be optional **read-only** Azure data collection (Activity Logs + Log Analytics) normalized into the existing evidence model, keeping deterministic scoring and tests intact.


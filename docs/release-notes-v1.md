# Release Notes — v1.0.0 (Public MVP)

## What this project demonstrates

Hybrid Network Correlator is a mock-first, deterministic incident-correlation workflow for hybrid connectivity troubleshooting (Azure ↔ on‑prem).

Given a scoped “connectivity failure” alert payload plus supporting fixtures, the tool produces an administrator-friendly summary that includes:

- A ranked list of probable causes with confidence and evidence
- A concise narrative summary suitable for incident notes
- Recommended next checks for responders
- Optional output shapes (`text`, `json`, and compact `dashboard`) designed for future ingestion

## Who it is for

- Network and infrastructure administrators who triage hybrid connectivity incidents
- Cloud operations engineers looking for safe, explainable correlation patterns
- Security/operations teams evaluating “evidence-first” workflows for incident response readiness
- Hiring managers and reviewers assessing practical engineering in a real-world ops domain

## Skills demonstrated

- Deterministic, explainable scoring and correlation (stable behavior; regression-friendly fixtures)
- Hybrid networking triage framing (NSG/UDR/VPN/DNS failure modes and operator decision points)
- Safety-by-design automation boundaries (read-only / prepare-only scaffolding; no hidden side effects)
- Test-driven stability for outputs and safety constraints (unit tests and expected JSON artifacts)
- Clear operator-focused documentation (architecture, non-goals, security model, and backlog)

## Future enterprise roadmap (directional)

The MVP is intentionally mock-first. The roadmap focuses on making the tool production-ready without compromising safety and auditability.

- **Read-only Azure integrations**: add authenticated, read-only querying for Activity Logs and Log Analytics with normalization into internal models.
- **Evidence bundle ingestion**: standardize an operator “evidence pack” format (files, timestamps, metadata) and support ingestion/validation.
- **Signal expansion**: broaden the hypothesis set and add scenario families (ExpressRoute, firewall/proxy, DNS forwarding, asymmetric routing).
- **Operational hardening**: structured logging, error taxonomy, input validation, and deterministic replay for audit/forensics.
- **Security and governance**: least-privilege guidance, managed identity support, and explicit RBAC assumptions for enterprise environments.
- **Dashboard integration**: define a stable contract for a dashboard/ITSM integration (without requiring UI as part of the core engine).


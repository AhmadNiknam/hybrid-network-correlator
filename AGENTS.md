# Agent Instructions

You are assisting with the Hybrid Network Correlator project.

## Project goal

Build a practical automation tool for network administrators that correlates Azure network incidents with recent changes and diagnostic evidence across Azure and hybrid/on-prem environments.

## MVP scope

The first MVP focuses on this scenario:

When connectivity between an Azure VM and an on-prem endpoint degrades or fails, the system should:

1. Receive or load an alert payload.
2. Inspect recent Azure activity changes.
3. Inspect network/availability telemetry.
4. Score likely root causes.
5. Produce a concise incident summary for an administrator.

## Important constraints

- Start with mock JSON data.
- Do not connect to live Azure until mock logic works.
- Use deterministic scoring first.
- Keep all code modular and testable.
- Document assumptions clearly.
- Do not introduce complex UI at this stage.

## Preferred implementation

- Python for core logic.
- Azure Functions later.
- KQL query templates later.
- PowerShell diagnostic scripts later.
- Bicep or Terraform later.

## Do not do

- Do not build the whole project at once.
- Do not add unnecessary frameworks.
- Do not hide assumptions.
- Do not hardcode credentials or environment-specific values.
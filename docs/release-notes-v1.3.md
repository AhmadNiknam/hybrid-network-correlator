# Release Notes - v1.3.0

v1.3.0 improves the operator workflow for notifications by making notification intent explicit at the CLI. The project remains a safe, mock-first MVP: no production deployment is claimed, live Azure querying is not implemented, and notification delivery remains disabled unless explicitly enabled.

## What changed since v1.2.0

v1.2.0 introduced explicit Teams webhook guardrails and enterprise notification guidance. v1.3.0 builds on that by exposing a clear CLI workflow:

- `--notify none` keeps the existing report-only behavior and is the default.
- `--notify teams` requests Teams notification handling after the incident summary is generated.
- Teams delivery remains controlled by environment configuration, including `TEAMS_ENABLED=true` and `TEAMS_WEBHOOK_URL`.
- Tests cover the notification workflow, including default no-op behavior, disabled Teams mode, missing webhook handling, mocked Teams delivery, and webhook URL redaction from CLI output.

## Why the CLI notification workflow matters

Incident correlation is most useful when the result can move into an administrator's operational workflow. A CLI-level notification switch gives operators a simple, auditable way to choose whether a run should only print a report or also attempt notification delivery.

This matters because it keeps intent visible:

- Local evaluation can continue with `--notify none`.
- Controlled Teams testing can use `--notify teams` without changing the core correlation command.
- JSON and dashboard outputs remain suitable for automation because notification status is kept separate from machine-parseable stdout.

## How to use it safely

Run the report-only workflow first:

```powershell
python -m src.correlator.main --scenario scenario1 --format text --notify none
```

To request Teams notification handling:

```powershell
python -m src.correlator.main --scenario scenario1 --format text --notify teams
```

Teams notifications are disabled by default. Real Teams delivery requires explicit runtime configuration:

- `NOTIFICATIONS_ENABLED=true`
- `TEAMS_ENABLED=true`
- `TEAMS_WEBHOOK_URL=<your Teams webhook URL>`

Treat `TEAMS_WEBHOOK_URL` as a secret. Do not commit it to git, print it in logs, or include it in sample output. For local testing, use environment variables or a local `.env` file that is not committed.

## Known limitations

- Live Azure authentication and query execution are still not implemented.
- The project does not perform remediation or write operations against Azure or on-prem systems.
- Evidence collection remains operator-driven; diagnostic scripts are not executed automatically.
- Email and SMS delivery are not implemented.
- Teams delivery requires a valid Teams webhook or workflow endpoint and explicit environment opt-in.
- This release does not add production deployment automation or claim production readiness.

## Future roadmap

Planned next steps remain focused on safe, practical operations:

- Add read-only Azure Activity Log and Log Analytics query execution behind explicit guardrails.
- Normalize live telemetry into the same evidence models used by mock scenarios.
- Expand evidence bundle ingestion while keeping diagnostics operator-controlled.
- Improve notification governance through brokered workflows such as Logic Apps or Power Automate.
- Add more hybrid connectivity scenarios and scoring rules while preserving deterministic test coverage.

## Release readiness

v1.3.0 is ready for GitHub release documentation as a docs-aligned MVP update. The release should be described as a safer CLI notification workflow over the existing Teams delivery guardrails, not as a production deployment or full incident-response platform.

## Hybrid Network Correlator

A practical incident-correlation tool for **network and infrastructure administrators** operating **hybrid connectivity** (Azure ↔ on-prem). The MVP is intentionally narrow and explainable: **deterministic, rule-based scoring** over **mock inputs**.

### Project purpose

Hybrid connectivity incidents often require a human to manually piece together:

- what changed recently (NSG / routes / gateway changes)
- what the symptoms look like (unreachable / packet loss / latency)
- what evidence supports each hypothesis

This project reduces time-to-triage by generating a concise, evidence-backed incident summary with recommended next checks.

### Current MVP capabilities

The implemented MVP provides:

- **Mock scenario ingestion**: loads an alert payload plus related activity/telemetry fixtures from `samples/`
- **Rule-based correlation**: ranks likely causes across a small, practical hypothesis set:
  - `NSG_CHANGE`, `ROUTE_UDR_CHANGE`, `VPN_GATEWAY_ISSUE`, `DNS_ISSUE`, `UNKNOWN`
- **Three output formats**:
  - `text`: administrator-friendly report
  - `json`: detailed incident summary JSON (stable for tests)
  - `dashboard`: compact JSON summary (for later UI ingestion)
- **Evidence manifest scaffolding (prepare-only)**: builds a machine-readable “what evidence to collect next” manifest without executing any diagnostics

### Safety note (Azure + evidence collection)

- **Azure integration is scaffolded/read-only only**: `src/integrations/` contains placeholder configuration and query templates; **live authentication and live queries are not implemented**.
- **Evidence collection is scaffolded/prepare-only only**: the Python evidence layer creates **action requests** and **operator instructions**; it does **not** execute PowerShell, start packet captures, or run live probes.

### Repository structure

- `src/`: Python correlation engine (CLI + scoring + output rendering) and scaffolding modules
  - `src/correlator/`: CLI entrypoint, scenario loader, scoring engine, reporting
  - `src/evidence/`: evidence manifest model + prepare-only “collection action” requests
  - `src/integrations/`: Azure config + KQL template scaffolding (read-only placeholders)
  - `src/tests/`: unit tests (MVP behavior + output formats + scaffolding safety)
- `samples/`: deterministic JSON fixtures used by the MVP and unit tests
- `scripts/powershell/`: optional, read-only diagnostic scripts admins can run manually
- `docs/`: architecture, backlog, and operator-focused documentation

### How to run the correlation engine

From the repository root:

```powershell
# Text report (default)
python -m src.correlator.main --scenario scenario1_nsg_rule_change --format text
```

Notes:

- The `--scenario` value can be a full slug (recommended) such as:
  - `scenario1_nsg_rule_change`
  - `scenario2_udr_route_change`
  - `scenario3_vpn_tunnel_instability`
- A short selector like `scenario1` may work, but if multiple fixtures match, the selection is deterministic and may not be what you expect.

### How to run output formats

#### Text (admin report)

```powershell
python -m src.correlator.main --scenario scenario1_nsg_rule_change --format text
```

#### JSON (detailed incident summary)

```powershell
python -m src.correlator.main --scenario scenario1_nsg_rule_change --format json
```

#### Dashboard (compact JSON)

```powershell
python -m src.correlator.main --scenario scenario1_nsg_rule_change --format dashboard
```

### How to run unit tests

From the repository root:

```powershell
python -m unittest discover -s src\tests -p "test_*.py"
```

### PowerShell diagnostic script overview

For Windows / on-prem evidence collection during an incident, this repo includes **optional, read-only** scripts under `scripts/powershell/` that produce JSON output you can save and attach to an incident record:

- `Test-NetworkPath.ps1`: DNS + reachability + TCP checks (optional traceroute-style evidence)
- `Get-DnsDiagnostics.ps1`: DNS client/server settings and resolution attempts
- `Get-WindowsNetworkSnapshot.ps1`: point-in-time network configuration snapshot

See `docs/powershell-diagnostics.md` for usage details and safety guidance.

### Key documents

- `docs/architecture.md`: implemented module architecture and end-to-end data flow
- `docs/backlog.md`: what’s completed, what’s remaining, and recommended next work
- `docs/powershell-diagnostics.md`: safe, read-only Windows/on-prem evidence collection scripts

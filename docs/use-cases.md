## Use cases

This project intentionally starts with **one MVP scenario**. Other use cases are listed to clarify what is **out of scope** for the MVP.

### Primary MVP use case (Phase 1)

#### Scenario

Connectivity between an **Azure VM** and an **on-prem endpoint** (IP or FQDN) degrades or fails.

Examples of symptoms:

- VM cannot reach on-prem endpoint (timeouts / unreachable)
- Latency spike or intermittent packet loss
- Specific ports fail (e.g., 443 fails, ICMP still works)

#### Inputs (MVP)

- An “alert payload” (mock JSON) containing:
  - Azure VM identifier (name/resource id)
  - On-prem endpoint (IP/FQDN) and relevant ports/protocols (if known)
  - Time window (incident start/end, or “last N minutes”)
  - Symptom labels (loss/latency/unreachable)
- A set of mock evidence feeds (mock JSON), such as:
  - Azure Activity changes (NSG/UDR/gateway-related changes)
  - Telemetry signals (simple availability status, connection failure events)
  - Diagnostic results (pre-captured routing/NSG evaluation summaries)

#### Output (MVP)

A concise report suitable for an IT administrator:

- Probable cause ranking (rule-based scores)
- Evidence list per hypothesis (supporting and contradicting)
- Next checks (“verify X by looking at Y”)
- Clear boundaries (“what this report does not prove”)

### Secondary use cases (later phases)

- **Read-only Azure Log Analytics queries**: pull relevant KQL results for the incident window.
- **Evidence collection bundles**: gather and attach diagnostics (still read-only).
- **Dashboards and team workflows**: case tracking, history, and reporting.

### Explicitly out of scope (not MVP)

- Automated remediation or self-healing
- Changes to customer environments (NSG/UDR/firewall edits)
- Broad multi-incident analytics (“all incidents across the tenant”)
- Full discovery of all hybrid topology dependencies
- Non-hybrid incidents (pure on-prem, pure Azure without on-prem endpoint)

### Assumptions and constraints

- The MVP assumes the incident is scoped to a known VM and endpoint.
- The tool may not identify a single root cause; it should present **probable causes with evidence**.
- If required evidence is missing, the tool should say so and list what would be needed.

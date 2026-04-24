## Backlog and roadmap

This backlog is organized by **phases**. Each phase should be “demo-able” and should keep scope narrow.

### Phase 1: mock data + rule-based correlation (MVP)

**Goal**: Prove the correlation workflow end-to-end using mock JSON and deterministic scoring.

- **Define the data contracts (docs-first)**
  - Alert payload shape (VM, endpoint, time window, symptoms)
  - Evidence event shape (timestamp, category, summary, attributes)
  - Acceptance: docs clearly describe fields and examples.

- **Define MVP hypotheses and scoring approach**
  - Start with a small hypothesis set (NSG, UDR, gateway, DNS, on-prem firewall, unknown)
  - Acceptance: scoring rules are explainable and attach evidence.

- **Create mock evidence fixtures (documentation only for now)**
  - Example incident payload + example evidence lists
  - Acceptance: examples cover at least 3 scenarios (e.g., NSG change, UDR change, gateway issue).

- **Define the MVP report format**
  - Probable causes ranked + evidence bullets + next checks
  - Acceptance: sample report reads like something an on-call admin would want.

### Phase 2: read-only Azure Log Analytics integration

**Goal**: Replace mock evidence with read-only queries (still no remediation).

- **Identify required Azure data sources**
  - Activity logs for change correlation
  - Network-related telemetry available in Log Analytics for the scenario
  - Acceptance: documented list of tables/signals and what each provides.

- **Draft KQL query templates (read-only)**
  - “Recent activity changes near incident window”
  - “Network health/connection failure signals”
  - Acceptance: templates documented with placeholders (no tenant/sub IDs in repo).

- **Map query outputs to NormalizedEvent**
  - Acceptance: documented normalization mapping and edge cases (missing fields, partial data).

### Phase 3: evidence collection

**Goal**: Gather a richer, incident-specific evidence bundle (still read-only).

- **Define evidence collection checklist by hypothesis**
  - For each hypothesis, list specific evidence to collect and where to find it
  - Acceptance: admin-friendly checklist and what each item confirms/denies.

- **Document script/runbook approach (no actual scripts yet)**
  - Azure-side diagnostics (gateway status, effective routes where appropriate)
  - On-prem collection expectations (firewall logs, routing, DNS)
  - Acceptance: clear inputs/outputs and least-privilege assumptions.

### Phase 4: dashboard + production hardening

**Goal**: Operationalize the workflow for repeat use.

- **Dashboard requirements**
  - Incident list, detail view, evidence drill-down, export/share report
  - Acceptance: documented UI requirements and non-goals.

- **Hardening requirements**
  - Auditability, RBAC assumptions, error handling, performance constraints
  - Acceptance: documented operational checklist and risks.

### Cross-cutting non-goals (until later)

- Automated remediation
- Full topology graph discovery
- Real-time streaming pipeline
- “Black box” root-cause reasoning without evidence traceability

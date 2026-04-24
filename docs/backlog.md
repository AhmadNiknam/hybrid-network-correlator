## Backlog and roadmap

This backlog is organized by **phases**. Each phase should be “demo-able” and should keep scope narrow.

### Phase 1: mock data + rule-based correlation (MVP)

**Goal**: Prove the correlation workflow end-to-end using mock JSON and deterministic scoring.

#### Completed (Phase 1)

- **Implemented scenario fixtures and loader**
  - Deterministic JSON fixtures under `samples/` (alert, activity log, telemetry, expected summary)
  - Scenario slug resolution and consistent file layout
- **Implemented deterministic correlation and scoring**
  - Rule-based scoring within incident time window
  - Confidence computation and top-3 ranking
  - Current hypothesis set: `NSG_CHANGE`, `ROUTE_UDR_CHANGE`, `VPN_GATEWAY_ISSUE`, `DNS_ISSUE`, `UNKNOWN`
- **Implemented admin-facing outputs**
  - `text`: admin report
  - `json`: detailed summary
  - `dashboard`: compact JSON summary for future UI ingestion
- **Implemented prepare-only evidence manifest scaffolding**
  - Evidence manifest model and safe “collection action request” objects
  - Manifest JSON writer to `samples/sample_outputs/evidence_manifests/`
- **Added unit tests for MVP stability**
  - Scenario output matches expected fixtures
  - Output formats are stable and contain required fields
  - “No live action executed” safety checks for evidence scaffolding

### Phase 2: read-only Azure Log Analytics integration

**Goal**: Replace mock evidence with read-only queries (still no remediation).

#### Partially complete (Phase 2 scaffolding)

- **Scaffolded Azure configuration and client shape (read-only placeholders)**
  - Environment-variable configuration loader
  - Mock-first client interface with explicit `NotImplementedError` for live calls
- **Drafted KQL query templates**
  - Recent activity changes template
  - Connection failures / heartbeat / high latency indicator templates (placeholders)

#### Remaining (Phase 2)

- **Implement live read-only Azure query execution**
  - Authentication approach (managed identity / developer auth) and secure configuration
  - Execute Log Analytics queries and Activity Log reads (read-only)
- **Normalize live query results to internal models**
  - Map live results into the same shapes used by the scorer
  - Handle missing fields and partial data robustly
- **Add integration tests (still read-only)**
  - Mocked SDK layer tests + contract tests for normalization

### Phase 3: evidence collection

**Goal**: Gather a richer, incident-specific evidence bundle (still read-only).

#### Partially complete (Phase 3 foundations)

- **PowerShell scripts exist as optional, read-only templates**
  - `scripts/powershell/` produces JSON output suitable for incident evidence
  - Documented in `docs/powershell-diagnostics.md`

#### Remaining (Phase 3)

- **Define an evidence checklist by hypothesis (operator-focused)**
  - What confirms/denies each cause, and where to collect it (Azure vs on-prem)
- **Define ingestion/normalization for collected evidence**
  - How PowerShell outputs and other artifacts become internal observations/events
- **Evidence packaging**
  - Bundle manifest + artifacts into a consistent folder layout for ticket attachment/export

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

### Next recommended work (practical sequence)

1. **Make Phase 2 real (read-only)**
   - Implement live Azure authentication and Log Analytics querying as read-only, with mock fallbacks kept intact.
2. **Add normalization contracts**
   - Document and implement a clear mapping from live query rows → internal observations/events used by `scorer.py`.
3. **Operationalize evidence packaging**
   - Standardize where manifests and operator-collected artifacts live and how they’re referenced in reports.

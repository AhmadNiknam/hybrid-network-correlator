## Screenshots (placeholders)

This project will eventually benefit from a small set of screenshots/gifs that show the workflow without requiring a reader to run anything locally.

### What to capture (recommended set)

- **CLI text report (happy path)**:
  - Run: `python -m src.correlator.main --scenario scenario1_nsg_rule_change --format text`
  - Capture a terminal screenshot that includes:
    - incident id + scenario
    - top probable cause and confidence
    - a few evidence lines
    - recommended next checks

- **JSON output (structure overview)**:
  - Run: `python -m src.correlator.main --scenario scenario1_nsg_rule_change --format json`
  - Capture either:
    - a short terminal screenshot, or
    - a cropped view in an editor showing `incidentId`, `rankedCauses`, and `summaryText`

- **Evidence manifest (prepare-only safety)**:
  - If/when a manifest file is produced under `samples/sample_outputs/evidence_manifests/`,
    capture a snippet showing it is a “what to collect next” artifact (not executed automation).

- **PowerShell diagnostics (optional, manual)**:
  - Capture one example of running a script (e.g., `Test-NetworkPath.ps1`) and the resulting JSON saved to disk.

### File naming and placement

When adding real screenshots later:

- Put image assets under `docs/assets/screenshots/`
- Use consistent, descriptive filenames:
  - `cli-text-report-scenario1.png`
  - `json-summary-scenario1.png`
  - `evidence-manifest-example.png`
  - `powershell-networkpath-example.png`

### Redaction checklist (important)

Before committing screenshots, ensure they contain **no sensitive or environment-specific data**:

- Tenant IDs, subscription IDs, resource IDs, public IPs, internal IPs that map to real networks
- Hostnames, usernames, domain names, gateway names tied to real environments
- Tokens, keys, connection strings, query results with customer-identifying data

Prefer showing the repo’s existing sanitized fixtures under `samples/` and generic placeholders like `<subscription-id>`.


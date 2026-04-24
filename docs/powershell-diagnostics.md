# PowerShell diagnostics (Windows / on-prem)

This project intentionally keeps the Python “evidence collection layer” in **prepare-only** mode (it generates operator instructions and action requests, but does not execute live diagnostics). The scripts in `scripts/powershell/` are **safe, read-only templates** that an administrator can run manually on a Windows host when collecting on-prem evidence.

## Safety model (read before running)

- **Read-only**: scripts collect state and test connectivity; they do not change configuration.
- **No admin required by default**: most sections run in standard user context. If a section may require additional privileges or is commonly blocked by policy, the script records an error and includes a warning.
- **Data handling**: outputs may include hostnames, IPs, DNS servers, and interface details. Store results according to your incident data-handling policy.

All scripts default to writing a **single JSON object** to stdout. Use `-OutputPath` to save results to a file.

## Scripts

### `Test-NetworkPath.ps1`

**Use when**
- You need fast evidence of “can this host reach that host/service?” during an incident window.
- You want to compare **DNS vs connectivity** (e.g., resolves but TCP fails, or DNS returns unexpected IPs).

**What it collects**
- DNS resolution (A/AAAA) using the system resolver, or explicit DNS server(s)
- ICMP echo summary (ping) when permitted
- TCP connectivity test when `-Port` is provided
- Optional traceroute-style hop discovery (`-TraceRoute`)

**Run examples (manual)**

```powershell
# TCP service check (JSON to stdout)
.\scripts\powershell\Test-NetworkPath.ps1 -TargetHost "onprem.example.com" -Port 443

# Add traceroute-style evidence and write to a file
.\scripts\powershell\Test-NetworkPath.ps1 -TargetHost "10.10.20.30" -Port 3389 -TraceRoute -OutputPath .\out\networkpath.json

# Use explicit DNS servers (split-horizon troubleshooting)
.\scripts\powershell\Test-NetworkPath.ps1 -TargetHost "onprem.example.com" -DnsServer @("10.0.0.10","10.0.0.11") -Port 443
```

**Notes**
- ICMP and traceroute may be blocked by policy; treat failures as **non-deterministic evidence** rather than proof of outage.

### `Get-DnsDiagnostics.ps1`

**Use when**
- The correlator flags a likely DNS issue, or you suspect split-horizon/conditional forwarders.
- A service works by IP but fails by name, or DNS answers look inconsistent across networks.

**What it collects**
- DNS client global settings (suffix search list, devolution)
- DNS servers per interface
- DNS cache summary (best-effort; may be restricted)
- Optional resolution attempts for `-TargetHost` across selected record types

**Run examples (manual)**

```powershell
# Local DNS config only
.\scripts\powershell\Get-DnsDiagnostics.ps1

# DNS config plus resolution attempts
.\scripts\powershell\Get-DnsDiagnostics.ps1 -TargetHost "onprem.example.com"

# Query using explicit DNS servers and write to file
.\scripts\powershell\Get-DnsDiagnostics.ps1 -TargetHost "onprem.example.com" -DnsServer @("10.0.0.10") -OutputPath .\out\dns.json
```

**Notes**
- Differences between resolvers can be expected in hybrid setups. Always capture *which DNS server(s)* were used.

### `Get-WindowsNetworkSnapshot.ps1`

**Use when**
- You need a point-in-time snapshot of the host’s network state for correlation (routes, adapters, DNS settings).
- You’re collecting evidence for “what changed / what is currently effective” on a Windows endpoint.

**What it collects**
- Host identity and OS details (CIM)
- Adapters and IP configuration (including DNS servers per interface)
- DNS client global settings
- IPv4 route and neighbor samples (bounded to avoid huge output)
- TCP connection state counts (summary)
- Optional firewall profile status (`-IncludeFirewall`, best-effort)

**Run examples (manual)**

```powershell
# Snapshot to stdout
.\scripts\powershell\Get-WindowsNetworkSnapshot.ps1

# Snapshot to a file
.\scripts\powershell\Get-WindowsNetworkSnapshot.ps1 -OutputPath .\out\network-snapshot.json

# Include firewall profile info (read-only; may be restricted)
.\scripts\powershell\Get-WindowsNetworkSnapshot.ps1 -IncludeFirewall -OutputPath .\out\network-snapshot.json
```

## Safety limitations / gotchas

- **Not a replacement for approved tooling**: these are templates meant to produce consistent, JSON-friendly evidence quickly.
- **Policy can block probes**: ping/traceroute are often filtered; TCP tests can be blocked; DNS can be split-horizon.
- **No system changes**: scripts intentionally avoid actions like flushing DNS cache, changing adapters, restarting services, enabling logging, or modifying firewall rules.
- **Partial data is expected**: when a section fails (policy, missing cmdlets, constrained host), the script records an error object for that section rather than stopping evidence capture entirely.


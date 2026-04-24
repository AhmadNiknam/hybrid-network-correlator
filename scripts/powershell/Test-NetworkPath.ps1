<#
.SYNOPSIS
Read-only network path diagnostics for a target host.

.DESCRIPTION
Collects common, safe connectivity evidence from the local Windows host to a target:
- DNS resolution (A/AAAA) using the local resolver (and optional explicit DNS servers)
- ICMP echo (ping) using Test-Connection (when permitted by network policy)
- TCP connectivity using Test-NetConnection (when a Port is provided)
- Optional traceroute-style hop discovery using Test-NetConnection -TraceRoute

Outputs a single JSON-friendly object to stdout by default, and can optionally write the same JSON to an output file.

Safety:
- Read-only: does not modify system settings.
- Does not require administrative privileges for most checks.
- Some networks block ICMP/traceroute; failures may be policy-related, not necessarily an outage.

.PARAMETER TargetHost
The destination host to test (IP address or FQDN).

.PARAMETER Port
Optional TCP port to test with Test-NetConnection (e.g., 443).

.PARAMETER DnsServer
Optional DNS server IP(s) to use for Resolve-DnsName. If omitted, the system resolver is used.

.PARAMETER PingCount
Number of ICMP echo attempts for Test-Connection. Default is 4.

.PARAMETER TimeoutSeconds
Timeout in seconds for ICMP echo attempts. Default is 2.

.PARAMETER TraceRoute
If set, performs a traceroute-style probe using Test-NetConnection -TraceRoute.

.PARAMETER OutputPath
Optional path to write the JSON result (UTF-8). Parent directories will be created if needed.

.PARAMETER AsObject
If set, writes the PowerShell object to the pipeline instead of JSON text.

.EXAMPLE
.\Test-NetworkPath.ps1 -TargetHost "onprem.example.com" -Port 443

.EXAMPLE
.\Test-NetworkPath.ps1 -TargetHost "10.10.20.30" -TraceRoute -OutputPath .\out\networkpath.json

.NOTES
Designed as a safe template for incident evidence collection. No live remediation is performed.
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string] $TargetHost,

    [Parameter(Mandatory = $false)]
    [ValidateRange(1, 65535)]
    [int] $Port,

    [Parameter(Mandatory = $false)]
    [ValidateNotNullOrEmpty()]
    [string[]] $DnsServer,

    [Parameter(Mandatory = $false)]
    [ValidateRange(1, 20)]
    [int] $PingCount = 4,

    [Parameter(Mandatory = $false)]
    [ValidateRange(1, 30)]
    [int] $TimeoutSeconds = 2,

    [Parameter(Mandatory = $false)]
    [switch] $TraceRoute,

    [Parameter(Mandatory = $false)]
    [string] $OutputPath,

    [Parameter(Mandatory = $false)]
    [switch] $AsObject
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function New-ResultEnvelope {
    param(
        [Parameter(Mandatory = $true)]
        [hashtable] $Data,

        [Parameter(Mandatory = $false)]
        [string[]] $Warnings = @()
    )

    $now = (Get-Date).ToUniversalTime().ToString("o")
    return [ordered]@{
        schemaVersion = "1.0"
        script = [ordered]@{
            name = "Test-NetworkPath.ps1"
            generatedAtUtc = $now
        }
        input = [ordered]@{
            targetHost = $TargetHost
            port = $(if ($PSBoundParameters.ContainsKey("Port")) { $Port } else { $null })
            dnsServer = $(if ($DnsServer) { $DnsServer } else { $null })
            traceRoute = [bool]$TraceRoute
        }
        warnings = $Warnings
        data = $Data
    }
}

function Write-Result {
    param(
        [Parameter(Mandatory = $true)]
        $ResultObject
    )

    if ($OutputPath) {
        $parent = Split-Path -Parent $OutputPath
        if ($parent -and -not (Test-Path -LiteralPath $parent)) {
            New-Item -ItemType Directory -Path $parent -Force | Out-Null
        }
    }

    if ($AsObject) {
        if ($OutputPath) {
            ($ResultObject | ConvertTo-Json -Depth 8) | Set-Content -LiteralPath $OutputPath -Encoding UTF8
        }
        $ResultObject
        return
    }

    $json = ($ResultObject | ConvertTo-Json -Depth 8)
    if ($OutputPath) {
        $json | Set-Content -LiteralPath $OutputPath -Encoding UTF8
    }
    $json
}

function Try-Run {
    param(
        [scriptblock] $ScriptBlock
    )
    try {
        return & $ScriptBlock
    } catch {
        return [ordered]@{
            error = $_.Exception.Message
            type = $_.Exception.GetType().FullName
        }
    }
}

$warnings = New-Object System.Collections.Generic.List[string]

$dnsA = Try-Run {
    $args = @{
        Name = $TargetHost
        Type = "A"
        ErrorAction = "Stop"
    }
    if ($DnsServer) { $args["Server"] = $DnsServer }
    Resolve-DnsName @args | ForEach-Object {
        [ordered]@{
            name = $_.Name
            type = $_.Type
            ipAddress = $_.IPAddress
            ttl = $_.TTL
        }
    }
}

$dnsAAAA = Try-Run {
    $args = @{
        Name = $TargetHost
        Type = "AAAA"
        ErrorAction = "Stop"
    }
    if ($DnsServer) { $args["Server"] = $DnsServer }
    Resolve-DnsName @args | ForEach-Object {
        [ordered]@{
            name = $_.Name
            type = $_.Type
            ipAddress = $_.IPAddress
            ttl = $_.TTL
        }
    }
}

$icmp = Try-Run {
    Test-Connection -TargetName $TargetHost -Count $PingCount -TimeoutSeconds $TimeoutSeconds -ErrorAction Stop |
        ForEach-Object {
            [ordered]@{
                address = $_.Address
                responseTimeMs = $_.ResponseTime
                status = $_.Status
            }
        }
}
if ($icmp -is [hashtable] -and $icmp.ContainsKey("error")) {
    $warnings.Add("ICMP ping may be blocked by policy or firewalls; treat ping failures as non-deterministic evidence.")
}

$tcp = $null
if ($PSBoundParameters.ContainsKey("Port")) {
    $tcp = Try-Run {
        $t = Test-NetConnection -ComputerName $TargetHost -Port $Port -InformationLevel Detailed -WarningAction SilentlyContinue
        [ordered]@{
            computerName = $t.ComputerName
            remoteAddress = $t.RemoteAddress
            remotePort = $t.RemotePort
            interfaceAlias = $t.InterfaceAlias
            sourceAddress = $t.SourceAddress
            pingSucceeded = $t.PingSucceeded
            tcpTestSucceeded = $t.TcpTestSucceeded
            latencyMs = $t.PingReplyDetails.RoundtripTime
        }
    }
}

$trace = $null
if ($TraceRoute) {
    $trace = Try-Run {
        $t = Test-NetConnection -ComputerName $TargetHost -TraceRoute -WarningAction SilentlyContinue
        $hops = @()
        foreach ($h in ($t.TraceRoute | Where-Object { $_ })) {
            $hops += [ordered]@{
                hop = $h.Hop
                ipAddress = $h.IPAddress
                responseTimeMs = $h.ResponseTime
            }
        }
        [ordered]@{
            traceRoute = $hops
        }
    }
    $warnings.Add("Traceroute-style probing can be affected by ICMP/time-exceeded filtering; missing hops can be normal.")
}

$data = [ordered]@{
    dns = [ordered]@{
        a = $dnsA
        aaaa = $dnsAAAA
    }
    icmp = $icmp
    tcp = $tcp
    trace = $trace
}

$result = New-ResultEnvelope -Data $data -Warnings $warnings.ToArray()
Write-Result -ResultObject $result


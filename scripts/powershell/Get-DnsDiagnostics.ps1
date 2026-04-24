<#
.SYNOPSIS
Read-only DNS diagnostics for local configuration and a target hostname.

.DESCRIPTION
Collects DNS-relevant evidence from the local Windows host:
- DNS client configuration (suffix search list, DNS servers per interface)
- DNS cache summary (when accessible)
- Resolution attempts for common record types (A/AAAA/CNAME) for a target host

Outputs a single JSON-friendly object to stdout by default, and can optionally write the same JSON to an output file.

Safety:
- Read-only: does not modify DNS settings, cache, or network configuration.
- Does not require administrative privileges for most data collection.

.PARAMETER TargetHost
Optional. The hostname to resolve (FQDN recommended). If omitted, only local DNS configuration is collected.

.PARAMETER DnsServer
Optional DNS server IP(s) to use for Resolve-DnsName. If omitted, the system resolver is used.

.PARAMETER RecordType
Record types to query. Default is A, AAAA, CNAME.

.PARAMETER OutputPath
Optional path to write the JSON result (UTF-8). Parent directories will be created if needed.

.PARAMETER AsObject
If set, writes the PowerShell object to the pipeline instead of JSON text.

.EXAMPLE
.\Get-DnsDiagnostics.ps1 -TargetHost "onprem.example.com"

.EXAMPLE
.\Get-DnsDiagnostics.ps1 -TargetHost "onprem.example.com" -DnsServer @("10.0.0.10","10.0.0.11") -OutputPath .\out\dns.json

.NOTES
DNS failures may be caused by split-horizon DNS, conditional forwarders, or blocked UDP/TCP 53 paths.
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [ValidateNotNullOrEmpty()]
    [string] $TargetHost,

    [Parameter(Mandatory = $false)]
    [ValidateNotNullOrEmpty()]
    [string[]] $DnsServer,

    [Parameter(Mandatory = $false)]
    [ValidateSet("A","AAAA","CNAME","PTR","TXT","SRV","MX")]
    [string[]] $RecordType = @("A","AAAA","CNAME"),

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
            name = "Get-DnsDiagnostics.ps1"
            generatedAtUtc = $now
        }
        input = [ordered]@{
            targetHost = $(if ($TargetHost) { $TargetHost } else { $null })
            dnsServer = $(if ($DnsServer) { $DnsServer } else { $null })
            recordType = $RecordType
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

$dnsClient = Try-Run {
    $global = Get-DnsClientGlobalSetting
    [ordered]@{
        suffixSearchList = @($global.SuffixSearchList)
        useDevolution = [bool]$global.UseDevolution
        devolutionLevel = $global.DevolutionLevel
    }
}

$dnsServers = Try-Run {
    Get-DnsClientServerAddress -AddressFamily IPv4 | ForEach-Object {
        [ordered]@{
            interfaceAlias = $_.InterfaceAlias
            interfaceIndex = $_.InterfaceIndex
            serverAddresses = @($_.ServerAddresses)
        }
    }
}

$cacheSummary = Try-Run {
    $cache = Get-DnsClientCache -ErrorAction Stop
    $sample = @($cache | Select-Object -First 25 | ForEach-Object {
        [ordered]@{
            entry = $_.Entry
            type = $_.Type
            data = $_.Data
            status = $_.Status
            section = $_.Section
            ttl = $_.TimeToLive
        }
    })
    [ordered]@{
        totalEntries = @($cache).Count
        sample = $sample
    }
}
if ($cacheSummary -is [hashtable] -and $cacheSummary.ContainsKey("error")) {
    $warnings.Add("DNS cache enumeration may be unavailable on some systems or constrained by policy.")
}

$resolution = $null
if ($TargetHost) {
    $resolution = @()
    foreach ($rt in $RecordType) {
        $resolution += Try-Run {
            $sw = [System.Diagnostics.Stopwatch]::StartNew()
            $args = @{
                Name = $TargetHost
                Type = $rt
                ErrorAction = "Stop"
            }
            if ($DnsServer) { $args["Server"] = $DnsServer }
            $rows = Resolve-DnsName @args
            $sw.Stop()
            [ordered]@{
                recordType = $rt
                durationMs = [int]$sw.ElapsedMilliseconds
                answers = @(
                    $rows | ForEach-Object {
                        [ordered]@{
                            name = $_.Name
                            type = $_.Type
                            ipAddress = $_.IPAddress
                            nameHost = $_.NameHost
                            ttl = $_.TTL
                            section = $_.Section
                        }
                    }
                )
            }
        }
    }
    $warnings.Add("If resolution differs across networks, consider split-horizon DNS and conditional forwarders.")
}

$data = [ordered]@{
    dnsClientGlobalSetting = $dnsClient
    dnsServersByInterface = $dnsServers
    dnsCache = $cacheSummary
    resolution = $resolution
}

$result = New-ResultEnvelope -Data $data -Warnings $warnings.ToArray()
Write-Result -ResultObject $result


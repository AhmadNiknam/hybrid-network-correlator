<#
.SYNOPSIS
Read-only "snapshot" of Windows network state for troubleshooting.

.DESCRIPTION
Captures a point-in-time view of local Windows networking state that is commonly useful
for incident correlation and evidence collection (Azure VM or on-prem Windows host):
- Host / OS identity
- Network adapters and IP configuration
- DNS client configuration and servers
- Routes and neighbors (ARP/ND)
- Active TCP connections summary
- Optional firewall profile state (read-only; may be restricted by policy)

Outputs a single JSON-friendly object to stdout by default, and can optionally write the same JSON to an output file.

Safety:
- Read-only: does not modify system settings.
- Does not require administrative privileges for most collection.
- Some data may be unavailable under constrained environments; the script records errors per section.

.PARAMETER OutputPath
Optional path to write the JSON result (UTF-8). Parent directories will be created if needed.

.PARAMETER IncludeFirewall
If set, attempts to read firewall profile status with Get-NetFirewallProfile. This is read-only but can be restricted.

.PARAMETER AsObject
If set, writes the PowerShell object to the pipeline instead of JSON text.

.EXAMPLE
.\Get-WindowsNetworkSnapshot.ps1

.EXAMPLE
.\Get-WindowsNetworkSnapshot.ps1 -IncludeFirewall -OutputPath .\out\network-snapshot.json

.NOTES
This script is intentionally "snapshot-only" and avoids event logs by default (event log export is more likely
to require admin privileges and can be noisy for evidence handling).
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [string] $OutputPath,

    [Parameter(Mandatory = $false)]
    [switch] $IncludeFirewall,

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
            name = "Get-WindowsNetworkSnapshot.ps1"
            generatedAtUtc = $now
        }
        input = [ordered]@{
            includeFirewall = [bool]$IncludeFirewall
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
            ($ResultObject | ConvertTo-Json -Depth 10) | Set-Content -LiteralPath $OutputPath -Encoding UTF8
        }
        $ResultObject
        return
    }

    $json = ($ResultObject | ConvertTo-Json -Depth 10)
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

$hostInfo = Try-Run {
    $os = Get-CimInstance -ClassName Win32_OperatingSystem
    $cs = Get-CimInstance -ClassName Win32_ComputerSystem
    [ordered]@{
        computerName = $env:COMPUTERNAME
        domain = $cs.Domain
        manufacturer = $cs.Manufacturer
        model = $cs.Model
        osCaption = $os.Caption
        osVersion = $os.Version
        buildNumber = $os.BuildNumber
        installDateUtc = ($os.InstallDate).ToUniversalTime().ToString("o")
        lastBootUpTimeUtc = ($os.LastBootUpTime).ToUniversalTime().ToString("o")
    }
}

$adapters = Try-Run {
    Get-NetAdapter | Sort-Object -Property InterfaceIndex | ForEach-Object {
        [ordered]@{
            name = $_.Name
            interfaceDescription = $_.InterfaceDescription
            interfaceIndex = $_.InterfaceIndex
            macAddress = $_.MacAddress
            status = $_.Status.ToString()
            linkSpeed = $_.LinkSpeed
        }
    }
}

$ipConfig = Try-Run {
    Get-NetIPConfiguration | Sort-Object -Property InterfaceIndex | ForEach-Object {
        [ordered]@{
            interfaceAlias = $_.InterfaceAlias
            interfaceIndex = $_.InterfaceIndex
            ipv4Address = @($_.IPv4Address | ForEach-Object { $_.IPAddress })
            ipv6Address = @($_.IPv6Address | ForEach-Object { $_.IPAddress })
            ipv4DefaultGateway = @($_.IPv4DefaultGateway | ForEach-Object { $_.NextHop })
            ipv6DefaultGateway = @($_.IPv6DefaultGateway | ForEach-Object { $_.NextHop })
            dnsServer = @($_.DnsServer.ServerAddresses)
            dnsSuffix = $_.DnsSuffix
            netProfile = $(if ($_.NetProfile) { $_.NetProfile.Name } else { $null })
        }
    }
}

$dnsClient = Try-Run {
    $global = Get-DnsClientGlobalSetting
    [ordered]@{
        suffixSearchList = @($global.SuffixSearchList)
        useDevolution = [bool]$global.UseDevolution
        devolutionLevel = $global.DevolutionLevel
    }
}

$routes = Try-Run {
    Get-NetRoute -AddressFamily IPv4 | Sort-Object -Property RouteMetric, DestinationPrefix | Select-Object -First 300 | ForEach-Object {
        [ordered]@{
            destinationPrefix = $_.DestinationPrefix
            nextHop = $_.NextHop
            interfaceIndex = $_.InterfaceIndex
            interfaceAlias = $_.InterfaceAlias
            routeMetric = $_.RouteMetric
            protocol = $_.Protocol.ToString()
            publish = $_.Publish.ToString()
            store = $_.Store.ToString()
        }
    }
}

$neighbors = Try-Run {
    Get-NetNeighbor -AddressFamily IPv4 | Sort-Object -Property InterfaceIndex, IPAddress | Select-Object -First 300 | ForEach-Object {
        [ordered]@{
            interfaceIndex = $_.InterfaceIndex
            interfaceAlias = $_.InterfaceAlias
            ipAddress = $_.IPAddress
            linkLayerAddress = $_.LinkLayerAddress
            state = $_.State.ToString()
        }
    }
}

$tcpConnections = Try-Run {
    Get-NetTCPConnection | Group-Object -Property State | ForEach-Object {
        [ordered]@{
            state = $_.Name
            count = $_.Count
        }
    }
}

$firewall = $null
if ($IncludeFirewall) {
    $firewall = Try-Run {
        Get-NetFirewallProfile | Sort-Object -Property Name | ForEach-Object {
            [ordered]@{
                name = $_.Name
                enabled = [bool]$_.Enabled
                defaultInboundAction = $_.DefaultInboundAction.ToString()
                defaultOutboundAction = $_.DefaultOutboundAction.ToString()
                logAllowed = [bool]$_.LogAllowed
                logBlocked = [bool]$_.LogBlocked
                logFileName = $_.LogFileName
            }
        }
    }
    if ($firewall -is [hashtable] -and $firewall.ContainsKey("error")) {
        $warnings.Add("Firewall profile enumeration may be restricted; rerun with appropriate privileges if required by your environment.")
    }
}

$data = [ordered]@{
    host = $hostInfo
    adapters = $adapters
    ipConfiguration = $ipConfig
    dnsClientGlobalSetting = $dnsClient
    routesIpv4Sample = $routes
    neighborsIpv4Sample = $neighbors
    tcpConnectionStateCounts = $tcpConnections
    firewallProfiles = $firewall
}

$result = New-ResultEnvelope -Data $data -Warnings $warnings.ToArray()
Write-Result -ResultObject $result


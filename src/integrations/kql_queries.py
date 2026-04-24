from __future__ import annotations


def _minutes(value: int) -> int:
    try:
        value_int = int(value)
    except (TypeError, ValueError) as e:
        raise ValueError("minutes must be an integer") from e
    if value_int <= 0:
        raise ValueError("minutes must be > 0")
    return value_int


def _ms(value: int) -> int:
    try:
        value_int = int(value)
    except (TypeError, ValueError) as e:
        raise ValueError("threshold_ms must be an integer") from e
    if value_int <= 0:
        raise ValueError("threshold_ms must be > 0")
    return value_int


def recent_activity_changes_last_minutes(minutes: int) -> str:
    """
    Template for Azure Activity Log "recent changes" view.
    This is a placeholder that can later be tightened to specific providers/resources.
    """
    minutes = _minutes(minutes)
    return f"""
AzureActivity
| where TimeGenerated >= ago({minutes}m)
| where CategoryValue in ("Administrative", "Policy", "Security")
| project TimeGenerated, CategoryValue, OperationNameValue, ActivityStatusValue, Caller, ResourceGroup, ResourceProviderValue, ResourceId, CorrelationId
| order by TimeGenerated desc
""".strip()


def connection_failures_last_minutes(minutes: int) -> str:
    """
    Generic template for connection failures (NSG flow logs / diagnostics / custom logs).
    Uses a hypothetical table name as scaffolding.
    """
    minutes = _minutes(minutes)
    return f"""
NetworkDiagnostics
| where TimeGenerated >= ago({minutes}m)
| where ResultType in ("Failure", "Deny", "Timeout")
| project TimeGenerated, SourceIp, SourcePort, DestIp, DestPort, Protocol, ResultType, Reason, ResourceId
| order by TimeGenerated desc
""".strip()


def heartbeat_missing_last_minutes(minutes: int) -> str:
    """
    Heartbeat missing indicator (commonly from Log Analytics Heartbeat table).
    """
    minutes = _minutes(minutes)
    return f"""
Heartbeat
| summarize LastSeen=max(TimeGenerated) by Computer
| where LastSeen < ago({minutes}m)
| project Computer, LastSeen
| order by LastSeen asc
""".strip()


def high_latency_indicators_last_minutes(minutes: int, *, threshold_ms: int = 200) -> str:
    """
    High latency indicator template based on hypothetical telemetry.
    """
    minutes = _minutes(minutes)
    threshold_ms = _ms(threshold_ms)
    return f"""
NetworkTelemetry
| where TimeGenerated >= ago({minutes}m)
| where LatencyMs >= {threshold_ms}
| summarize AvgLatencyMs=avg(LatencyMs), P95LatencyMs=percentile(LatencyMs, 95), Count=count() by Source, Destination
| order by P95LatencyMs desc
""".strip()


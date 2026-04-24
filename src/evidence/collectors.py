from __future__ import annotations

from typing import Any, Dict, Optional


def prepare_packet_capture_request(
    *,
    target: str,
    duration_seconds: int = 120,
    filter_expression: Optional[str] = None,
    max_size_mb: int = 200,
) -> Dict[str, Any]:
    """
    Prepare a packet capture request object.

    Safety: this function does NOT start capture or call any APIs.
    """
    if duration_seconds <= 0:
        raise ValueError("duration_seconds must be > 0")
    if max_size_mb <= 0:
        raise ValueError("max_size_mb must be > 0")

    return {
        "actionType": "PACKET_CAPTURE",
        "target": target,
        "parameters": {
            "durationSeconds": duration_seconds,
            "filter": filter_expression,
            "maxSizeMb": max_size_mb,
        },
        "execution": {
            "mode": "PREPARE_ONLY",
            "liveActionsExecuted": False,
        },
        "operatorInstructions": [
            "If approved, run a packet capture using your standard tooling (e.g., Netsh, Wireshark, or agent-based capture).",
            "Ensure you have authorization and follow data handling policies before capturing traffic.",
        ],
    }


def prepare_windows_diagnostics_script_request(
    *,
    target_host: str,
    script_name: str = "Collect-NetworkDiagnostics.ps1",
    include_event_logs: bool = True,
) -> Dict[str, Any]:
    """
    Prepare a Windows diagnostics script request object.

    Safety: this function does NOT execute PowerShell or generate runnable code.
    """
    return {
        "actionType": "WINDOWS_DIAGNOSTICS_SCRIPT",
        "target": target_host,
        "parameters": {
            "scriptName": script_name,
            "includeEventLogs": bool(include_event_logs),
        },
        "execution": {
            "mode": "PREPARE_ONLY",
            "liveActionsExecuted": False,
        },
        "operatorInstructions": [
            "If approved, execute your vetted diagnostics collection script on the target host.",
            "Run with least privilege required; avoid collecting more data than necessary.",
        ],
    }


def prepare_connectivity_test_request(
    *,
    source: str,
    destination: str,
    protocol: str = "tcp",
    port: Optional[int] = None,
    attempts: int = 3,
    timeout_seconds: int = 3,
) -> Dict[str, Any]:
    """
    Prepare a connectivity test request object.

    Safety: this function does NOT perform any live network probing.
    """
    if attempts <= 0:
        raise ValueError("attempts must be > 0")
    if timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be > 0")

    protocol_s = str(protocol).lower().strip()
    if protocol_s not in {"tcp", "udp", "icmp"}:
        raise ValueError("protocol must be one of: tcp, udp, icmp")
    if protocol_s in {"tcp", "udp"} and port is None:
        raise ValueError("port is required for tcp/udp")

    return {
        "actionType": "CONNECTIVITY_TEST",
        "source": source,
        "target": destination,
        "parameters": {
            "protocol": protocol_s,
            "port": port,
            "attempts": attempts,
            "timeoutSeconds": timeout_seconds,
        },
        "execution": {
            "mode": "PREPARE_ONLY",
            "liveActionsExecuted": False,
        },
        "operatorInstructions": [
            "If approved, run a connectivity test from the source to the destination (e.g., Test-NetConnection, ping, traceroute).",
            "Capture timestamps and results for correlation with the incident window.",
        ],
    }


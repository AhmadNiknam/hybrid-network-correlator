from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Tuple

from .models import (
    ActivityLog,
    AlertPayload,
    ProbableCause,
    RankedCause,
    TelemetryBundle,
)


def _parse_ts(ts: str) -> datetime:
    # Fixtures use ISO 8601 with Z suffix.
    if ts.endswith("Z"):
        ts = ts[:-1] + "+00:00"
    return datetime.fromisoformat(ts).astimezone(timezone.utc)


def _in_window(ts: str, start: str, end: str) -> bool:
    t = _parse_ts(ts)
    return _parse_ts(start) <= t <= _parse_ts(end)


@dataclass
class CauseAccumulator:
    score: int = 0
    support: List[str] = field(default_factory=list)
    against: List[str] = field(default_factory=list)
    next_checks: List[str] = field(default_factory=list)

    def add(self, points: int, support: str | None = None) -> None:
        self.score += points
        if support:
            self.support.append(support)

    def add_against(self, points: int, evidence: str) -> None:
        # points should typically be <= 0 for "against"; allow 0 if caller
        # wants to add counter-evidence without penalizing score.
        self.score += points
        self.against.append(evidence)


MAX_SCORES: Dict[ProbableCause, int] = {
    ProbableCause.NSG_CHANGE: 10,
    ProbableCause.ROUTE_UDR_CHANGE: 10,
    ProbableCause.VPN_GATEWAY_ISSUE: 10,
    ProbableCause.DNS_ISSUE: 10,
    ProbableCause.UNKNOWN: 10,
}


def _confidence(cause: ProbableCause, score: int) -> float:
    max_score = MAX_SCORES.get(cause, 10)
    if score <= 0:
        return 0.0
    return min(1.0, round(score / max_score, 2))


def score_probable_causes(
    alert: AlertPayload, activity: ActivityLog, telemetry: TelemetryBundle
) -> List[RankedCause]:
    acc: Dict[ProbableCause, CauseAccumulator] = {c: CauseAccumulator() for c in ProbableCause}

    tw_start = alert.timeWindow.start
    tw_end = alert.timeWindow.end

    # --- Symptoms: weak priors ---
    symptoms = set(s.lower() for s in (alert.symptoms or []))
    is_unreachable = "unreachable" in symptoms or "tcp_connect_failed" in symptoms
    is_intermittent = "intermittent" in symptoms or "packet_loss" in symptoms
    is_latency = "latency_spike" in symptoms

    if is_unreachable:
        acc[ProbableCause.NSG_CHANGE].add(1, "Symptom suggests hard block/unreachable, consistent with policy block (NSG/ACL)")
        acc[ProbableCause.ROUTE_UDR_CHANGE].add(0, "Symptom could be caused by routing blackhole/misroute (UDR/route)")
        acc[ProbableCause.VPN_GATEWAY_ISSUE].add(1, "Connectivity is failing, gateway issues are a possible contributor")
    if is_intermittent:
        acc[ProbableCause.VPN_GATEWAY_ISSUE].add(2, "Intermittent/packet loss symptoms are consistent with tunnel instability")
    if is_latency:
        acc[ProbableCause.ROUTE_UDR_CHANGE].add(0, "Latency spikes can be caused by routing changes (path length/appliance)")
        acc[ProbableCause.VPN_GATEWAY_ISSUE].add(0, "Latency/jitter can be caused by gateway/tunnel performance issues")

    # If endpoint is an FQDN, DNS is at least plausible.
    if "." in (alert.onPremEndpoint.ipOrFqdn or "") and not _looks_like_ipv4(alert.onPremEndpoint.ipOrFqdn):
        acc[ProbableCause.DNS_ISSUE].add(1, "Endpoint is an FQDN; DNS issues can sometimes cause intermittent failures")

    # --- Activity log: strong indicators if within window ---
    for ev in activity.events:
        if not _in_window(ev.timestamp, tw_start, tw_end):
            continue
        op = ev.operationName.lower()
        if "networksecuritygroups" in op and "securityrules" in op:
            acc[ProbableCause.NSG_CHANGE].add(
                5, f"Activity change near incident window: {ev.eventId} NSG securityRules/write"
            )
            _ensure_next_checks(
                acc[ProbableCause.NSG_CHANGE],
                [
                    "Review effective NSG rules on the VM NIC/subnet for the destination/port",
                    "Confirm the recent NSG rule change was intended; revert/adjust priority if not",
                ],
            )
        if "routetables" in op and "/routes/" in op or "routetables/routes" in op:
            acc[ProbableCause.ROUTE_UDR_CHANGE].add(
                5, f"Activity change near incident window: {ev.eventId} routeTables/routes/write"
            )
            _ensure_next_checks(
                acc[ProbableCause.ROUTE_UDR_CHANGE],
                [
                    "Review effective routes on the VM NIC for the on-prem destination",
                    "Validate next hop (appliance/gateway) health and routing; revert UDR if unintended",
                ],
            )
        if "virtualnetworkgateways" in op:
            acc[ProbableCause.VPN_GATEWAY_ISSUE].add(
                2, f"Gateway change near incident window: {ev.eventId} virtualNetworkGateways/write"
            )

    # --- Telemetry observations: strongest evidence ---
    for ob in telemetry.observations:
        if not _in_window(ob.timestamp, tw_start, tw_end):
            continue

        ob_type = (ob.type or "").lower()
        ob_result = (ob.result or "").lower()
        details = ob.details or ""

        if ob_type == "connectivity_probe":
            target = ob.target or ""
            if ob_result in {"fail", "failed"}:
                acc[ProbableCause.NSG_CHANGE].add(0, f"Connectivity probe failed to {target}: {ob.observationId}")
                acc[ProbableCause.ROUTE_UDR_CHANGE].add(0, f"Connectivity probe failed to {target}: {ob.observationId}")
                acc[ProbableCause.VPN_GATEWAY_ISSUE].add(0, f"Connectivity probe failed to {target}: {ob.observationId}")
            elif ob_result in {"degraded", "slow"}:
                acc[ProbableCause.ROUTE_UDR_CHANGE].add(0, f"Connectivity probe degraded to {target}: {ob.observationId}")
                acc[ProbableCause.VPN_GATEWAY_ISSUE].add(1, f"Connectivity probe degraded to {target}: {ob.observationId}")

        if ob_type == "nsg_effective_flow":
            if ob_result == "blocked":
                acc[ProbableCause.NSG_CHANGE].add(
                    3,
                    f"Telemetry indicates NSG blocking flow: {ob.observationId} blocked ({details})",
                )
            if ob_result == "allowed":
                acc[ProbableCause.NSG_CHANGE].add_against(
                    -3, f"Telemetry indicates NSG allows flow: {ob.observationId} allowed ({details})"
                )

        if ob_type == "effective_route":
            if ob_result == "changed":
                acc[ProbableCause.ROUTE_UDR_CHANGE].add(
                    3,
                    f"Telemetry indicates effective route changed: {ob.observationId} changed ({details})",
                )

        if ob_type == "vpn_tunnel_health":
            if ob_result == "degraded":
                acc[ProbableCause.VPN_GATEWAY_ISSUE].add(
                    5, f"VPN tunnel health degraded: {ob.observationId} degraded ({details})"
                )
                _ensure_next_checks(
                    acc[ProbableCause.VPN_GATEWAY_ISSUE],
                    [
                        "Check VPN gateway/tunnel diagnostics for drops, BGP issues, and packet loss during the incident window",
                        "Validate on-prem VPN device status and ISP stability for the same time window",
                    ],
                )
            elif ob_result == "healthy":
                acc[ProbableCause.VPN_GATEWAY_ISSUE].add_against(
                    0, f"VPN tunnel health looks healthy: {ob.observationId}"
                )

        if ob_type == "dns_resolution":
            if ob_result in {"fail", "failed"}:
                q = ob.query or ""
                acc[ProbableCause.DNS_ISSUE].add(5, f"DNS resolution failed for {q}: {ob.observationId} ({details})")
                _ensure_next_checks(
                    acc[ProbableCause.DNS_ISSUE],
                    [
                        "Verify DNS server health and conditional forwarders for the queried zone",
                        "Confirm the endpoint resolves consistently from the VM subnet (split-horizon considerations)",
                    ],
                )
            elif ob_result == "ok":
                acc[ProbableCause.DNS_ISSUE].add_against(0, f"DNS resolution succeeded: {ob.observationId}")

    # --- Unknown ---
    # If everything is weak/empty, we keep UNKNOWN as fallback with neutral explanation.
    # We'll finalize UNKNOWN later based on whether strong evidence exists elsewhere.

    ranked = _finalize_ranked(acc)
    return ranked[:3]


def _finalize_ranked(acc: Dict[ProbableCause, CauseAccumulator]) -> List[RankedCause]:
    # Determine if any strong evidence exists (score >= 5)
    strong_any = any(a.score >= 5 for c, a in acc.items() if c != ProbableCause.UNKNOWN)

    if strong_any:
        acc[ProbableCause.UNKNOWN].against.append("Strong, specific evidence points to a different cause")
        acc[ProbableCause.UNKNOWN].next_checks = [
            "Collect additional evidence if the issue does not align with the top hypotheses"
        ]
        acc[ProbableCause.UNKNOWN].score = max(0, acc[ProbableCause.UNKNOWN].score)
    else:
        acc[ProbableCause.UNKNOWN].support.append("Insufficient specific evidence for NSG/UDR/VPN/DNS; treating as unknown")
        acc[ProbableCause.UNKNOWN].next_checks = [
            "Collect NSG effective rules, effective routes, VPN tunnel health, and DNS resolution evidence"
        ]
        acc[ProbableCause.UNKNOWN].score = max(acc[ProbableCause.UNKNOWN].score, 2)

    ranked: List[RankedCause] = []
    for cause, a in acc.items():
        ranked.append(
            RankedCause(
                cause=cause,
                score=int(a.score),
                confidence=_confidence(cause, int(a.score)),
                evidenceSupport=list(a.support),
                evidenceAgainst=list(a.against),
                nextChecks=list(a.next_checks),
            )
        )

    ranked.sort(key=lambda rc: (rc.score, rc.cause.value), reverse=True)
    return ranked


def _ensure_next_checks(acc: CauseAccumulator, checks: List[str]) -> None:
    seen = set(acc.next_checks)
    for c in checks:
        if c not in seen:
            acc.next_checks.append(c)
            seen.add(c)


def _looks_like_ipv4(value: str) -> bool:
    parts = value.split(".")
    if len(parts) != 4:
        return False
    try:
        return all(0 <= int(p) <= 255 for p in parts)
    except ValueError:
        return False


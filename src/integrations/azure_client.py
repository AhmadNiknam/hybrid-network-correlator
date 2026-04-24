from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .config import AzureConfig, load_azure_config


@dataclass(frozen=True, slots=True)
class AzureQueryResult:
    """
    Minimal, SDK-agnostic return shape for Log Analytics queries.
    """

    query: str
    rows: list[dict[str, Any]]
    source: str  # "mock" or "live"


class AzureClient:
    """
    Phase 2 read-only scaffolding client.

    Design constraints / guardrails:
    - No write operations (create/update/patch/put/post/delete) against Azure resources.
    - No resource modification or deletion.
    - No packet capture execution or diagnostic command execution.

    Behavior:
    - If LIVE_AZURE_ENABLED=false (default): always safe, simulated responses (optionally overridden by provided mocks).
    - If LIVE_AZURE_ENABLED=true: still read-only, but live SDK/API execution is not implemented yet in this MVP.
    """

    def __init__(
        self,
        config: AzureConfig | None = None,
        *,
        mock_log_analytics: dict[str, list[dict[str, Any]]] | None = None,
        mock_activity_logs: list[dict[str, Any]] | None = None,
    ) -> None:
        self._config = config or load_azure_config(strict=False)
        self._mock_log_analytics = mock_log_analytics or {}
        self._mock_activity_logs = mock_activity_logs

    @property
    def config(self) -> AzureConfig:
        return self._config

    @property
    def live_enabled(self) -> bool:
        return bool(self._config.live_azure_enabled)

    def _require_live_ready(self) -> None:
        if not self.live_enabled:
            return
        if not self._config.is_configured:
            raise ValueError(
                "LIVE_AZURE_ENABLED=true but required Azure environment variables are missing. "
                "See .env.example for required variables."
            )

    def authenticate(self) -> None:
        """
        Placeholder for future auth.

        Future implementation options:
        - DefaultAzureCredential (managed identity / dev auth)
        - ClientSecretCredential (env vars) if needed
        """
        if not self.live_enabled:
            # Mock mode: do nothing.
            return
        self._require_live_ready()
        raise NotImplementedError("Live read-only Azure authentication is not implemented yet.")

    def query_log_analytics(self, *, workspace_id: str | None = None, query: str) -> AzureQueryResult:
        """
        Read-only Log Analytics query.

        If mock_log_analytics contains an entry for the query string, returns it.
        Otherwise raises until live integration is implemented.
        """
        if query in self._mock_log_analytics:
            return AzureQueryResult(query=query, rows=self._mock_log_analytics[query], source="mock")

        if not self.live_enabled:
            # Safe simulated response for offline MVP operation.
            return AzureQueryResult(query=query, rows=[], source="mock")

        self._require_live_ready()

        _ = workspace_id or self._config.log_analytics_workspace_id
        raise NotImplementedError("Live read-only integration not implemented yet.")

    def get_activity_logs(self, *, minutes: int = 60) -> list[dict[str, Any]]:
        """
        Read-only Activity Logs fetch.

        If mock_activity_logs is provided, returns it.
        Otherwise raises until live integration is implemented.
        """
        if self._mock_activity_logs is not None:
            return list(self._mock_activity_logs)

        if not self.live_enabled:
            # Safe simulated response for offline MVP operation.
            return []

        self._require_live_ready()

        _ = minutes
        raise NotImplementedError("Live read-only integration not implemented yet.")


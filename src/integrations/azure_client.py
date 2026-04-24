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

    - No Azure SDK dependency yet.
    - No authentication performed yet (placeholder only).
    - Supports mock-first execution by returning provided mock responses.
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

    def authenticate(self) -> None:
        """
        Placeholder for future auth.

        Future implementation options:
        - DefaultAzureCredential (managed identity / dev auth)
        - ClientSecretCredential (env vars) if needed
        """
        if not self._config.is_configured:
            # In mock mode, do nothing.
            return
        # Live authentication intentionally not implemented in scaffolding.
        raise NotImplementedError("Live Azure authentication is not implemented (Phase 2 scaffolding).")

    def query_log_analytics(self, *, workspace_id: str | None = None, query: str) -> AzureQueryResult:
        """
        Read-only Log Analytics query.

        If mock_log_analytics contains an entry for the query string, returns it.
        Otherwise raises until live integration is implemented.
        """
        if query in self._mock_log_analytics:
            return AzureQueryResult(query=query, rows=self._mock_log_analytics[query], source="mock")

        if not self._config.is_configured:
            raise RuntimeError(
                "Azure config not set and no mock response provided for this query."
            )

        _ = workspace_id or self._config.log_analytics_workspace_id
        raise NotImplementedError("Live Log Analytics queries are not implemented (Phase 2 scaffolding).")

    def get_activity_logs(self, *, minutes: int = 60) -> list[dict[str, Any]]:
        """
        Read-only Activity Logs fetch.

        If mock_activity_logs is provided, returns it.
        Otherwise raises until live integration is implemented.
        """
        if self._mock_activity_logs is not None:
            return list(self._mock_activity_logs)

        if not self._config.is_configured:
            raise RuntimeError("Azure config not set and no mock activity logs provided.")

        _ = minutes
        raise NotImplementedError("Live Activity Logs are not implemented (Phase 2 scaffolding).")

